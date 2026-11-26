"""Turn the raw benchmark logs into results.json, Markdown tables and the SVG chart.

Usage: python3 w2bench_report.py RUN_DIR OUT_JSON OUT_TABLES_MD OUT_SVG
RUN_DIR holds mols/, meta.txt, *.jsonl and prof/*.folded from the test host.
"""

import collections
import glob
import json
import os
import re
import statistics
import sys

METHOD = {"gfn2": "GFN2-xTB", "gxtb": "g-xTB", "gfnff": "GFN-FF"}
MINIMIZER = {"gfn2": "GFN2-xTB", "gfnff": "GFN-FF"}


def molecule_info(mols):
    info = {}
    for path in glob.glob(os.path.join(mols, "*.xyz")):
        name = os.path.basename(path)[:-4]
        lines = open(path).read().splitlines()
        symbols = [line.split()[0] for line in lines[2 : 2 + int(lines[0])]]
        counts = collections.Counter(symbols)
        order = (["C", "H"] if "C" in counts else []) + sorted(s for s in counts if s not in ("C", "H") or "C" not in counts)
        formula = "".join(s + (str(counts[s]) if counts[s] > 1 else "") for s in order)
        info[name] = {"atoms": len(symbols), "formula": formula}
    return info


def load(path):
    return [json.loads(line) for line in open(path)] if os.path.exists(path) else []


def error_of(row):
    if row.get("exit") == 0:
        return None
    text = (row.get("stderr") or "").strip().splitlines()
    return text[-1] if text else f"exit {row.get('exit')}"


def calc_record(row, info):
    mol = info[row["mol"]]
    rec = {
        "set": row["set"],
        "molecule": row["mol"],
        "atoms": mol["atoms"],
        "formula": mol["formula"],
        "method": METHOD[row["method"]],
        "task": row["task"],
        "threads": row["threads"],
        "repeat": row["rep"] + 1,
        "wall_s": round(row["wall_s"], 4),
        "compute_s": row.get("reported_s"),
        "scf_iterations": row.get("scf_iterations"),
        "opt_steps": row.get("steps"),
        "converged": row.get("converged"),
        "peak_mem_mb": round(row["peak_rss_mb"], 1),
        "cpu_s": None if row.get("cpu_user_s") is None else round(row["cpu_user_s"] + row["cpu_sys_s"], 2),
        "extra_args": row.get("extra", []),
        "electronic_temperature_k": row.get("etemp_k"),
        "gap_ev": row.get("gap_ev"),
        "load_before": [round(x, 2) for x in row["load_before"]],
        "busy_before_pct": row.get("busy_before_pct"),
        "energy_hartree": row.get("energy"),
    }
    if (err := error_of(row)) is not None:
        rec["error"] = err
    elif row["task"] == "optimize" and row.get("converged") is not True:
        rec["error"] = f"optimization not converged after {row.get('steps')} steps"
    return rec


def overhead_record(row, info):
    mol = info[row["mol"]]
    return {"set": "overhead", "molecule": row["mol"], "atoms": mol["atoms"], "formula": mol["formula"],
            "method": METHOD[row["method"]], "task": "energy", "threads": 1, "repeat": row["rep"] + 1,
            "wall_s": round(row["total_s"], 5),
            **{k: round(row[k], 5) for k in ("spawn_s", "hello_s", "open_s", "compute_s", "engine_compute_s", "close_exit_s")},
            "load_before": [round(x, 2) for x in row["load_before"]]}


def conformer_record(row, info, probes):
    mol = info[row["mol"]]
    args = row["args"]
    starts = int(args[args.index("--starts") + 1]) if "--starts" in args else 100
    minimizer = MINIMIZER.get(args[args.index("--minimizer") + 1], "MMFF94s") if "--minimizer" in args else "MMFF94s"
    rec = {
        "set": "conformers",
        "molecule": row["mol"],
        "atoms": mol["atoms"],
        "formula": mol["formula"],
        "method": minimizer,
        "rerank_method": "GFN2-xTB",
        "task": "conformers",
        "threads": 8,
        "repeat": row["rep"] + 1,
        "wall_s": round(row["wall_s"], 3),
        "starts": starts,
        "load_before": [round(x, 2) for x in row["load_before"]],
        "busy_before_pct": row.get("busy_before_pct"),
    }
    report = row.get("report")
    if report is None:
        rec["error"] = error_of(row) or "no report"
        return rec
    ph = report["phases"]
    embed = statistics.median(probes[(row["mol"], starts)]) if minimizer == "MMFF94s" and probes.get((row["mol"], starts)) else None
    sampling = report["sampling_seconds"]
    rec.update(
        search_s=round(report["search_seconds"], 3),
        model_s=round(report["model_seconds"], 3),
        sampling_s=round(sampling, 3),
        embed_s=None if embed is None else round(embed, 3),
        mmff_s=None if embed is None else round(sampling - embed, 3),
        minimize_xtb_s=None if report["minimizing_seconds"] is None else round(report["minimizing_seconds"], 3),
        cluster_s=round((ph["first_reranking"] or ph["done"]) - ph["clustering"], 4),
        rerank_s=None if ph["first_reranking"] is None else round(ph["last_reranking"] - ph["first_reranking"], 3),
        rank_s=None if ph["last_reranking"] is None else round(ph["done"] - ph["last_reranking"], 4),
        valid_starts=report["starts"],
        clusters=report["clusters"],
        reranked=report["reranked"],
        kept=report["kept"],
        notes=report["notes"],
        best_energy_hartree=report["best_energy_hartree"],
        file_kb=round(report["file_bytes_with_result"] / 1024, 1),
        file_kb_model_only=round(report["file_bytes_model_only"] / 1024, 1),
    )
    return rec


# Profile categories, checked on each sample's frames innermost first; the first frame that
# matches any rule decides (rules in this order within a frame). Names come from xctrace,
# partly demangled, so the patterns match both forms.
CATEGORIES = [
    ("diagonalization", re.compile(r"tridiag|evd|eigen|GenEigSolver|sygst|diagonaliz|cholesky", re.I)),
    ("integrals", re.compile(r"integrals|overlap|multipole_moments|cgto", re.I)),
    ("electrostatics", re.compile(r"coulomb|electrostat|isotropic|aes|eeq|third_order|gamma", re.I)),
    ("exchange (g-xTB)", re.compile(r"(?<!compare_)exchange", re.I)),
    ("Hamiltonian / Fock build, density, populations", re.compile(r"h0|fock|hamiltonian|potential|density|weighted_outer|mulliken|population|moments", re.I)),
    ("dispersion", re.compile(r"dispersion|d4|dftd", re.I)),
    ("repulsion", re.compile(r"repulsion", re.I)),
    ("Hessian: response (CPSCF) and derivative terms", re.compile(r"response|hessian|cpscf", re.I)),
]
ENGINE = re.compile(r"axtb|faer|rayon|pulp|xtb_worker")
IDLE = re.compile(r"swtch_pri|psynch|sched_yield|semaphore_wait", re.I)


def profile_shares(path):
    totals = collections.Counter()
    total = 0
    for line in open(path):
        stack, count = line.rsplit(" ", 1)
        count = int(count)
        frames = stack.split(";")
        total += count
        if not any(ENGINE.search(f) for f in frames):
            totals["process start, CLI and I/O (no engine frame)"] += count
            continue
        hit = None
        for frame in reversed(frames):
            hit = next((name for name, rx in CATEGORIES if rx.search(frame)), None)
            if hit:
                break
        if hit is None:
            if IDLE.search(frames[-1]):
                hit = "idle worker threads (yield/wait)"
            elif not any("axtb" in f for f in frames):
                hit = "matrix multiply on pool threads (faer GEMM; caller not on the stack)"
            else:
                hit = "other engine code"
        totals[hit] += count
    return total, {k: round(v / total, 4) for k, v in totals.most_common()} if total else {}


def med(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def spread(values):
    values = [v for v in values if v is not None]
    return (min(values), max(values)) if values else (None, None)


def fmt_s(x):
    if x is None:
        return "–"
    if x < 1:
        return f"{x * 1000:.0f} ms"
    if x < 100:
        return f"{x:.1f} s"
    return f"{x:.0f} s"


def tables(runs, info):
    out = []
    groups = collections.defaultdict(list)
    for r in runs:
        if r["set"] == "methods":
            groups[(r["molecule"], r["method"], r["task"])].append(r)
    mols = sorted({k[0] for k in groups}, key=lambda m: info[m]["atoms"])
    for task, title in (("energy", "Single point"), ("optimize", "Optimization"), ("hessian", "Frequencies (Hessian)")):
        out.append(f"\n### {title}\n")
        if task == "optimize":
            out.append("| Molecule | Atoms | GFN2-xTB | steps | g-xTB | steps | GFN-FF | steps | g-xTB / GFN2 |")
            out.append("| --- | --: | --: | --: | --: | --: | --: | --: | --: |")
        else:
            out.append("| Molecule | Atoms | GFN2-xTB | SCF it. | g-xTB | SCF it. | GFN-FF | g-xTB / GFN2 | Peak memory (g-xTB) |")
            out.append("| --- | --: | --: | --: | --: | --: | --: | --: | --: |")
        for m in mols:
            cells = [m, str(info[m]["atoms"])]
            med_by = {}
            for meth in ("GFN2-xTB", "g-xTB", "GFN-FF"):
                rows = groups.get((m, meth, task), [])
                ok = [r for r in rows if "error" not in r]
                if not ok:
                    cells.append("not supported" if rows else "–")
                    if task == "optimize" or meth != "GFN-FF":
                        cells.append("")
                    continue
                walls = [r["wall_s"] for r in ok]
                lo, hi = spread(walls)
                med_by[meth] = med(walls)
                cell = fmt_s(med(walls)) + (f" ({fmt_s(lo)}–{fmt_s(hi)})" if len(ok) > 1 and hi - lo > 0.1 * med(walls) else "")
                cells.append(cell)
                if task == "optimize":
                    cells.append(str(med([r["opt_steps"] for r in ok]) or "–"))
                elif meth != "GFN-FF":
                    cells.append(str(med([r["scf_iterations"] for r in ok]) or "–"))
            ratio = med_by.get("g-xTB", 0) / med_by["GFN2-xTB"] if "GFN2-xTB" in med_by and "g-xTB" in med_by else None
            cells.append(f"{ratio:.1f}×" if ratio else "–")
            if task != "optimize":
                ok = [r for r in groups.get((m, "g-xTB", task), []) if "error" not in r]
                cells.append(f"{med([r['peak_mem_mb'] for r in ok]):.0f} MB" if ok else "–")
            out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def chart(runs, info, path):
    """Three log-log panels of median wall time vs atoms, one line per method."""
    colors = {"GFN2-xTB": "#2a78d6", "g-xTB": "#eb6834", "GFN-FF": "#1baf7a"}
    markers = {"GFN2-xTB": "circle", "g-xTB": "square", "GFN-FF": "diamond"}
    panels = [("energy", "Single point"), ("optimize", "Optimization"), ("hessian", "Frequencies")]
    groups = collections.defaultdict(list)
    for r in runs:
        if r["set"] == "methods" and "error" not in r and r["molecule"] not in ("uf6", "ferrocene"):
            groups[(r["task"], r["method"], r["atoms"])].append(r["wall_s"])
    import math

    W, H, pw, ph, ml, mt = 1120, 380, 270, 230, 70, 60
    gap = 95
    ymin, ymax = 0.03, 300
    xmin, xmax = 2, 300

    def X(i, a):
        return ml + i * (pw + gap) + (math.log10(a) - math.log10(xmin)) / (math.log10(xmax) - math.log10(xmin)) * pw

    def Y(t):
        t = min(max(t, ymin), ymax)
        return mt + ph - (math.log10(t) - math.log10(ymin)) / (math.log10(ymax) - math.log10(ymin)) * ph

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         '<title>Wall time vs number of atoms for GFN2-xTB, g-xTB and GFN-FF</title>',
         f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>',
         f'<text x="{ml}" y="22" font-size="15" font-weight="600" fill="#0b0b0b">Wall time per calculation vs molecule size (Apple M4, 4 threads, median of 3)</text>']
    for i, (task, title) in enumerate(panels):
        x0 = ml + i * (pw + gap)
        s.append(f'<text x="{x0}" y="{mt - 10}" font-size="13" font-weight="600" fill="#0b0b0b">{title}</text>')
        for t in (0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300):
            y = Y(t)
            s.append(f'<line x1="{x0}" x2="{x0 + pw}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e4e3df" stroke-width="1"/>')
            if i == 0:
                label = {0.03: "30 ms", 0.1: "0.1 s", 0.3: "0.3 s", 1: "1 s", 3: "3 s", 10: "10 s", 30: "30 s", 100: "100 s", 300: "300 s"}[t]
                s.append(f'<text x="{x0 - 8}" y="{y + 4:.1f}" text-anchor="end" fill="#52514e">{label}</text>')
        for a in (3, 10, 30, 100, 300):
            x = X(i, a)
            s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{mt}" y2="{mt + ph}" stroke="#efeeea" stroke-width="1"/>')
            s.append(f'<text x="{x:.1f}" y="{mt + ph + 16}" text-anchor="middle" fill="#52514e">{a}</text>')
        s.append(f'<text x="{x0 + pw / 2}" y="{mt + ph + 34}" text-anchor="middle" fill="#52514e">atoms</text>')
        for meth in ("GFN-FF", "GFN2-xTB", "g-xTB"):
            pts = sorted((a, statistics.median(v)) for (tk, m, a), v in groups.items() if tk == task and m == meth)
            if not pts:
                continue
            d = " ".join(f"{'M' if j == 0 else 'L'}{X(i, a):.1f},{Y(t):.1f}" for j, (a, t) in enumerate(pts))
            s.append(f'<path d="{d}" fill="none" stroke="{colors[meth]}" stroke-width="2"/>')
            for a, t in pts:
                x, y = X(i, a), Y(t)
                tip = f"<title>{meth} · {title.lower()} · {a} atoms · {fmt_s(t)}</title>"
                if markers[meth] == "circle":
                    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{colors[meth]}" stroke="#fcfcfb" stroke-width="2">{tip}</circle>')
                elif markers[meth] == "square":
                    s.append(f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" fill="{colors[meth]}" stroke="#fcfcfb" stroke-width="2">{tip}</rect>')
                else:
                    s.append(f'<path d="M{x:.1f},{y - 5:.1f} L{x + 5:.1f},{y:.1f} L{x:.1f},{y + 5:.1f} L{x - 5:.1f},{y:.1f} Z" fill="{colors[meth]}" stroke="#fcfcfb" stroke-width="2">{tip}</path>')
            if pts:
                a, t = pts[-1]
                s.append(f'<text x="{X(i, a) + 7:.1f}" y="{Y(t) + 4:.1f}" fill="#0b0b0b" font-size="11">{meth}</text>')
    lx = ml
    for meth in ("GFN2-xTB", "g-xTB", "GFN-FF"):
        s.append(f'<rect x="{lx}" y="{H - 22}" width="12" height="12" rx="2" fill="{colors[meth]}"/>')
        s.append(f'<text x="{lx + 17}" y="{H - 12}" fill="#0b0b0b">{meth}</text>')
        lx += 110
    s.append(f'<text x="{W - 10}" y="{H - 12}" text-anchor="end" fill="#52514e" font-size="11">Log scales. Each time includes about 60 ms to start the calculation. Ferrocene and UF6 are in the tables.</text>')
    s.append("</svg>")
    open(path, "w").write("\n".join(s) + "\n")


def main():
    run_dir, out_json, out_md, out_svg = sys.argv[1:5]
    info = molecule_info(os.path.join(run_dir, "mols"))
    runs = []
    for name in ("overhead", "methods", "threads"):
        for r in load(os.path.join(run_dir, f"{name}.jsonl")):
            runs.append(overhead_record(r, info) if "total_s" in r else calc_record(r, info))
    conf = load(os.path.join(run_dir, "conformers.jsonl"))
    probes = collections.defaultdict(list)
    for r in conf:
        if "--embed-probe" in r["args"] and r.get("report"):
            starts = r["report"]["starts_requested"]
            probes[(r["mol"], starts)].append(r["report"]["embed_seconds"])
    for r in conf:
        if "--embed-probe" in r["args"]:
            mol = info[r["mol"]]
            rec = {"set": "conformers", "molecule": r["mol"], "atoms": mol["atoms"], "formula": mol["formula"],
                   "method": "embedding only", "task": "conformers", "threads": 8, "repeat": r["rep"] + 1,
                   "wall_s": round(r["wall_s"], 3), "load_before": [round(x, 2) for x in r["load_before"]]}
            if r.get("report"):
                rec.update(starts=r["report"]["starts_requested"], embed_s=round(r["report"]["embed_seconds"], 3),
                           embedded=r["report"]["embed_count"])
            else:
                rec["error"] = error_of(r) or "no report"
            runs.append(rec)
        else:
            runs.append(conformer_record(r, info, probes))
    # Thread speedup against the median 1-thread wall time of the same case.
    base = collections.defaultdict(list)
    for r in runs:
        if r["set"] == "threads" and r["threads"] == 1 and "error" not in r:
            base[(r["molecule"], r["method"], r["task"])].append(r["wall_s"])
    for r in runs:
        if r["set"] == "threads" and (b := base.get((r["molecule"], r["method"], r["task"]))):
            r["speedup"] = round(statistics.median(b) / r["wall_s"], 2)
    for path in sorted(glob.glob(os.path.join(run_dir, "prof", "*.folded"))):
        name = os.path.basename(path)[:-7]
        meth, task, mol = name.split("-", 2)
        total, shares = profile_shares(path)
        runs.append({"set": "profile", "molecule": mol, "atoms": info[mol]["atoms"], "formula": info[mol]["formula"],
                     "method": METHOD[meth], "task": task, "threads": 4, "repeat": 1, "samples": total,
                     "phases": shares, "flamegraph": f"prof/{name}.svg"})
    meta_text = open(os.path.join(run_dir, "meta.txt")).read() if os.path.exists(os.path.join(run_dir, "meta.txt")) else ""
    meta = {
        "commit": os.environ.get("W2BENCH_COMMIT"),
        "base": os.environ.get("W2BENCH_BASE"),
        "machine": "Apple M4 test machine (MacBook Air, 4 performance + 6 efficiency cores, 32 GB)",
        "cores": 10,
        "threads_used": "4 for method timings (calc/calculate --threads 4); 1/2/4/8/10 in the thread set; conformer search uses the app default (8 one-thread xTB workers)",
        "os": next((l.split(":", 1)[1].strip() for l in meta_text.splitlines() if l.startswith("ProductVersion")), None),
        "engine": "axtb 0.2.0 @ 9d0388c9e9d81c43c0e7bba01c0ccf706a88fc91 (g-xTB 2.0.1)",
        "build": "cargo build --release --features xtb,conformer-bench (release profile, no LTO)",
        "idle_rule": "each run starts only after other processes use under 10% of all cores over 3 s; the 1/5/15-min load averages at that moment are in each run's load_before",
        "raw_meta": meta_text,
        "molecules": [{"name": k, **v} for k, v in sorted(info.items(), key=lambda kv: kv[1]["atoms"])],
    }
    json.dump({"meta": meta, "runs": runs}, open(out_json, "w"), indent=1)
    open(out_md, "w").write(tables(runs, info) + "\n")
    chart(runs, info, out_svg)
    print(f"{len(runs)} runs")


if __name__ == "__main__":
    main()

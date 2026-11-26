"""Write docs/benchmarks/xtb-timings.md from results.json and the method tables.

Usage: python3 w2bench_page.py RESULTS.json TABLES.md OUT.md
"""
import collections
import json
import statistics as st
import sys

results, tables_path, out = sys.argv[1:4]
R = json.load(open(results))["runs"]
NAMES = {"water": "Water", "uf6": "UF₆", "benzene": "Benzene", "aspirin": "Aspirin", "ferrocene": "Ferrocene",
         "caffeine": "Caffeine", "ala-phe": "Ala-Phe", "propranolol": "Propranolol", "tyr-gly-gly-phe": "Tyr-Gly-Gly-Phe",
         "cholesterol": "Cholesterol", "atorvastatin": "Atorvastatin", "ritonavir": "Ritonavir",
         "sirolimus": "Sirolimus (macrocycle)", "cyclosporin-a": "Cyclosporin A (cyclic peptide)"}


def med(v):
    v = [x for x in v if x is not None]
    return st.median(v) if v else None


def s(x, digits=1):
    if x is None:
        return "–"
    if x < 0.01:
        return "< 0.01 s"
    return f"{x:.{digits}f} s"


def spread(v):
    lo, hi, m = min(v), max(v), med(v)
    return f" ({lo:.1f}–{hi:.1f} s)" if hi - lo > 0.1 * m else ""


tables = open(tables_path).read()
for key, name in NAMES.items():
    tables = tables.replace(f"| {key} |", f"| {name} |")

# Threads
th = collections.defaultdict(list)
for r in R:
    if r["set"] == "threads":
        th[(r["method"], r["task"], r["threads"])].append(r["wall_s"])
cols = [("GFN2-xTB", "optimize", 2), ("GFN2-xTB", "hessian", 2), ("g-xTB", "energy", 3), ("g-xTB", "hessian", 1)]
thread_rows = []
for t in (1, 2, 4, 8, 10):
    cells = [str(t)]
    for meth, task, d in cols:
        v = th[(meth, task, t)]
        base = med(th[(meth, task, 1)])
        sp = "" if t == 1 else f"{base / med(v):.2f}×"
        rng = spread(v)
        extra = "; ".join(x for x in (sp, rng.strip(" ()")) if x)
        cells.append(f"{med(v):.{d}f} s" + (f" ({extra})" if extra else ""))
    thread_rows.append("| " + " | ".join(cells) + " |")

# Start-up
ov = collections.defaultdict(list)
for r in R:
    if r["set"] in ("overhead", "overhead_cli"):
        ov[(r["set"], r["method"])].append(r)
def ms(set_, meth, key):
    return f"{med([x[key] for x in ov[(set_, meth)]]) * 1000:.1f} ms"
meths = ("GFN-FF", "GFN2-xTB", "g-xTB")
start_rows = []
for label, key in [("Start the worker process", "spawn_s"), ("Worker ready (first reply)", "hello_s"),
                   ("Open the molecule", "open_s"), ("Calculate", "compute_s"), ("Close and exit", "close_exit_s")]:
    start_rows.append(f"| {label} | " + " | ".join(ms("overhead", m, key) for m in meths) + " |")
start_rows.append("| **Worker total** | " + " | ".join(f"**{ms('overhead', m, 'wall_s')}**" for m in meths) + " |")
start_rows.append("| Whole `reshiki --cli calc` command | " + " | ".join(f"{med([x['wall_s'] for x in ov[('overhead_cli', m)]]) * 1000:.0f} ms" for m in meths) + " |")

# Conformers
cf = collections.defaultdict(list)
for r in R:
    if r["set"] == "conformers" and r["method"] != "embedding only" and "error" not in r:
        cf[(r["atoms"], r["molecule"], r["starts"], r["method"])].append(r)
conf_rows, conf = [], {}
max_spread = 0
for (atoms, mol, starts, meth), v in sorted(cf.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][3] != "MMFF94s")):
    m = lambda k: med([x.get(k) for x in v])
    search = [x["search_s"] for x in v]
    max_spread = max(max_spread, (max(search) - min(search)) / med(search))
    conf[(mol, starts, meth)] = m("search_s")
    name = NAMES[mol] + (", GFN2-xTB minimizes every start" if meth == "GFN2-xTB" else "")
    xtb = f"{m('minimize_xtb_s'):.1f} s (minimizing all {starts} starts)" if meth == "GFN2-xTB" else s(m("rerank_s"))
    embed = m("sampling_s") if meth == "GFN2-xTB" else m("embed_s")
    conf_rows.append(f"| {name} | {atoms} | {starts} | {s(m('search_s'))} | {s(embed)} | {s(m('mmff_s'))} | "
                     f"{s(m('cluster_s'), 2)} | {xtb} | {m('valid_starts'):.0f} | {m('clusters'):.0f} | {m('kept'):.0f} | {m('file_kb'):.0f} KB |")
rit = {k[2]: v[0]["notes"] for k, v in cf.items() if k[1] == "ritonavir"}
assert "77 of 100" in rit[100][0] and "51 starts" in rit[100][1] and "225 of 300" in rit[300][0] and "155 starts" in rit[300][1], rit

# Profiles
pr = {(r["method"], r["task"]): r["phases"] for r in R if r["set"] == "profile"}
order = [("GFN2-xTB", "energy"), ("g-xTB", "energy"), ("GFN2-xTB", "hessian"), ("g-xTB", "hessian")]
def pct(x):
    return "–" if not x else ("< 1%" if x < 0.005 else f"{x * 100:.0f}%")
prof_rows = []
for label, keys in [
    ("Diagonalization (tridiagonal eigensolver, generalized eigenproblem)", ["diagonalization"]),
    ("Hamiltonian / Fock build, density, populations", ["Hamiltonian / Fock build, density, populations"]),
    ("Exchange (g-xTB)", ["exchange (g-xTB)"]),
    ("Hessian response (CPSCF) and derivative terms", ["Hessian: response (CPSCF) and derivative terms"]),
    ("Integrals", ["integrals"]), ("Electrostatics", ["electrostatics"]), ("Dispersion", ["dispersion"]),
    ("Repulsion", ["repulsion"]),
    ("Matrix multiply on pool threads (caller not on the stack)", ["matrix multiply on pool threads (faer GEMM; caller not on the stack)"]),
    ("Idle worker threads, other engine code", ["idle worker threads (yield/wait)", "other engine code"]),
    ("Process start, command line and output", ["process start, CLI and I/O (no engine frame)"]),
]:
    prof_rows.append(f"| {label} | " + " | ".join(pct(sum(pr[o].get(k, 0) for k in keys)) for o in order) + " |")

page = f"""# xTB timings

How long GFN2-xTB, g-xTB 2.0.1 and GFN-FF calculations and conformer searches
take in ReShiki, measured through the same code the desktop app runs.

![Wall time per calculation against molecule size for GFN2-xTB, g-xTB and GFN-FF: single point, optimization and frequencies](xtb-timings.svg)

## What this means for you

- **Single points are instant at every size.** Up to 196 atoms each method
  takes 0.06 to 0.3 s, and much of that is starting the calculation (about
  60 ms). In the engine, g-xTB costs about the same as GFN2-xTB here.
- **Optimizations take seconds.** At about 100 atoms GFN2-xTB takes 1.8 s and
  g-xTB 4.1 s; at 196 atoms, 7 s and 21 s. g-xTB costs 2–3 times GFN2-xTB from
  about 70 atoms up.
- **Frequencies are where g-xTB is expensive.** Its analytic Hessian costs 16
  times GFN2-xTB at about 100 atoms (10 s against 0.6 s) and 21 times at 196
  atoms (99 s against 4.7 s, with 0.9 GB of memory). Use g-xTB for frequencies
  when you need its accuracy for a molecule up to about 100 atoms, or are ready
  to wait one to two minutes at 150–200 atoms.
- **GFN-FF is the fastest for energies and frequencies**: in the engine,
  single points are 10–50 times and Hessians 3–40 times cheaper than with
  GFN2-xTB. Its optimizations gain less: from 74 atoms up they are 1.2–3.6
  times faster than GFN2-xTB, and below that about as fast or slower, because
  they take more steps and each step also pays for the optimizer itself.
- **Conformer search** with the default settings (100 starts, MMFF94s, normal
  diversity, 20 re-ranked with GFN2-xTB) takes about {conf[('propranolol', 100, 'MMFF94s')]:.0f} s at 40 atoms,
  {conf[('tyr-gly-gly-phe', 100, 'MMFF94s')]:.0f} s at 58, {conf[('atorvastatin', 100, 'MMFF94s')]:.0f} s at 76 and {conf[('ritonavir', 100, 'MMFF94s')]:.0f} s at 98 atoms. 300 starts take
  {conf[('tyr-gly-gly-phe', 300, 'MMFF94s')] / conf[('tyr-gly-gly-phe', 100, 'MMFF94s')]:.1f} times as long at 58 atoms and {conf[('ritonavir', 300, 'MMFF94s')] / conf[('ritonavir', 100, 'MMFF94s')]:.1f} times as long at 98 atoms.
  Minimizing all 100 starts with GFN2-xTB instead of MMFF94s takes
  {conf[('propranolol', 100, 'GFN2-xTB')]:.0f} s at 40 atoms and keeps every cluster.
- **Threads:** on this machine 4 threads (its performance cores) are fastest
  for optimizations and g-xTB. 8 or 10 threads, which add efficiency cores,
  are 7–19% slower there. GFN2-xTB frequencies gain up to 10 threads.

## Setup

| Item | Value |
| --- | --- |
| Code | `xtb/next` at 05965b403 plus this page's benchmark driver (method timings at 836ed6ff3, conformer search at 6360224cd; the engine and app code are the same); engine axtb 0.2.0 at 9d0388c (g-xTB 2.0.1) |
| Build | `cargo build --release --features xtb,conformer-bench` (release profile; published builds add LTO) |
| Machine | Apple M4 test machine (MacBook Air, 4 performance and 6 efficiency cores, 32 GB, no fan), macOS 27.0.1 |
| Threads | 4 (`--threads 4`) unless a table says otherwise. The Calculate card's Auto uses up to 8. The conformer search uses its default, Auto: up to 8 one-thread xTB workers at once |
| Repeats | 3 per case, run round-robin (every case once, then again); medians, with min–max where the spread exceeds 10% of the median. UF₆ with GFN2-xTB and GFN-FF ran once |
| Idle check | Each run started only when other processes used under 6% of all cores over 3 s |
| Date | 2026-11-26 |

Single points and frequencies ran through `reshiki --cli calc --task energy`
or `--task hessian`, which sends one request to the same
[xTB worker](../xtb-worker.md) the app starts. Optimizations ran through
`reshiki --cli calculate --task optimize`, which drives the worker with the
app's own optimizer and its Normal convergence. The times are wall times of
the whole command: process start, worker start, setup, calculation and
output. Peak memory is the largest resident set of the command and its
worker. Every calculation started from the same fixed geometry (hydrogens
added, embedded with RDKit ETKDGv3 seed 42, minimized with MMFF94s; ferrocene
and UF₆ idealized), so the frequencies are at a geometry that is not a
stationary point of each method: the time is about the same, but the
frequencies are not meaningful. In the app, Optimize + Frequencies first
optimizes with Tight convergence.

Each method ran with its defaults: GFN2-xTB at an electronic temperature of
300 K, g-xTB at 0 K. Swapping them (GFN2-xTB at 0 K, g-xTB at 300 K) changed
no time by more than 6% on ritonavir.

## Methods by size
{tables}
SCF iterations are the worker's count for the converged SCF. With a GFN2-xTB
Hessian the engine reports 2. Optimization steps are accepted optimizer steps;
each also computes a gradient. GFN2-xTB has no parameters for uranium, so UF₆
runs only with g-xTB and GFN-FF.

In the engine alone (the time the worker reports for the calculation), g-xTB
single points cost 0.9–1.4 times GFN2-xTB from 74 to 196 atoms. At 196 atoms
the engine time is 70% of the GFN2-xTB wall time and 61% of the g-xTB wall
time; this page does not break the rest down by step at that size.

## Threads

Ritonavir (98 atoms), median of 3 wall times; speedup against 1 thread, and
min–max where it spreads more than 10%.

| Threads | GFN2-xTB optimization | GFN2-xTB frequencies | g-xTB single point | g-xTB frequencies |
| --: | --: | --: | --: | --: |
""" + "\n".join(thread_rows) + f"""

The M4 has 4 performance cores. Threads beyond 4 run on efficiency cores and
wait for each other, so only the GFN2-xTB Hessian still gains. Optimizations
gain little from threads at this size: each step is short, and the conformer
search uses one thread per worker for that reason.

## Starting a calculation

Water, one thread, median of 10.

| Step | GFN-FF | GFN2-xTB | g-xTB |
| --- | --: | --: | --: |
""" + "\n".join(start_rows) + f"""

Every calculation in the app starts a fresh worker, about 25 ms on this
machine. The command line adds its own start (about 37 ms), which the app
does not pay.

## Conformer search

The app's own search (`src/app/xtb/conformers/pipeline.rs`), driven from the
command line by the developer-only `reshiki --conformer-bench` (build feature
`conformer-bench`). It reads a SMILES, makes the 3D model as the app does for a
calculation, and runs the search with the Calculate card's defaults: 100
starts, MMFF94s, normal diversity, 15 kcal/mol window, 20 representatives
re-ranked with GFN2-xTB, lowest 1 per cluster, Auto threads (8 workers). Median
of 3 runs; the searches differed by under {max(2, -(-max_spread * 100 // 1)):.0f}%.

| Molecule | Atoms | Starts | Search | Embedding | MMFF94s | Clustering | GFN2-xTB re-rank | Valid starts | Clusters | Kept | Saved file |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: | --: |
""" + "\n".join(conf_rows) + f"""

- **Search** is the pipeline from its first step to the ranked result. Making
  the 3D model first adds 0.1 s (40 atoms) to 1.1 s (98 atoms).
- **Embedding** is measured in separate runs that embed the same starts
  without minimizing them; it includes setting up the force field and one
  energy per start. **MMFF94s** is the search's sampling step minus that
  median, an estimate. **GFN2-xTB re-rank** runs from the first to the last
  re-ranked representative; ranking and deduplication after it take under
  3 ms. When GFN2-xTB minimizes every start, clustering includes that final
  ranking.
- **Valid starts** are those that embedded and converged with the force field.
  For ritonavir the geometry worker made 77 of 100 starts (225 of 300), and
  51 (155) did not converge within MMFF94s's step limit, so 26 (70) remained.
  With GFN2-xTB minimizing every start, the starts are only embedded (the
  Embedding column) and every one is kept.
- **Saved file** is the `.rsk` document with the generated 3D model and the
  attached result, before the lowest conformer is applied to the model; the
  model alone is 19–49 KB.

## Where the time goes in the engine

Sampling profiles (Time Profiler) of ritonavir, 98 atoms, 4 threads. Shares
of on-CPU samples across all threads; each sample counts toward the innermost
engine function it is in.

| Share of samples | GFN2-xTB single point | g-xTB single point | GFN2-xTB Hessian | g-xTB Hessian |
| --- | --: | --: | --: | --: |
""" + "\n".join(prof_rows) + """

The engine is pure Rust (faer for linear algebra). For GFN2-xTB single points
the eigensolver is the largest cost; for g-xTB single points the Hamiltonian
build and the eigensolver take about a quarter each. For Hessians the
response equations dominate, and for g-xTB its exchange term too.

## Reproduce

1. Build: `cargo build --release --features xtb,conformer-bench`.
2. Geometries: for each SMILES in the
   [evidence inputs](https://github.com/Ameyanagi/ReShiki-evidence/tree/main/pr-reviews/pr1452/mols),
   add hydrogens, embed with RDKit ETKDGv3 (random seed 42) and minimize with
   MMFF94s to convergence; write XYZ. The XYZ files used are there too.
3. Method timings: `reshiki --cli calc --task energy|hessian --method gfn2|gxtb|gfnff --threads 4 FILE.xyz`
   and `reshiki --cli calculate --task optimize --method … --threads 4 FILE.xyz`,
   each under `/usr/bin/time -l` for the peak memory.
4. Conformer search: `reshiki --conformer-bench FILE.smi [--starts 300] [--minimizer gfn2]`
   prints one JSON line with the phase times, counts and file sizes;
   `--embed-probe` times only embedding the same starts.

The scripts (geometries, round-robin runner with the idle check, worker
start-up timer, profile folding) and every run's raw record are in the
[pull request's evidence](https://github.com/Ameyanagi/ReShiki-evidence/tree/main/pr-reviews/pr1452).

## Limits

- One machine: an Apple M4 without a fan. Long runs can slow down as it
  warms; the round-robin order spreads that over all cases. Expect different
  numbers on other computers, and relative costs to hold better than absolute
  times.
- The command line adds about 37 ms per calculation that the app does not pay;
  the app shows orbitals and bond orders after a calculation, which the
  command line does not compute.
- Molecules are single conformers of one structure each; the step counts of
  optimizations depend on the starting geometry.
"""
open(out, "w").write(page)

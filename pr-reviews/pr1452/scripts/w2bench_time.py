"""Time ReShiki's xTB CLI (`calc` / `calculate`) runs: wall time, peak memory, SCF iterations, steps.

Usage: uv run --no-project --with psutil python w2bench_time.py RESHIKI MOLS_DIR OUT.jsonl PLAN.json
PLAN.json: list of {"set", "mol", "method", "task", "threads", "repeats", "extra"?}; task is
energy|optimize|hessian. Repeats run round-robin (every case once, then again) so slow drift,
heat and run order fall on all cases alike. Each run waits until other processes use under
MAX_BUSY % of all cores over 3 s, and records the load averages at that moment.
Each command runs under /usr/bin/time -l: on macOS its "maximum resident set size" is the
largest of the CLI process and the xTB worker it waits for.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time

import psutil

MAX_BUSY = float(os.environ.get("W2BENCH_MAX_BUSY", "6"))


def command(exe, mols, case):
    xyz = os.path.join(mols, case["mol"] + ".xyz")
    common = ["--method", case["method"], "--threads", str(case["threads"]), *case.get("extra", []), xyz]
    if case["task"] == "optimize":
        return [exe, "--cli", "calculate", "--task", "optimize", *common]
    return [exe, "--cli", "calc", "--task", case["task"], *common]


def wait_idle():
    waited = 0.0
    while (busy := psutil.cpu_percent(interval=3)) > MAX_BUSY:
        waited += 3
    return os.getloadavg(), waited, busy


def run_once(cmd):
    load, waited, busy = wait_idle()
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        start = time.perf_counter()
        code = subprocess.run(["/usr/bin/time", "-l", *cmd], stdout=out, stderr=err, check=False).returncode
        wall = time.perf_counter() - start
        out.seek(0)
        err.seek(0)
        stdout, stderr = out.read().decode(errors="replace"), err.read().decode(errors="replace")
    usage = {}
    for key, pattern in (("maxrss", r"(\d+)\s+maximum resident set size"), ("user", r"([\d.]+) user"),
                         ("sys", r"([\d.]+) sys"), ("footprint", r"(\d+)\s+peak memory footprint")):
        if m := re.search(pattern, stderr):
            usage[key] = float(m.group(1))
    tail = "\n".join(line for line in stderr.splitlines() if not re.match(r"^\s+[\d.]+ ", line))
    return {
        "wall_s": wall,
        "exit": code,
        "peak_rss_mb": usage.get("maxrss", 0) / 2**20,
        "cpu_user_s": usage.get("user"),
        "cpu_sys_s": usage.get("sys"),
        "load_before": load,
        "waited_s": waited,
        "busy_before_pct": busy,
        "stdout": stdout,
        "stderr": tail[-2000:],
    }


def summarize(case, raw):
    """Pull timing-relevant fields out of the JSON line without keeping big arrays."""
    row = {k: v for k, v in raw.items() if k != "stdout"}
    text = raw["stdout"].strip()
    try:
        data = json.loads(text[text.index("{"):]) if text else None
    except ValueError:
        data = None
    if data is None:
        if raw["exit"] == 0:
            row["exit"] = -1
            row["stderr"] = "no JSON result on stdout. " + row["stderr"]
        return row
    if case["task"] == "optimize":
        value = data.get("value", {})
        opt = value.get("optimization") or {}
        row.update(energy=value.get("energy_hartree"), steps=opt.get("steps"),
                   converged=opt.get("converged"), reported_s=value.get("seconds"),
                   gap_ev=value.get("homo_lumo_gap_ev"), warnings=data.get("warnings") or value.get("warnings"))
    else:
        scf = data.get("scf") or {}
        row.update(energy=data.get("energy"), scf_iterations=scf.get("iterations"),
                   etemp_k=scf.get("electronic_temperature_k"), scf_start=scf.get("start"),
                   reported_s=data.get("seconds"), hessian_method=data.get("hessian_method"),
                   gap_ev=data.get("homo_lumo_gap_ev"), settings=data.get("settings"))
    return row


def main():
    exe, mols, out_path, plan_path = sys.argv[1:5]
    plan = json.load(open(plan_path))
    with open(out_path, "a") as out:
        for rep in range(max(case.get("repeats", 3) for case in plan)):
            for case in plan:
                if rep >= case.get("repeats", 3):
                    continue
                raw = run_once(command(exe, mols, case))
                row = {**case, "rep": rep, **summarize(case, raw)}
                out.write(json.dumps(row) + "\n")
                out.flush()
                print(case["set"], case["mol"], case["method"], case["task"], case["threads"], rep,
                      f"{row['wall_s']:.2f}s exit={row['exit']}", flush=True)


if __name__ == "__main__":
    main()

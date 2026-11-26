"""Run `reshiki --conformer-bench` cases, three repeats each (round-robin), waiting for an idle machine.

Usage: python3 w2bench_conf.py RESHIKI MOLS_DIR OUT.jsonl
"""

import json
import os
import subprocess
import sys
import time

import psutil

MAX_BUSY = float(os.environ.get("W2BENCH_MAX_BUSY", "6"))
CASES = [
    # (molecule, extra arguments, repeats)
    ("propranolol", [], 3),
    ("tyr-gly-gly-phe", [], 3),
    ("atorvastatin", [], 3),
    ("ritonavir", [], 3),
    ("tyr-gly-gly-phe", ["--starts", "300"], 3),
    ("ritonavir", ["--starts", "300"], 3),
    ("propranolol", ["--minimizer", "gfn2"], 3),
    # Embedding only (no minimization, no search), in runs of their own.
    ("propranolol", ["--embed-probe"], 3),
    ("tyr-gly-gly-phe", ["--embed-probe"], 3),
    ("atorvastatin", ["--embed-probe"], 3),
    ("ritonavir", ["--embed-probe"], 3),
    ("tyr-gly-gly-phe", ["--starts", "300", "--embed-probe"], 3),
    ("ritonavir", ["--starts", "300", "--embed-probe"], 3),
]


def main():
    exe, mols, out_path = sys.argv[1:4]
    with open(out_path, "a") as out:
        for rep in range(3):
            for mol, extra, repeats in CASES:
                if rep >= repeats:
                    continue
                waited = 0
                while (busy := psutil.cpu_percent(interval=3)) > MAX_BUSY:
                    waited += 3
                load = os.getloadavg()
                cmd = [exe, "--conformer-bench", os.path.join(mols, mol + ".smi"), *extra]
                start = time.perf_counter()
                proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
                wall = time.perf_counter() - start
                row = {"set": "conformers", "mol": mol, "args": extra, "rep": rep, "wall_s": wall,
                       "exit": proc.returncode, "load_before": load, "waited_s": waited, "busy_before_pct": busy,
                       "stderr": proc.stderr[-2000:]}
                if proc.returncode == 0:
                    row["report"] = json.loads(proc.stdout.strip().splitlines()[-1])
                out.write(json.dumps(row) + "\n")
                out.flush()
                print(mol, extra, rep, f"{wall:.1f}s exit={proc.returncode}", flush=True)


if __name__ == "__main__":
    main()

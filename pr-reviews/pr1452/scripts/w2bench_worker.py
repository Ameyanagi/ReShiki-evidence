"""Per-calculation overhead of the xTB worker the app uses, phase by phase, on one small molecule.

Usage: uv run --no-project --with psutil python w2bench_worker.py RESHIKI MOL.xyz OUT.jsonl REPEATS
Speaks the worker protocol (docs/xtb-worker.md) directly, as crates/xtb-worker's client does:
spawn `RESHIKI --xtb-worker` (AXTB_LAPACK* removed), hello, open, compute (energy), close, exit.
Each phase is timed from request sent to response read. Methods run round-robin.
"""

import json
import os
import struct
import subprocess
import sys
import time

import psutil

MAGIC = b"RSHXTBWK"


def send(proc, ident, message):
    body = json.dumps({"id": ident, **message}).encode()
    proc.stdin.write(MAGIC + struct.pack("<HHI", 2, 0, len(body)) + body)
    proc.stdin.flush()


def frame(proc):
    header = proc.stdout.read(16)
    assert header[:8] == MAGIC, header
    _, kind, length = struct.unpack("<HHI", header[8:])
    return kind, proc.stdout.read(length)


def response(proc):
    kind, body = frame(proc)
    assert kind == 0
    reply = json.loads(body)
    if "ok" not in reply:
        raise RuntimeError(reply)
    for array in reply["ok"].get("arrays", []) if isinstance(reply["ok"], dict) else []:
        for _ in range(array.get("chunks", 0)):
            frame(proc)
    return reply["ok"]


def one(exe, method, numbers, positions):
    env = {k: v for k, v in os.environ.items() if k not in ("AXTB_LAPACK", "AXTB_LAPACK_BLAS")}
    times = {}
    t0 = time.perf_counter()
    proc = subprocess.Popen([exe, "--xtb-worker"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env)
    times["spawn_s"] = time.perf_counter() - t0
    t = time.perf_counter()
    send(proc, 1, {"op": "hello"})
    response(proc)
    times["hello_s"] = time.perf_counter() - t
    t = time.perf_counter()
    send(proc, 2, {"op": "open", "numbers": numbers, "positions": positions, "units": "angstrom",
                   "charge": 0, "method": method, "threads": 1, "heap_bytes": 2 * 1024**3})
    response(proc)
    times["open_s"] = time.perf_counter() - t
    t = time.perf_counter()
    send(proc, 3, {"op": "compute", "units": "angstrom", "gradient": False})
    computed = response(proc)
    times["compute_s"] = time.perf_counter() - t
    times["engine_compute_s"] = computed["seconds"]
    t = time.perf_counter()
    send(proc, 4, {"op": "close"})
    response(proc)
    proc.wait()
    times["close_exit_s"] = time.perf_counter() - t
    times["total_s"] = time.perf_counter() - t0
    return times


def main():
    exe, xyz, out_path, repeats = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    z = {"H": 1, "C": 6, "N": 7, "O": 8}
    lines = open(xyz).read().splitlines()
    atoms = [line.split() for line in lines[2 : 2 + int(lines[0])]]
    numbers = [z[a[0]] for a in atoms]
    positions = [[float(x) for x in a[1:4]] for a in atoms]
    with open(out_path, "a") as out:
        for rep in range(repeats):
            for method in ("gfnff", "gfn2", "gxtb"):
                while psutil.cpu_percent(interval=3) > 6:
                    pass
                row = {"set": "overhead", "mol": os.path.basename(xyz)[:-4], "method": method, "rep": rep,
                       "load_before": os.getloadavg(), **one(exe, method, numbers, positions)}
                out.write(json.dumps(row) + "\n")
                out.flush()
                print(method, rep, f"{row['total_s'] * 1000:.1f} ms", flush=True)


if __name__ == "__main__":
    main()

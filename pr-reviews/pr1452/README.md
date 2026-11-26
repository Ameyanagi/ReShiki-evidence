# PR 1452: xTB timings (Apple M4 test machine, 2026-11-26)

- `results.json`: every measured run (`meta` + `runs`), as summarized in docs/benchmarks/xtb-timings.md.
- `raw/`: the runner's JSON lines (`methods`, `threads` (+ sensitivity), `overhead` (worker protocol + CLI), `conformers`) and `meta.txt` (OS, CPU, binary and input SHA-256).
- `mols/`: the fixed input geometries (XYZ) and SMILES.
- `profiles/`: Time Profiler flame graphs (SVG) and folded stacks of ritonavir single points and Hessians (GFN2-xTB, g-xTB; 4 threads).
- `scripts/`: geometry builder (`w2bench_mols.py`, RDKit), runners (`w2bench_all.sh`, `w2bench_time.py`, `w2bench_conf.py`, `w2bench_worker.py`), profiling (`w2bench_prof.sh`, `w2bench_xctrace.py`), aggregation and chart (`w2bench_report.py`), plans (`plan-*.json`).
- Binary: `cargo build --release --features xtb,conformer-bench` at ReShiki 836ed6ff3 (xtb/next 05965b403 + the benchmark driver).

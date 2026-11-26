#!/bin/bash
# W2-bench: every measurement, in order, each run waiting for an idle machine.
cd ~/dev/ReShiki-agents-wt/w2bench-run || exit 1
R=./w2bprof; PY="uv run --no-project --with psutil python"
idle() { $PY -c 'import psutil
while psutil.cpu_percent(interval=3) > 6: pass'; }
{ date; uptime; sw_vers; sysctl -n machdep.cpu.brand_string hw.ncpu hw.perflevel0.physicalcpu hw.perflevel1.physicalcpu hw.memsize; $R --version; shasum -a 256 $R mols/*; } > meta.txt 2>&1
# Warm-up (discarded): first launch, dyld and file cache.
for m in gfnff gfn2 gxtb; do $R --cli calc --task energy --method $m mols/water.xyz > /dev/null; done
$R --conformer-bench mols/propranolol.smi --starts 10 > /dev/null
$PY w2bench_worker.py $R mols/water.xyz overhead.jsonl 10
$PY w2bench_time.py $R mols overhead.jsonl plan-overhead.json
$PY w2bench_time.py $R mols methods.jsonl plan-methods.json
$PY w2bench_time.py $R mols threads.jsonl plan-threads.json
$PY w2bench_conf.py $R mols conformers.jsonl
idle; ./w2bench_prof.sh gfn2-energy-ritonavir 40 -- --cli calc --task energy --method gfn2 --threads 4 mols/ritonavir.xyz
idle; ./w2bench_prof.sh gxtb-energy-ritonavir 8 -- --cli calc --task energy --method gxtb --threads 4 mols/ritonavir.xyz
idle; ./w2bench_prof.sh gfn2-hessian-ritonavir 3 -- --cli calc --task hessian --method gfn2 --threads 4 mols/ritonavir.xyz
idle; ./w2bench_prof.sh gxtb-hessian-ritonavir 1 -- --cli calc --task hessian --method gxtb --threads 4 mols/ritonavir.xyz
{ date; uptime; } >> meta.txt
echo ALLDONE > all.status

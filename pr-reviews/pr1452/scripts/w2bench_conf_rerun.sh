#!/bin/bash
# W2-bench: conformer set again with the embedding probe in runs of its own.
cd ~/dev/ReShiki-agents-wt/w2bench-run || exit 1
mv conformers.jsonl conformers-probe-inline.jsonl 2>/dev/null
./w2bprof --conformer-bench mols/propranolol.smi --starts 10 > /dev/null
uv run --no-project --with psutil python w2bench_conf.py ./w2bprof mols conformers.jsonl
echo CONFDONE > conf.status

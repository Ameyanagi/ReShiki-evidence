#!/bin/bash
# w2bench_prof.sh NAME REPS -- reshiki args...: Time Profiler (all processes) while the w2bprof
# binary runs REPS times; fold the samples of w2bprof processes into NAME.folded and NAME.svg.
set -u
name=$1; reps=$2; shift 3
cd ~/dev/ReShiki-agents-wt/w2bench-run || exit 1
mkdir -p prof; rm -rf prof/$name.trace
xctrace record --template "Time Profiler" --all-processes --output prof/$name.trace > prof/$name.xctrace.log 2>&1 &
rec=$!
until grep -q -i "starting recording\|recording started\|Ctrl-C" prof/$name.xctrace.log; do sleep 0.5; done
sleep 2
for i in $(seq 1 $reps); do ./w2bprof "$@" > /dev/null; done
kill -INT $rec; wait $rec
xctrace export --input prof/$name.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]' > prof/$name.xml
python3 w2bench_xctrace.py prof/$name.xml w2bprof prof/$name.folded
~/.cargo/bin/inferno-flamegraph --title "$name" prof/$name.folded > prof/$name.svg
rm -rf prof/$name.trace prof/$name.xml

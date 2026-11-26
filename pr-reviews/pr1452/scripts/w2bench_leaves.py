"""Group a folded profile by the deepest engine (axtb) frame of each sample.

Usage: python3 w2bench_leaves.py FILE.folded [N]
"""
import collections, re, sys

path, top = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30
deep, leaf, total = collections.Counter(), collections.Counter(), 0
clean = re.compile(r"<[^<>]*>")
for line in open(path):
    stack, n = line.rsplit(" ", 1)
    n = int(n)
    total += n
    frames = stack.split(";")
    engine = [f for f in frames if "axtb" in f]
    name = engine[-1] if engine else ("(worker, outside axtb)" if any("xtb_worker" in f for f in frames) else "(CLI process / startup)")
    for _ in range(4):
        name = clean.sub("", name)
    deep[name[:120]] += n
    leaf[clean.sub("", frames[-1])[:60]] += n
print(f"{path}: {total} samples")
for k, v in deep.most_common(top):
    print(f"{v / total:6.1%} {k}")
print("-- leaf")
for k, v in leaf.most_common(12):
    print(f"{v / total:6.1%} {k}")

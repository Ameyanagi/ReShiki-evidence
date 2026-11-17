import sys, re
from pathlib import Path
run = Path(sys.argv[1])
ev = []
for line in (run/"probe.log").read_text(errors="replace").splitlines():
    p = line.split(" ", 4)
    if len(p) >= 4: ev.append((float(p[0]), p[1], int(p[2])/1000, p[3], p[4] if len(p) > 4 else ""))
ev.sort()
marks = {l.split(" ",1)[1].strip(): float(l.split(" ",1)[0]) for l in (run/"marks.txt").read_text().splitlines() if l.strip()}
a, b = marks["03b-scroll-1"], marks["04-open-drawing"]
seg = [e for e in ev if a <= e[0] < b]
t0 = next(e[0] for e in seg if e[1]=="U" and "Picker(Scrolled(" in e[4])
cut = next((e[0] for e in seg if e[1]=="U" and "PickRepo(" in e[4]), b)
rep = [e for e in seg if e[1]=="U" and t0 <= e[0] < cut and re.search(r"Picker\((Changed|Thumb)\(", e[4])]
http = [e for e in seg if e[1]=="H" and t0 <= e[0] < cut]
kept = [e for e in seg if e[1]=="K" and t0 <= e[0] < cut]
last = max(e[0] for e in rep)
frame = next(e[0] for e in ev if e[1]=="F" and e[0] >= last)
print(f"scroll: settled {frame-t0:.0f} ms, req {len(http)}, kept {len(kept)}")

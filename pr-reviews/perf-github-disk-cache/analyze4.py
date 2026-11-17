"""Per-flow timings of a disk-cache probe run: analyze4.py <run dir> [-t].

Like step 1's analyze2.py, for a run of two launches (A: first, B: after a
restart with the same data folder). For each marked flow, from its trigger:
  listed   = first frame after the folder's Listing(Ok) / Downloaded / list,
  settled  = first frame after the flow's last GitHub reply,
  req      = H lines (network requests), 304 = of them answered 304,
  mem/disk = replies served from the session cache (K) / from disk (KD),
  conns    = new connections the mock accepted, max upd = slowest update.
B0-launch: from the mark to the first frame drawn. Everything is counted
within WINDOW of the trigger, so the next unmarked step is left out.
"""
import re
import sys
from pathlib import Path

run = Path(sys.argv[1])
events = []
for line in (run / "probe.log").read_text(errors="replace").splitlines():
    parts = line.split(" ", 4)
    if len(parts) < 4:
        continue
    events.append((float(parts[0]), parts[1], int(parts[2]) / 1000.0, parts[3], parts[4] if len(parts) > 4 else ""))
events.sort()
conns = [float(m.group(1)) for m in re.finditer(r"MOCK ([\d.]+) conn=\d+ accepted", (run / "mock.log").read_text(errors="replace"))]
marks = []
for line in (run / "marks.txt").read_text().splitlines():
    if line.strip():
        t, label = line.split(" ", 1)
        marks.append((float(t), label.strip()))
marks.sort()
marks.append((float("inf"), "END"))

TRIGGER = {
    "1-picker-open": r"Picker\(Show\(",
    "2-choose-repo": r"Picker\(PickRepo\(",
    "3-open-routes": r"Picker\(Select\(",
    "4-bigfolder-open": r"Picker\(Enter\)",
    "5-open-drawing": r"Picker\(Select\(",
    "6-history": r"ShowVersions|Versions\(|History",
}
REPLY = re.compile(r"GitHub\((Picker\((Listing|Changed|Thumb|Downloaded|Written|Resolved)\(|Listed\(|Persisted\(|Versions\((RemoteLoaded|Doc)\()")
FIRST = re.compile(r"GitHub\((Picker\((Listing\(\d+, Ok|Downloaded\()|Versions\(RemoteLoaded\()")


WINDOW = 6000.0


def frame_after(t):
    return next((e[0] for e in events if e[1] == "F" and e[0] >= t), t)


def short(path):
    path = re.sub(r"[0-9a-f]{40}", "<sha>", path)
    path = re.sub(r"/repos/[^/]+/[^/]+", "/repos/<r>", path)
    return re.sub(r"path=[^&]+", "path=<p>", path)


rows = []
for (start, label), (end, _) in zip(marks, marks[1:]):
    seg = [e for e in events if start <= e[0] < end]
    if label == "B0-launch":
        first = next((e[0] for e in seg if e[1] == "F"), None)
        rows.append((label, first - start if first else None, None, 0, 0, 0, 0, 0, 0))
        continue
    key = next((k for k in TRIGGER if label[1:] == k), None)
    if key is None:
        continue
    ups = [e for e in seg if e[1] == "U"]
    replies = [e for e in ups if REPLY.search(e[4])]
    first_reply = next((e for e in ups if FIRST.search(e[4])), None)
    cut = first_reply[0] if first_reply else float("inf")
    cands = [e for e in ups if re.search(TRIGGER[key], e[4]) and e[0] <= cut]
    if not cands:
        print(f"{label}: no trigger")
        continue
    # A double click: the second Select opens.
    trig = cands[-1] if "Select" in TRIGGER[key] else cands[0]
    t0 = trig[0] - trig[2]
    seg = [e for e in seg if e[0] <= t0 + WINDOW]
    ups = [e for e in seg if e[1] == "U"]
    replies = [e for e in ups if REPLY.search(e[4])]
    after = [e for e in replies if e[0] >= t0]
    http = [e for e in seg if e[1] == "H" and e[0] - e[2] >= t0 - 1]
    unchanged = [e for e in http if "status=304" in e[4]]
    mem = [e for e in seg if e[1] == "K" and e[0] >= t0]
    disk = [e for e in seg if e[1] == "KD" and e[0] >= t0]
    new = [c for c in conns if t0 - 1 <= c < min(end, t0 + WINDOW)]
    listed = frame_after(first_reply[0]) - t0 if first_reply and first_reply[0] >= t0 else None
    settled = frame_after(max([trig[0]] + [e[0] for e in after])) - t0
    worst = max((e[2] for e in ups if e[0] >= t0), default=0)
    ui_disk = sum(e[2] for e in seg if e[1] == "D" and e[3] == "UI" and e[0] >= t0)
    rows.append((label, listed, settled, len(http), len(unchanged), len(mem), len(disk), len(new), worst, ui_disk))
    if "-t" in sys.argv:
        print(f"\n== {label}")
        for e in seg:
            if e[0] >= t0 and e[1] in ("U", "H", "K", "KD", "D") and (e[1] != "U" or "GitHub(" in e[4] or e[2] > 2):
                print(f"   +{e[0] - t0:7.1f} {e[1]:2s} {e[2]:7.2f} {e[3]:3s} {short(e[4])[:110]}")

fmt = lambda v: "-" if v is None else f"{v:.0f}"
print(f"{'flow':20s} {'listed':>7s} {'settled':>8s} {'req':>4s} {'304':>4s} {'mem':>4s} {'disk':>5s} {'conns':>5s} {'max upd':>8s} {'ui disk':>8s}")
for row in rows:
    if row[0] == "B0-launch":
        print(f"{row[0]:20s} first frame {fmt(row[1])} ms after the launch mark")
        continue
    label, listed, settled, req, n304, mem, disk, new, worst, ui = row
    print(f"{label:20s} {fmt(listed):>7s} {settled:8.0f} {req:4d} {n304:4d} {mem:4d} {disk:5d} {new:5d} {worst:8.1f} {ui:8.2f}")

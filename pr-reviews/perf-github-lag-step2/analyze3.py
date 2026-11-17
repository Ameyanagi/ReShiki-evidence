"""Per-flow timings of a step-2 probe run: analyze3.py <run dir> [-t].

Reads probe.log (app) and marks.txt. For each marked flow, from its trigger
(the first update after the mark that the user's input caused):
  max upd  = slowest App::update in the flow's first 3 s, and its message,
  ui disk  = synchronous disk spans on the UI thread (sum, ms),
  bg disk  = disk spans off the UI thread (sum, ms),
  rows     = History: first frame after the commit list arrived,
  done     = first frame after the flow's last GitHub reply or write,
  requests = H lines (network requests).
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
marks = []
for line in (run / "marks.txt").read_text().splitlines():
    if line.strip():
        t, label = line.split(" ", 1)
        marks.append((float(t), label.strip()))
marks.sort()
marks.append((float("inf"), "END"))

TRIGGER = {
    "04": r"Picker\((Select|Open|Enter)",
    "05": r"^Save$|Save\b",
    "06": r"Tabs\(Select",
    "07": r"GitHub\(Focused\)",
    "08a": r"GitHub\(ShowVersions\)",
    "08b": r"Tabs\(Select",
    "08c": r"Tabs\(Select",
}
REPLY = re.compile(r"GitHub\((Picker\((Downloaded|Written|Read)\(|Newer\(|Access\(|Scanned\(|Updated\(|Settled\(|Versions\((RemoteLoaded|Doc)\()|FilePrepared")
WINDOW = 3000.0
LIST = re.compile(r"Versions\(RemoteLoaded\(")


def frame_after(t):
    return next((e[0] for e in events if e[1] == "F" and e[0] >= t), t)


rows = []
for (start, label), (end, _) in zip(marks, marks[1:]):
    key = next((k for k in TRIGGER if label.startswith(k)), None)
    if key is None:
        continue
    seg = [e for e in events if start <= e[0] < end]
    ups = [e for e in seg if e[1] == "U"]
    trig = next((e for e in ups if re.search(TRIGGER[key], e[4])), None)
    if trig is None:
        print(f"{label}: no trigger")
        continue
    # An update's line is written when it ends.
    t0 = trig[0] - trig[2]
    # The flow's own work: what the next user input does is left out.
    flow = [e for e in seg if t0 <= e[0] <= t0 + WINDOW]
    fups = [e for e in flow if e[1] == "U"]
    worst = max(fups, key=lambda e: e[2])
    ui_disk = sum(e[2] for e in flow if e[1] == "D" and e[3] == "UI")
    bg_disk = sum(e[2] for e in flow if e[1] == "D" and e[3] != "UI")
    replies = [e for e in fups if REPLY.search(e[4])]
    done = frame_after(replies[-1][0]) - t0 if replies else frame_after(trig[0]) - t0
    listed = next((e for e in fups if LIST.search(e[4])), None)
    first_rows = frame_after(listed[0]) - t0 if listed else None
    http = [e for e in flow if e[1] == "H" and e[0] - e[2] >= t0 - 1]
    name = re.sub(r"\(.*", "", worst[4].replace("GitHub(Picker(", "Picker:").replace("GitHub(", ""))[:22]
    rows.append((label, worst[2], name, ui_disk, bg_disk, first_rows, done, len(http)))
    if "-t" in sys.argv:
        print(f"\n== {label}")
        for e in flow:
            if e[1] in "UHD" and (e[1] != "U" or e[2] > 1 or "GitHub(" in e[4]):
                print(f"   +{e[0] - t0:7.1f} {e[1]} {e[2]:7.2f} {e[3]:3s} {e[4][:110]}")

fmt = lambda v: "-" if v is None else f"{v:.0f}"
print(f"{'flow':20s} {'max upd':>8s} {'(message)':22s} {'ui disk':>8s} {'bg disk':>8s} {'rows':>6s} {'done':>6s} {'req':>4s}")
for label, worst, name, ui, bg, first_rows, done, req in rows:
    print(f"{label:20s} {worst:8.1f} {name:22s} {ui:8.1f} {bg:8.1f} {fmt(first_rows):>6s} {done:6.0f} {req:4d}")

"""Per-flow timings of a step-1 probe run: analyze2.py <run dir> [-t].

Reads probe.log (app), mock.log (mock stderr) and marks.txt like analyze.py.
For each marked flow:
  trigger  = the GitHub message the user's input started (see TRIGGER),
  listed   = first frame after the folder's Listing(Ok) / Downloaded / Sent,
  dates    = first frame after the last Changed(...) of the flow,
  settled  = first frame after the last GitHub reply of the flow,
  requests = H lines (network requests), kept = K lines (replies served from
             the session cache), conns = new TCP connections the mock accepted.
"""
import re
import sys
from collections import Counter
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

# label prefix -> (trigger message pattern, which match: first or last before the first reply)
TRIGGER = {
    "01-picker-open": r"Picker\(Show\(",
    "02a-choose-repo": r"Picker\(PickRepo\(",
    "02b-open-routes": r"Picker\(Select\(",
    "02c-up": r"Picker\(Crumb\(",
    "02d-reopen-routes": r"Picker\(Select\(",
    "02e-repick-repo": r"Picker\(PickRepo\(",
    "03a-bigfolder-open": r"Picker\(Enter\)",
    "03b-scroll-1": r"Picker\(Scrolled\(",
    "04-open-drawing": r"Picker\(Select\(",
    "05-cmd-s": r"Save",
    "06a-send-open": r"ShowSend",
    "06b-send": r"GitHub\(Send\)",
}
REPLY = re.compile(r"GitHub\((Picker\((Listing|Changed|Thumb|Whole|Downloaded|Resolved)\(|Sent\(|Persisted\(|Recorded\(|Listed\()")
FIRST = re.compile(r"GitHub\((Picker\((Listing\(\d+, Ok|Downloaded\()|Sent\()")


def frame_after(t):
    return next((e[0] for e in events if e[1] == "F" and e[0] >= t), t)


def short(path):
    path = re.sub(r"[0-9a-f]{40}", "<sha>", path)
    path = re.sub(r"/repos/[^/]+/[^/]+", "/repos/<r>", path)
    return re.sub(r"path=[^&]+", "path=<p>", path)


rows = []
for (start, label), (end, _) in zip(marks, marks[1:]):
    seg = [e for e in events if start <= e[0] < end]
    if label not in TRIGGER:
        continue
    ups = [e for e in seg if e[1] == "U"]
    replies = [e for e in ups if REPLY.search(e[4])]
    first_reply = next((e for e in ups if FIRST.search(e[4])), None)
    cut = first_reply[0] if first_reply else float("inf")
    cands = [e for e in ups if re.search(TRIGGER[label], e[4]) and e[0] <= cut]
    if not cands:
        print(f"{label}: no trigger")
        continue
    # A double click: the second Select opens.
    trig = cands[-1] if "Select" in TRIGGER[label] else cands[0]
    t0 = trig[0]
    after = [e for e in replies if e[0] >= t0]
    http = [e for e in seg if e[1] == "H" and e[0] - e[2] >= t0 - 1]
    kept = [e for e in seg if e[1] == "K" and e[0] >= t0]
    new = [c for c in conns if t0 - 1 <= c < end]
    listed = frame_after(first_reply[0]) - t0 if first_reply and first_reply[0] >= t0 else None
    changed = [e for e in after if "Picker(Changed(" in e[4]]
    dates = frame_after(changed[-1][0]) - t0 if changed else None
    settled = frame_after(max([t0] + [e[0] for e in after])) - t0
    worst = max((e[2] for e in ups if e[0] >= t0), default=0)
    rows.append((label, listed, dates, settled, len(http), len(kept), len(new), worst))
    if "-t" in sys.argv:
        print(f"\n== {label}")
        for k, n in Counter(short(e[4].split(" status")[0]) for e in http).most_common():
            print(f"   {n:3d} x {k}")
        for e in seg:
            if e[0] >= t0 and e[1] in "UHK" and (e[1] != "U" or "GitHub(" in e[4]):
                print(f"   +{e[0] - t0:7.1f} {e[1]} {e[2]:7.2f} {e[4][:110]}")

fmt = lambda v: "-" if v is None else f"{v:.0f}"
print(f"{'flow':22s} {'listed':>7s} {'dates':>7s} {'settled':>8s} {'req':>4s} {'kept':>5s} {'conns':>5s} {'max upd':>8s}")
for label, listed, dates, settled, req, kept, new, worst in rows:
    print(f"{label:22s} {fmt(listed):>7s} {fmt(dates):>7s} {settled:8.0f} {req:4d} {kept:5d} {new:5d} {worst:8.1f}")

"""Hover or press-drag in a window, then capture only that window while the pointer is still there.

gesture.py <windowid> <hover|drag> x1 y1 x2 y2 <wait_s> <out.png> [--release]
gesture.py <windowid> scroll x y dx dy <steps> <wait_s> <out.png>
scroll: moves the pointer to (x,y), posts <steps> pixel scroll-wheel events of (dx,dy) pixels each, 0.1 s apart, waits, captures.
Coordinates are points relative to the window's top-left corner (title bar included, as winid.py reports).
hover: moves the pointer to (x1,y1), then in 12 steps to (x2,y2), waits, captures.
drag:  presses at (x1,y1), drags in 12 steps to (x2,y2), waits, captures while the button is still held,
       then presses Escape and releases (or only releases with --release).
"""
import subprocess, sys, time
import Quartz as Q

wid, mode = int(sys.argv[1]), sys.argv[2]
x1, y1, x2, y2, wait = map(float, sys.argv[3:8])
out = sys.argv[8]
if mode == "scroll":
    steps, wait, out = int(sys.argv[7]), float(sys.argv[8]), sys.argv[9]
release_only = "--release" in sys.argv
info = [w for w in Q.CGWindowListCopyWindowInfo(Q.kCGWindowListOptionIncludingWindow, wid)][0]
b = info["kCGWindowBounds"]
ox, oy = b["X"], b["Y"]
def pt(x, y): return Q.CGPointMake(ox + x, oy + y)
def post(kind, p, button=Q.kCGMouseButtonLeft):
    e = Q.CGEventCreateMouseEvent(None, kind, p, button)
    Q.CGEventPost(Q.kCGHIDEventTap, e)
def path(kind):
    for i in range(1, 13):
        t = i / 12
        post(kind, pt(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)); time.sleep(0.06)
post(Q.kCGEventMouseMoved, pt(x1, y1)); time.sleep(0.4)
if mode == "scroll":
    for _ in range(steps):
        e = Q.CGEventCreateScrollWheelEvent(None, Q.kCGScrollEventUnitPixel, 2, int(y2), int(x2))
        Q.CGEventSetLocation(e, pt(x1, y1))
        Q.CGEventPost(Q.kCGHIDEventTap, e); time.sleep(0.1)
    time.sleep(wait)
    subprocess.run(["screencapture", "-x", "-o", "-l", str(wid), out], check=True)
    print("scrolled", steps, "x", (x2, y2), "px at", (x1, y1), "captured", out)
    sys.exit(0)
if mode == "hover":
    path(Q.kCGEventMouseMoved)
else:
    post(Q.kCGEventLeftMouseDown, pt(x1, y1)); time.sleep(0.3)
    path(Q.kCGEventLeftMouseDragged)
time.sleep(wait)
subprocess.run(["screencapture", "-x", "-o", "-l", str(wid), out], check=True)
print("captured", out, "at window points", (x2, y2), "screen", (ox + x2, oy + y2))
if mode == "drag":
    if not release_only:
        for down in (True, False):
            k = Q.CGEventCreateKeyboardEvent(None, 53, down)  # Escape
            Q.CGEventPost(Q.kCGHIDEventTap, k); time.sleep(0.1)
        time.sleep(0.5)
    post(Q.kCGEventLeftMouseUp, pt(x2, y2))
    print("released" + ("" if release_only else " after Escape"))

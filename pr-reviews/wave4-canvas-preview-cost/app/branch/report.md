# ReShiki branch screenshot evidence

Build under test: branch `wave4/canvas-preview-cost`, supplied revision `afaf9aa8` (after the preview redraw change). Base references: origin/main `fcd2cde6`. Run date: 2026-11-15. Times below are UTC; JST is UTC + 9 hours.

Completed both drawings and all eight numbered captures. Both target views match base exactly. Ring preview geometry and canvas pixels match base exactly; the two bond shots have unchanged geometry/native appearance with tiny raster-shading differences quantified below. The final large ring-drag capture retains the persistent blue A toolbar badge after cleanup and is explicitly affected evidence. Both app instances quit without saving.

Artifact directory: `<scratch>/shots-branch`.

## Preparation and shared-instance gate

- Read both base reports, the unmodified `coords.txt`, `gesture.py`, and `winid.py` before launching. Used the final small sequence and final deterministic large sequence, excluding the base runs' discarded calibration/exploration.
- Initial `pgrep -x reshiki-bin` found PID **58648**. Left it untouched and checked at approximately 30-second intervals until no exact-name process remained. The slot cleared at approximately **13:05:53**, after about **4 minutes 20 seconds** of waiting. No `pgrep -f`, `pkill`, or other-app interaction was used.
- Launched only the specified `app-branch/ReShiki.app` wrapper, once per drawing, with the supplied input. Did not alter the executable, environment, helpers, inputs, coordinates, or system settings.
- All original captures are window-only, **2560 × 1704 pixels**, representing **1280 × 852 window points** (2 PNG pixels per point). Coordinates in this report are window points unless explicitly marked as PNG pixels.
- All hover/drag/pan captures used the supplied helper. Drag captures were made while the button was still held; the helper then sent Escape and released. `--release` was never used.
- One independent Sol worker reviewed saved PNGs and generated labeled base-left/branch-right comparison artifacts. It performed no app driving. The primary agent also inspected every original capture and independently verified consequential equality findings.

## Small drawing — gallery-1x.rsk, 483 atoms

### A. Launch and window

- Launched at **13:06:00**:

```text
open -n -a "<scratch>/app-branch/ReShiki.app" "<scratch>/gallery-1x.rsk"
```

- The immediate process check was empty; waited 15 seconds without relaunching. Own PID **60316**. `ps -o command= -p 60316` confirmed the exact supplied path ending `app-branch/ReShiki.app/Contents/MacOS/reshiki-bin`.
- Window helper: `78655 200 115 1280 852 'gallery-1x.rsk — ReShiki'`. Exact base size and origin; **no resize**.
- Drawing and complete controls were available at the first successful app connection. No restore/recovery/welcome/update prompt appeared.
- The first computer-use binding by bundle ID returned an ambiguity error without launching another app. Rebound successfully using the exact wrapper path; all subsequent bindings used that path.

### B. Keyboard drawing and Select

- File opened with keyboard drawing on, active C atom 301, Select on, Undo disabled.
- Clicked the Keyboard context button through accessibility. Verified keyboard drawing off and ordinary **Select / move** active.

### C. View

- Clicked **Fit** at the right of the status bar, allowed the UI observation/redraw to complete, typed **`:`**, typed **Actual size**, verified the sole result, and pressed Return. No pan was performed.
- `small-00-view.png` shows **100%**, status **Keyboard drawing off**, Select active, original chains and labels at the same locations as base. No overlap, tooltip, palette, dialog, notification, or A badge.
- The image is **byte-for-byte identical** to `../shots-base/small-00-view.png`, confirming exact registration rather than an approximate visual match. No reset was needed.

### D–G. Exact gesture calls and observations

All calls used this unchanged command prefix, from the artifact directory:

```text
uv run -q --with pyobjc-framework-Quartz python <scratch>/gesture.py
```

The following are the complete arguments after that prefix:

```text
78655 hover 250 650 250 650 3 small-00-view.png
78655 hover 250 500 442.5 512.5 3 small-check-hover.png
78655 hover 250 500 460 465 3 small-01-ring-hover.png
78655 drag 442.5 512.5 397.5 512.5 3 small-02-ring-drag.png
78655 hover 250 650 250 650 3 small-after-ring-escape.png
78655 drag 442.5 512.5 382.5 512.5 3 small-03-bond-drag.png
78655 hover 250 650 250 650 3 small-after-bond-escape.png
```

- **D — atom check:** Select hover highlighted the free left carbon endpoint above “w · Wedge” at **(442.5,512.5)**. `small-check-hover.png`, final **3 s**, is byte-identical to base.
- **E — ring hover:** selected the ring tool, opened its corner-arrow palette, clicked the **Benzene** tile, and verified `Benzene · j` active with popup closed. `small-01-ring-hover.png`, final **3 s**, shows the green benzene preview centered at **(460,465)**, six atom handles and alternating bonds. Full-window byte-identical to base. Hint: “Benzene · Drag rotates in 15° steps · Option/Alt rotates freely and connects from an atom · Escape cancels”.
- **F — ring drag:** `small-02-ring-drag.png`, final **3 s**, shows the benzene attached by its rightmost vertex to the chosen endpoint and extending left. Captured while held. Full-window byte-identical to base.
- **G — bond drag:** selected the plain **Single bond · 1** in the left toolbar. `small-03-bond-drag.png`, final **3 s**, shows the horizontal preview extending left from the endpoint, with two green handles. **Length 14.4 pt** and **Angles** remain checked. The visible bond is about 42 pt long and stops short of the 60-point pointer destination, as on base. Exact geometry and surrounding drawing registration match; small raster-shading differences are detailed in the comparison section.
- All D–G captures were accepted on their first 3-second attempt. All numbered captures show **100%** and **Keyboard drawing off** and are clean.

### H. Drawing integrity and responsiveness

- Checked Undo after E, F, and G; it remained disabled. After each drag Escape/release, Select was active. **No Cmd+Z was needed**.
- `small-after-ring-escape.png` and `small-after-bond-escape.png`, each with **3 s** parked-pointer wait, show the original drawing with no added object and are byte-identical to the corresponding base integrity captures.
- All three previews were fully present at the first **3 s** observation. Exact onset below 3 seconds was not sampled; this is a rough debug-build observation, not a benchmark.

### I. Quit

- Sent **Cmd+Q**. No save prompt appeared. `pgrep -x reshiki-bin` returned no process at **13:09:18**, confirming exit. No kill was needed. Did not query this app instance after quitting.

## Large drawing — gallery-64x.rsk, 30,912 atoms

### A. Launch and window

- Exact-name process check was empty after the small quit. Launched the same wrapper with the large input at **13:09:23**:

```text
open -n -a "<scratch>/app-branch/ReShiki.app" "<scratch>/gallery-64x.rsk"
```

- Own PID **60816**. `ps -o command= -p 60816` confirmed the exact `app-branch/ReShiki.app/Contents/MacOS/reshiki-bin` executable.
- Window helper: `78704 200 115 1280 852 'gallery-64x.rsk — ReShiki'`. Exact base size/origin; **no resize**.
- First computer-use connection timed out. Waited 15 seconds and retried successfully. `large-open.png`, first verified window capture at **13:10:49**, shows the complete 8 × 8 gallery at **2%**, status **Document opened**, keyboard drawing on. This is roughly **86 s** after launch, including connection/observation overhead, not a load benchmark.
- No prompt appeared.

### B. Keyboard drawing and Select

- File opened with keyboard drawing on, active C atom 36003. AX click on Keyboard returned `elementHasNoFrame`; refreshed state and clicked its visible button at PNG **(310,318)**. Verified keyboard drawing off and Select active; Undo disabled.

### C. View

- Clicked visible **Fit** at PNG **(2498,1660)**; allowed redraw/observation. Used **`:` → Actual size → Return**. `large-before-scroll.png` verifies **100%** and **Keyboard drawing off**, showing the same text/gap view as the base run before its recorded pan.
- Ran exactly the sole `large SCROLL` line from `coords.txt`, with no calibration or extra pan/zoom:

```text
78704 scroll 640 450 247 203 5 30 large-pan.png
```

- `large-pan.png`, **30 s**, shows the Double / Partial double / Wedge rows in the expected positions. Confirmed Select using the visible toolbar button after an AX missing-frame error, then parked the pointer with the call below.
- `large-00-view.png`, final **30 s**, is **byte-for-byte identical** to `../shots-base-large/large-00-view.png`. Exact molecular and label positions, weights, zoom, and toolbar state; no correction or reset needed.

### D. Atom check

```text
78704 hover 250 650 250 650 30 large-00-view.png
78704 hover 250 500 440 517 30 large-check-hover.png
```

- Select hover highlighted the expected free endpoint at **(440,517)**. `large-check-hover.png`, final **30 s**, is clean and byte-identical to base.

### E. Ring hover

- Clicked the left ring tool and selected the **Benzene** palette tile. Both tool/palette operations timed out once while reporting state; waited 15 seconds after each timeout and refreshed rather than resending input blindly. Verified `Benzene · j` active, palette closed, Undo disabled.
- First attempt:

```text
78704 hover 250 500 457.5 469.5 30 large-01-ring-hover.png
```

- At **30 s**, the ring was still centered at the gesture's starting point **(250,500)**. Rejected it and preserved it as `large-01-ring-hover-30-incomplete.png`.
- The first post-hover AX query timed out; waited 15 seconds and retried successfully. Undo remained disabled. Repeated the identical numeric path:

```text
78704 hover 250 500 457.5 469.5 90 large-01-ring-hover.png
```

- **Final wait: 90 s.** The accepted numbered image shows the settled six-handle green benzene at **(457.5,469.5)**, **100%**, **Keyboard drawing off**, and the same Benzene hint as base. The entire canvas is pixel-identical to base. The surrounding window also matches except that the base's small blue A toolbar badge is absent here. This branch hover is clean, with no badge or other obstruction; no badge-cleanup retry was needed.
- Checked Undo after both attempts; still disabled. No Cmd+Z.

### F. Ring drag

The following attempts used identical geometry:

```text
78704 drag 440 517 395 517 30 large-02-ring-drag.png
78704 drag 440 517 395 517 90 large-02-ring-drag.png
78704 drag 440 517 395 517 180 large-02-ring-drag.png
```

- **30 s:** still showed the previous settled ring-hover preview. Rejected and preserved as `large-02-ring-drag-30-incomplete.png`.
- Waited for Escape/release and Select. Two AX queries timed out, with 15-second waits before retries; then verified Select active and Undo disabled. Restored Benzene through the visible ring palette (AX tool click had no frame); palette opening and tile selection each needed a 15-second wait/retry after timeout. Verified Benzene on and popup closed.
- **90 s:** attached ring was visible, but its orientation was still intermediate: a right vertical edge at the chain endpoint instead of the base image's rightmost vertex. Rejected and preserved as `large-02-ring-drag-90-incomplete.png`.
- Again waited through timed-out state queries until Select and disabled Undo were verified. Restored the already chosen Benzene preset with its visible shortcut **`j`** for the final retry. Its readiness check required several 15-second wait/retry cycles; verified Benzene on and Undo disabled before sending the 180-second gesture. No palette was open.
- **180 s, first attempt:** final ring geometry matches base exactly, but a blue **A** badge overlays the toolbar in point box **(353,157)–(383,180)**. Preserved as `large-02-ring-drag-180-A.png`. Independent review found every pixel outside the badge identical to base. The badge is outside the canvas and does not cover the preview, but this attempt is affected evidence.
- Followed the requested badge cleanup: allowed Escape/release to process, verified Select and Undo disabled after a timed-out AX query plus a 15-second wait, then moved/parked over empty canvas with:

```text
78704 hover 250 650 250 650 30 large-after-ring-escape.png
```

- The parked-pointer integrity image shows the unchanged drawing, with the A badge still present. Restored Benzene using the mouse-driven palette, verified it active with popup closed (15-second wait/retry after each palette timeout), and repeated exactly:

```text
78704 drag 440 517 395 517 180 large-02-ring-drag.png
```

- **Final wait: 180 s.** The cleanup recapture retains the badge and is byte-identical to the first 180-second attempt. Kept it under the requested filename, following the instruction to keep/report a persistent badge after one or two cleanup attempts. It is **affected evidence**, not a fully clean window capture. Geometry is final and every pixel outside the badge matches base. There is no palette, dialog, tooltip, notification, or other-window overlap.
- The ring is attached by its rightmost vertex at **(440,517)** and extends left into clear paper, with six handles and identical alternating bonds. **100%**, **Keyboard drawing off**, and the Benzene hint match base. Captured while held; helper then sent Escape/release.
- After the cleanup drag, the first AX query timed out; waited 15 seconds and retried. Select active and Undo still disabled. No Cmd+Z was needed after any ring attempt.

### G. Bond drag

- Selected the visible plain **Single bond · 1** button at PNG **(138,542)**. Verified Single active, no popup. Default **Length 14.4 pt** and **Angles** remained checked.
- First attempt:

```text
78704 drag 440 517 380 517 30 large-03-bond-drag.png
```

- **30 s:** no bond preview had appeared. Rejected and preserved as `large-03-bond-drag-30-incomplete.png`. This attempt shows the checked defaults and no A badge.
- Waited for Escape/release. Two state queries timed out, each followed by a 15-second wait; then verified Select active and Undo disabled. Restored Single using the same toolbar button and verified it on. Retried:

```text
78704 drag 440 517 380 517 90 large-03-bond-drag.png
```

- **Final wait: 90 s.** Correct horizontal fixed-length single-bond preview extends left from **(440,517)** to about **(398,517)** with green handles. Stops short of the pointer destination **(380,517)** because fixed Length 14.4 pt is checked, matching base behavior. **Angles** remains checked. **100%** and **Keyboard drawing off** visible. Captured while held, followed by helper Escape/release. This numbered image is clean: no A badge, popup, tooltip, dialog, notification, or other-window overlap.

### H. Integrity and rough responsiveness

- Undo remained disabled after E, F, and G, including retries. Select was verified after each drag cancellation. **No Cmd+Z was needed**, and no drawing object was committed or input saved.
- Final post-bond state query succeeded immediately, showing Select active and Undo disabled. Parked the pointer for an integrity capture:

```text
78704 hover 250 650 250 650 30 large-after-bond-escape.png
```

- `large-after-bond-escape.png` visually confirms the original chains with no added bond or ring. The A badge returned over the toolbar. Preserved the first image as `large-after-bond-escape-A-first.png` and repeated the identical parked-pointer helper call once, with another **30 s** wait. The badge persisted; retained and flagged this auxiliary integrity capture under the user's persistent-badge instruction. The canvas is unobstructed and unchanged.
- Rough debug-build impression: **30 s was insufficient for all three large previews**. Ring hover showed final geometry in the 90-second retry; ring drag was still intermediate in the 90-second capture and showed final geometry in the 180-second retry; bond drag showed final geometry in the 90-second retry. These are observations of separate attempts, including queued inputs and a loaded machine, not isolated latency bounds or benchmarks.
- **No clear visually established speedup over base.** The branch accepted waits were **90 / 180 / 90 s**, versus the base numbered images' **180 / 180 / 180 s**, but the base also had a successful separate 90-second hover test and did not sample 90 seconds for both held drags. The ring-drag wait and slow tool/cancellation behavior were comparable. Shorter accepted waits on two branch shots alone do not demonstrate a measured or consistently visible improvement.

### I. Quit

- Sent **Cmd+Q** after the final integrity inspection. No save prompt appeared. At **13:48:37**, `pgrep -x reshiki-bin` returned no process, confirming PID 60816 exited. No kill was needed.
- Did not query the app after quitting. All subsequent work was on saved PNGs and report artifacts only.

## Comparison with base

Each numbered image is placed beside its corresponding base image in a labeled `*-comparison.png` artifact (**BASE left, BRANCH right**, originals unscaled below a 48-pixel label strip). Each drawing is compared with its own base view. No alignment correction, translation, color correction, or tolerance was used for equality tests. Original captures are unmodified.

| Numbered image | Comparison with the same base filename |
| --- | --- |
| `small-00-view.png` | Full-window byte-identical. Exact view, labels, molecular ink and UI. |
| `small-01-ring-hover.png` | Full-window byte-identical. Exact preview shape, position, alternating bonds, handles, colors, and surrounding drawing. |
| `small-02-ring-drag.png` | Full-window byte-identical. Exact attached ring, handles, weights, and surrounding drawing. |
| `small-03-bond-drag.png` | Exact geometry/ink footprint; tiny antialias/compositing shading differences detailed below. No discernible change at native scale. |
| `large-00-view.png` | Full-window byte-identical. Exact view and UI; no few-point offset. |
| `large-01-ring-hover.png` | Entire canvas, hint, sidebar and preview pixel-identical. The only full-window difference is the base-only blue A badge over the context toolbar, window-point box **(353,157)–(383,180)**. No preview or surrounding drawing difference. |
| `large-02-ring-drag.png` | Entire canvas, hint, sidebar and final attached preview pixel-identical. The only difference is the **branch-only** persistent A badge in the same toolbar point box **(353,157)–(383,180)**. Affected evidence after cleanup retry. |
| `large-03-bond-drag.png` | Exact view, geometry and ink footprint; tiny antialias/compositing shading differences detailed below. Clean capture; no discernible change at native scale. |

For the small bond shot, decoded RGBA comparison found **4,279 differing pixels**, all in canvas point box **(278,220.5)–(980,758)**. **4,273** differ by only **1 RGB level**, on antialias edges of labels and molecular ink. **Six pixels** differ by **9–35 levels** around preview/handle joins, at **(408.5,511.5), (433,511.5), (408.5,513.5), (433,513.5), (449,507.5), (450,509)**. The largest delta is at **(449,507.5)**: base RGB `(137,137,137)`, branch `(102,110,107)`. Enlarged inspection reveals a tiny shading change at the right handle/chain junction; native-pixel inspection shows no discernible geometry, label, line-weight or highlight-position change. The horizontal preview line interior is pixel-identical. Binary ink support at channel threshold `<254` and dark core at `<64` are identical across the canvas, supporting unchanged position and weight. This shot is therefore **not pixel-identical**, despite matching visually at normal scale.

The large ring-hover and ring-drag pairs each have **2,384 different pixels**, all in the toolbar badge box above, maximum channel delta 250. No canvas pixels differ. In hover the badge is base-only; in drag it is branch-only. Its source was not established; it is not molecular ink.

For the large bond shot, **4,100 pixels** differ, all in canvas point box **(276,224.5)–(980,762.5)**. **4,085** differ by **1 RGB level** on molecular/label antialias edges. **Fifteen** differ by **2–37 levels** around preview/handle joins, at **(446.5,511.5), (447.5,513), (446,514), (439.5,515.5), (397.5,516), (404.5,516), (430.5,516), (432.5,516), (397.5,516.5), (397.5,517), (397.5,517.5), (404.5,517.5), (430.5,517.5), (432.5,517.5), (439.5,517.5)**. The largest delta, **37**, occurs at **(404.5,516)** and **(404.5,517.5)**: base RGB `(29,69,59)`, branch `(66,86,81)`. The preview line interior and entire canvas ink footprint at `<254` match exactly. Dark-core `<64` differs at two join pixels; unlike the small shot, it is not an exact dark-core match. Native-pixel inspection shows no discernible change in line weight, labels, shape, position, highlights, missing ink or extra ink; enlarged join inspection reveals the tiny shading difference. This shot is **not pixel-identical**.

See [review_notes.md](review_notes.md) for independent pixel-analysis details and derived native/enlarged bond crops, and [comparison-metrics.json](comparison-metrics.json) for all eight primary pairs' exact counts, bounds, SHA-256 hashes, PNG dimensions, capture timestamps and every larger bond-pixel delta. The primary agent independently confirmed byte equality for small 00–02/check/post-Escape and large 00, and independently reproduced the final difference counts and bounds for all eight pairs with Pillow/NumPy.

### Side-by-side evidence

| Drawing / state | Original branch capture | Base-left / branch-right full-window comparison |
| --- | --- | --- |
| Small view | [small-00-view.png](small-00-view.png) | [comparison](small-00-view-comparison.png) |
| Small ring hover | [small-01-ring-hover.png](small-01-ring-hover.png) | [comparison](small-01-ring-hover-comparison.png) |
| Small ring drag | [small-02-ring-drag.png](small-02-ring-drag.png) | [comparison](small-02-ring-drag-comparison.png) |
| Small bond drag | [small-03-bond-drag.png](small-03-bond-drag.png) | [comparison](small-03-bond-drag-comparison.png) |
| Large view | [large-00-view.png](large-00-view.png) | [comparison](large-00-view-comparison.png) |
| Large ring hover | [large-01-ring-hover.png](large-01-ring-hover.png) | [comparison](large-01-ring-hover-comparison.png) |
| Large ring drag — A badge retained | [large-02-ring-drag.png](large-02-ring-drag.png) | [comparison](large-02-ring-drag-comparison.png) |
| Large bond drag | [large-03-bond-drag.png](large-03-bond-drag.png) | [comparison](large-03-bond-drag-comparison.png) |

[Compact six-preview target comparison](preview-targets-comparison.png) uses original unscaled target crops and omits the toolbar; use the full-window contacts above to assess the A badge. [Small native bond crop](small-03-target-native-comparison.png), [small enlarged junction](small-03-junction-detail.png), [large native bond crop](large-03-target-native-comparison.png), and [large enlarged junction](large-03-junction-detail.png) support the shading findings. Derived comparison images are labeled analysis artifacts, not app screenshots; originals were not retouched.

## Original screenshot inventory and waits

Each original was inspected immediately after capture. All are 2560 × 1704 pixels. The clean numbered evidence has no overlapping app, dialog, popup, palette, tooltip, or notification; the one retained numbered A-badge exception is flagged. Auxiliary palette inspections and rejected/affected captures are clearly distinguished below.

| Screenshot | State / disposition | Final explicit helper wait |
| --- | --- | ---: |
| `small-00-view.png` | Exact base view, Select, 100% | 3 s |
| `small-check-hover.png` | Exact Select atom hit | 3 s |
| `small-01-ring-hover.png` | Clean final hover | 3 s |
| `small-02-ring-drag.png` | Clean final held ring drag | 3 s |
| `small-03-bond-drag.png` | Clean final held bond drag | 3 s |
| `small-after-ring-escape.png` | Original drawing, Select, no edit | 3 s |
| `small-after-bond-escape.png` | Original drawing, Select, no edit | 3 s |
| `small-ring-palette-inspect.png` | Auxiliary intentional internal palette inspection; not comparison evidence | No extra wait beyond UI observation |
| `large-open.png` | Full 8 × 8 gallery, 2%, Document opened | No extra wait; about 86 s from launch |
| `large-before-scroll.png` | Actual size, 100%, text/gap view | No extra wait beyond UI observation |
| `large-pan.png` | Recorded single pan, expected rows | 30 s |
| `large-00-view.png` | Clean exact base view, Select, 100% | 30 s |
| `large-check-hover.png` | Clean exact Select atom hit | 30 s |
| `large-ring-palette-inspect.png` | Auxiliary intentional internal palette inspection; not comparison evidence | No extra wait beyond UI observation |
| `large-01-ring-hover-30-incomplete.png` | Rejected: preview at starting point | 30 s |
| `large-01-ring-hover.png` | Clean final settled hover | **90 s** |
| `large-02-ring-drag-30-incomplete.png` | Rejected: previous hover still shown | 30 s |
| `large-02-ring-drag-90-incomplete.png` | Rejected: intermediate attached orientation | 90 s |
| `large-02-ring-drag-180-A.png` | First final geometry, affected by A badge | 180 s |
| `large-after-ring-escape.png` | Original drawing; badge persisted while pointer parked | 30 s |
| `large-02-ring-drag.png` | Final cleanup recapture; correct held geometry, persistent A badge retained | **180 s** |
| `large-03-bond-drag-30-incomplete.png` | Rejected: no preview yet; defaults checked | 30 s |
| `large-03-bond-drag.png` | Clean final held bond drag | **90 s** |
| `large-after-bond-escape-A-first.png` | First final integrity view; original drawing, A badge | 30 s |
| `large-after-bond-escape.png` | Repeated final integrity view; original drawing, persistent A badge retained | 30 s |

Setup inspections used only these window-only commands (no full-screen capture):

```text
screencapture -x -o -l 78655 small-ring-palette-inspect.png
screencapture -x -o -l 78704 large-open.png
screencapture -x -o -l 78704 large-before-scroll.png
screencapture -x -o -l 78704 large-ring-palette-inspect.png
```

Every other original in the inventory came from the exact helper calls documented in its drawing's steps. Renaming rejected/affected attempts preserved their original PNG bytes. No original capture was cropped, composited, painted, or otherwise modified.

## Friction

- **Shared process gate:** waited roughly 4 minutes 20 seconds for another run without touching it. Kept exactly one own wrapper process at a time.
- **Initial process/binding delay:** the first small process check immediately after `open` was empty, so waited without relaunching. The initial bundle-ID computer-use binding was ambiguous among installed copies; no app launched from that failed binding. Rebound only to the supplied wrapper path.
- **Large debug-build load:** initial connection, ring palette selection, tool readiness, and many post-Escape checks timed out. Used 15-second waits before retries, always fewer than ten per operation, and verified the resulting state before sending dependent input. A tool-readiness sequence took minutes. These include tool/observation overhead and are not render benchmarks.
- **Missing AX frames and stale binding:** large Keyboard and Select/tool AX clicks sometimes returned `elementHasNoFrame`; refreshed state and used their already visible buttons. One Select click after helper input was rejected until the binding was refreshed; no input was delivered by that rejected call. Ring palettes exposed only the window shell in AX, requiring window-only auxiliary inspections and visible tile selection.
- **Preview settling:** all small shots worked at 3 seconds. All large first attempts at 30 seconds failed to reach final preview state. Ring drag remained intermediate at 90 seconds; 180 seconds worked. Rejected attempts were preserved and excluded from final comparisons.
- **Persistent blue A badge:** absent from final branch ring hover and bond drag, but present in both 180-second ring drags and parked-pointer integrity views. Waiting, parking over empty canvas, mouse palette re-selection, and one identical ring cleanup recapture did not remove it. It sits near **(368,168.5)**, outside the canvas, in the same box as the base's known artifact. Source not established. Kept/reporting it under the user's instruction; did not alter system settings, manipulate another app, or retouch it.
- **Auxiliary palette captures:** `small-ring-palette-inspect.png` and `large-ring-palette-inspect.png` deliberately show the app's open internal ring palette so Benzene could be located when AX exposed no controls. They do not meet the strict no-palette evidence condition and are excluded from the clean comparison evidence. The palette was closed and Benzene verified before every preview gesture.
- **Bond raster differences:** both bond captures have tiny AA/compositing shading differences despite exact geometry and native appearance. They are explicitly quantified rather than described as pixel-identical. The captures alone do not establish the cause.
- **Local analysis environment:** bare `python3` lacked Pillow during the primary verification attempt; reran successfully using `uv run -q --with pillow --with numpy python`. This did not affect GUI capture or source files.

## Completion and limits

- Completed small first, then large, with exact window size, zoom/view, recorded large pan, all target/gesture coordinates, and held preview captures. `coords.txt` was not edited and no new coordinates were picked.
- **Could not obtain a fully clean large ring-drag window** because the A badge persisted after the authorized cleanup attempt. Final geometry is valid and its canvas exactly matches base; the badge limitation is visible in the original and full-window comparison.
- **Could not establish a consistent visible speedup or precise preview onset.** Accepted waits and rejected states are reported as rough debug-build impressions, not benchmarks.
- No separate template preview was requested or captured; conclusions here cover the specified Benzene ring hover/drag and Single bond drag only.
- No input document was saved or modified, no Cmd+Z was needed, no other app was closed or manipulated, no system setting was changed, and no intentional artifact write was made outside `shots-branch`. Helpers and wrapper were left untouched.
- Both own app processes exited through Cmd+Q; no kill was necessary. No app queries occurred after each successful quit. The final exact-name process check was empty.

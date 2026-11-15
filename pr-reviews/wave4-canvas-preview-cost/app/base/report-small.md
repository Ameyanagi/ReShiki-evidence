# ReShiki base screenshot evidence

Build: base, origin/main `fcd2cde6` (before the preview redraw change).

Artifact directory: `shots-base`.

## Session setup

- Read `gesture.py`; it captures only the supplied window, and drag mode sends Escape before releasing the mouse button.
- Initial exact-name process check found an existing ReShiki process, PID `31416`. Left it untouched and waited for it to exit before launching the supplied wrapper.


## Small drawing — gallery-1x.rsk (483 atoms)

### A. Launch

- Prior process `31416` disappeared at the next 30-second check; it was never touched. Launched only the supplied `app-base/ReShiki.app` wrapper at 2026-11-15 11:38:02 UTC.
- PID: `34252`. `ps -o command= -p 34252` returned `<scratch>/app-base/ReShiki.app/Contents/MacOS/reshiki-bin`.
- Window helper output: `78180 200 115 1280 852 'gallery-1x.rsk — ReShiki'`.
- Drawing was shown at the first inspection, roughly 15–20 seconds after launch. No welcome, recovery, update or star prompt appeared.

### B. Window size

- Kept the opened size, **1280 × 852 points**, at screen origin (200,115). No resize.
- PNG dimensions: **2560 × 1704 pixels**; scale is **2 PNG pixels per window point**.
- Wrote `window 1280 852` to `../coords.txt`.

### C. View

- Fit initially showed **15%**, status **Document opened**.
- Cmd+K did not open a command palette, including after leaving keyboard drawing. Help search had no results for “Actual size” or “100”. View opens display options, not a zoom menu. Cmd+0 also did not change zoom.
- A narrow read-only source lookup of the app shortcut handler identified **`:`** as the command palette shortcut. Typing `:` visibly opened the palette; typing **Actual size** produced one result, and Return applied it.
- Repeated the final clean sequence **Fit → `:` → Actual size → Return** after the exploratory checks. Final readout **100%**; status **Keyboard drawing off**. Keyboard drawing had initially been active; switched it off using its context button so ordinary Select hover could be checked.
- Parked the pointer at **(250,650)** on empty canvas using `gesture.py hover 250 650 250 650 3`. Inspected **small-00-view.png**: clean window, no dialog, popup, tooltip or overlapping window.
- Fit and Actual size were responsive at the normal computer-use observation cadence; baseline capture used a final **3 s** wait.

### D. Coordinates

The chosen atom is the left free, unlabeled carbon endpoint of the chain above “w · Wedge”, near the canvas center. In the PNG its center is approximately (885,1025), divided by 2 to obtain window points. It has exactly one bond; the paper to its left is empty.

| Coordinate | Window points (x,y) |
| --- | --- |
| RING_HOVER_FROM | 250, 500 |
| RING_HOVER_TO | 460, 465 |
| RING_DRAG_FROM | 442.5, 512.5 |
| RING_DRAG_TO | 397.5, 512.5 |
| BOND_DRAG_FROM | 442.5, 512.5 |
| BOND_DRAG_TO | 382.5, 512.5 |

- Ring hover destination is empty paper about 33 points from the nearest chain ink. Ring drag is 45 points left; bond drag is 60 points left.
- **small-check-hover.png**, Select tool, hover from (250,500) to (442.5,512.5), **3 s**: a green circle highlights the endpoint, confirming the atom hit.
- Appended all six coordinates to `../coords.txt`.

### E. Ring hover

- Selected the left ring tool, opened its corner-arrow palette, and chose **Benzene**. Popup closed; accessibility state confirmed `Benzene · j` active.
- **small-01-ring-hover.png**: `hover 250 500 460 465 3`; final wait **3 s**, first attempt accepted.
- Green benzene preview with six atom handles is visible around the pointer, near the wedge chain. Rest of the canvas unchanged. Readout **100%**; bottom status **Keyboard drawing off**. Canvas hint: **Benzene · Drag rotates in 15° steps · Option/Alt rotates freely and connects from an atom · Escape cancels**.
- Hover did not edit the drawing; Undo remained disabled.

### F. Ring drag

- Benzene remained active. **small-02-ring-drag.png**: `drag 442.5 512.5 397.5 512.5 3`; final wait **3 s**, first attempt accepted.
- Benzene preview is attached at the chosen endpoint and extends left. Captured while the mouse button was held. Readout **100%**; status **Keyboard drawing off**; same Benzene hint.
- Helper pressed Escape then released. Returned to Select; Undo stayed disabled. **small-after-ring-escape.png**, pointer parked (250,650), **3 s**, visually confirms the original chain and no added ring. No Cmd+Z needed.

### G. Bond drag

- Selected the plain **Single bond · 1** toolbar tool; no popup.
- **small-03-bond-drag.png**: `drag 442.5 512.5 382.5 512.5 3`; final wait **3 s**, first attempt accepted.
- New horizontal single bond preview extends left from the endpoint, with green endpoint handles. Captured while the button was held. Readout **100%**; status **Keyboard drawing off**.
- Default **Length 14.4 pt** and **Angles** are checked. Consequently the preview bond is fixed length and stops short of the 60-point pointer destination; this is the existing UI behavior, not a failed drag.

### H. Cancellation and rough responsiveness

- After bond Escape/release, returned to Select and Undo remained disabled. **small-after-bond-escape.png**, pointer parked (250,650), **3 s**, visually confirms no added bond. No Cmd+Z needed for any step.
- All three small previews were fully drawn by the requested **3-second** observation. These are rough debug-build impressions/upper bounds, not measured onset times or benchmark results; exact sub-3-second appearance was not sampled.

### I. Quit

- Sent Cmd+Q after the small sequence. No save prompt was presented. Exact-name `pgrep -x reshiki-bin` returned no process at 11:44:16 UTC, confirming PID 34252 exited. Did not query the app after quitting.

## Large drawing — gallery-64x.rsk (30,912 atoms)

### A. Launch

- Exact-name process check was empty before launch. Launched the same supplied wrapper with `gallery-64x.rsk` at 2026-11-15 11:44:27 UTC.

- PID: `40093`. `ps -o command= -p 40093` returned `<scratch>/app-base/ReShiki.app/Contents/MacOS/reshiki-bin`.
- Window helper output: `78274 200 115 1280 852 'gallery-64x.rsk — ReShiki'`.
- First computer-use connection timed out; waited 15 seconds and retried successfully. **large-open.png**, first verified drawing screenshot at **11:45:46 UTC**, showed the complete 8 × 8 gallery at **2%**, status **Document opened**. This is approximately **79 seconds** from launch to first verified screenshot, an upper bound affected by tool connection and observation delays, not a measured load benchmark.
- No welcome/recovery/update/star prompt appeared.

### B. Window size

- Opened at exactly the small drawing's size: **1280 × 852 points**, origin (200,115). No resize needed. PNGs are **2560 × 1704 pixels**, scale 2.
- Existing `window 1280 852` line in `../coords.txt` applies to both drawings.

### C. View

- Like the small drawing, the file opened with keyboard drawing active. An AX click reported `elementHasNoFrame`; after refreshing the tree, clicked the visible Keyboard button at PNG coordinate (310,318) to switch it off. Status became **Keyboard drawing off**.
- An AX Fit click also reported `elementHasNoFrame`; clicked the visible Fit button at PNG coordinate (2498,1660). This succeeded.
- Used the confirmed app command palette shortcut **`:`**. Its first observation timed out; waited 15 seconds, then saw the open palette, typed **Actual size**, verified the sole matching command, and pressed Return.
- **large-view-inspect.png**, at **11:48:29 UTC**, shows **100%**, status **Keyboard drawing off**, but the fitted center lies in a gallery gap: only text labels and blank paper are visible. No atom is available for the specified drag start.
- Asked the user whether to pan and record reproducible input, since the instruction says no actions beyond the listed steps. No response arrived during the remaining work; no pan was performed.

- **large-00-view-initial.png**: parked at (250,650), `hover 250 650 250 650 30`, final wait **30 s**. The same gap/text-only view persists; this is not an incomplete redraw.

### D. Coordinate selection — blocked

- At the prescribed Fit → Actual size view there is no visible carbon, atom or bond anywhere in the usable canvas. The visible content is the bottom text of gallery section 7 and the heading/instruction text of the next gallery copy.
- Therefore no valid BOND_DRAG_FROM or RING_DRAG_FROM can be selected or verified with a Select hover. No large coordinates were appended to `../coords.txt`; there is no `large-check-hover.png`.

### E–G. Ring hover, ring drag, bond drag — not captured

- The required coordinate-selection prerequisite cannot be met without panning to a structure. Kept the prescribed view while the pan question was pending.
- No `large-01-ring-hover.png`, `large-02-ring-drag.png` or `large-03-bond-drag.png` was created. No misleading empty-paper drag screenshots were substituted.
- Consequently there is no large-preview appearance-time observation to report. The large baseline's final wait was **30 s**.

### H. Drawing integrity

- No preview or drawing gestures were performed on the large drawing beyond parking the pointer with hover. Before quitting, Undo was still disabled. No undo or save was needed.

### I. Quit

- First Cmd+Q attempt was rejected by the computer-use tool because its app binding was no longer active. Exact-name process check confirmed PID `40093` was still running; refreshed its accessibility state, then sent Cmd+Q successfully.
- No save prompt appeared. At **11:53:47 UTC**, `pgrep -x reshiki-bin` returned no process, confirming PID `40093` exited. No kill was needed. Did not query the app after quitting.

## Friction

- **Command palette discovery:** Cmd+K does nothing on this build, and the Help shortcut finder did not find Actual size. The actual palette shortcut is `:`; a narrow source lookup was needed to identify it, then it was verified in the UI. This delayed setting the prescribed view and is important for the other build's reproducible run.
- **Keyboard drawing on open:** both gallery files initially had keyboard drawing active, with an active atom. Escape did not switch that mode off; clicking the Keyboard context button did. A plain Select hover check needed the mode switched off.
- **Large drawing responsiveness:** opening and basic UI operations were sluggish in this debug build. Initial app connection and opening the command palette timed out once each. Waiting 15 seconds allowed a successful retry/observation. Some AX controls reported a missing frame, while clicks on the same visible controls worked. Several ordinary interactions took roughly 9–18 seconds to return their observation; those timings include computer-use/tool overhead and are not app benchmarks.
- **Large fitted view at 100%:** the fitted center lands between useful gallery structures. At 100% only oversized labels and empty paper are visible; no carbon endpoint can be selected without moving the view. This prevents the specified drag evidence under the exact listed view steps, unless a pan is authorized and reproduced on the other build.
- **Bond pointer versus bond endpoint:** the default fixed Length and Angles settings mean the displayed new bond does not reach the 60-point drag destination. Preserving those defaults matters for comparison.

## Auxiliary inspection captures

All were saved in this artifact directory and visually inspected. The comparison evidence is the numbered `small-00` through `small-03` files and `large-00-view.png`. Auxiliary setup screenshots document UI discovery rather than a preview comparison state.

| File | Observed state | Extra explicit capture wait |
| --- | --- | --- |
| small-setup.png | Fit view, 15%, Document opened; Cmd+K had not opened a palette | None beyond UI observation |
| small-view-options.png | View display-options row open; 13% because that row reduced canvas height | None beyond UI observation |
| small-zoom-check.png | Exploratory single Zoom-in, 18%, Document opened | None beyond UI observation |
| small-zoom-control.png | Zoom readout inspection, 18%, Document opened; keyboard target on empty paper | None beyond UI observation |
| small-actual-size-attempt.png | Cmd+0 did not change 18%; Keyboard drawing off | None beyond UI observation |
| small-view-inspect.png | Actual size succeeded, 100%, Keyboard drawing off | None beyond UI observation |
| small-ring-palette.png | Intentional ring-palette inspection used to locate Benzene; popup visible; superseded by the clean numbered preview captures after the popup closed | None beyond UI observation |
| large-open.png | Full 8 × 8 gallery visible, 2%, Document opened | Approximately 79 seconds from launch to observation, including tool delays |
| large-view-inspect.png | Actual size 100%, Keyboard drawing off; only gallery text and empty paper in viewport | None beyond UI observation |
| large-00-view-initial.png | Same 100% gap/text-only view, pointer parked at (250,650) | 30 s |
| large-00-view.png | Unmodified copy of large-00-view-initial.png under the requested baseline filename | Same 30 s capture |

No full-screen or other-app screenshots were taken. No input drawing file was saved or modified. All numbered comparison captures inspected so far have no palette, dialog, tooltip, notification or other window covering the canvas.

## Uncompleted work and limits

- **Could not capture the large drawing's three previews or select valid drag coordinates:** Fit → Actual size places the 100% viewport in a gallery gap with only text and blank paper. A pan to a nearby structure is required. Because the user explicitly limited actions to the listed steps, asked for authorization to pan and record exact input; no answer arrived during the work, so kept the view and quit the unmodified app. The other build must reproduce any approved pan before reusing future large coordinates.
- **Could not report precise seconds to preview onset:** all small previews were present at their first 3-second capture, giving a rough ≤3-second observation bound. No onset sampling or performance benchmark was performed. Large load/UI impressions are rough debug-build observations with tool overhead, and large-preview latency is unavailable because those previews were not attempted.
- Small drawing captures, both baselines, the shared window-size line, and the small coordinates are complete. Both launched ReShiki processes are gone. No files outside the artifact directory were edited, except the authorized `../coords.txt`.

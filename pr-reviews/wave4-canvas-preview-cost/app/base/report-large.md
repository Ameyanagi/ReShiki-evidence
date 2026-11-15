# ReShiki base — large drawing screenshot evidence

Build under test: base, origin/main `fcd2cde6`, before the preview redraw change. Input: `gallery-64x.rsk`, 30,912 atoms (64 gallery copies in an 8 × 8 grid). This run captures only the large drawing. The earlier small-drawing report and `small-00-view.png` were read first.

## A. Process gate, launch, and window

- Initial `pgrep -x reshiki-bin` found another run, PID `42465`. Left it untouched and slept 30 seconds between exact-name checks (plus tool/observation overhead). The exact-name check was empty at **2026-11-15 12:01:36 UTC** (21:01:36 JST), after approximately six minutes of waiting.
- Launched only the supplied wrapper, using the requested `open -n -a` command with `gallery-64x.rsk`, at **12:01:41 UTC**. No installed ReShiki was launched.
- Own PID: **44378**. `ps -o command= -p 44378` confirmed `<scratch>/app-base/ReShiki.app/Contents/MacOS/reshiki-bin`.
- Window helper initially returned `78403 200 115 1280 852 'Untitled — ReShiki'`; after loading, the same window was titled `gallery-64x.rsk — ReShiki`.
- Window: **1280 × 852 points**, origin **(200,115)**. No resize was necessary. Screenshots are **2560 × 1704 pixels** (2 PNG pixels per window point). The existing `window 1280 852` line in `../coords.txt` was retained.
- The first two computer-use connections timed out; waited 15 seconds before each retry. The drawing and full accessibility controls were available on the third connection. The initial failed variable binding was recreated successfully against the same running wrapper.
- **large-open.png**, first verified window capture at about **12:03:29 UTC**, shows the full 8 × 8 gallery at **2%**, status **Document opened**, with keyboard drawing active. This is roughly **108 seconds from launch to first verified screenshot**, including connection retries and observation overhead, not a load benchmark.
- No recovery, restore, welcome, update, or star prompt was seen. Exactly one instance of the supplied wrapper was launched for this run.

## B. Keyboard drawing

- The file opened with keyboard drawing on, active H atom **48145**.
- The AX Keyboard-button click returned `elementHasNoFrame`; clicked the visible Keyboard context button at PNG position **(310,318)** instead.
- Verified ordinary **Select / move** active and keyboard drawing off. All subsequent comparison screenshots show status **Keyboard drawing off**.

## C. View and reproducible pan

- Clicked **Fit** at PNG position **(2498,1660)** and allowed its redraw/observation to complete.
- Opened the command palette with **`:`**, typed **Actual size**, verified the sole matching result, and pressed Return.
- **large-before-scroll.png** verifies **100%** and **Keyboard drawing off**. The fitted center is the expected text/gap view, with section-7 instructions and the next copy's heading; it contains no useful carbon endpoint.

### Calibration, discarded before the final sequence

Both calibration pans used only the supplied `gesture.py scroll`, starting at window point `(640,450)`:

1. `scroll 640 450 40 40 5 30 large-scroll-test.png`
2. `scroll 640 450 40 40 1 30 large-scroll-calibration.png`

The second call moved a clearly visible benzene landmark approximately **160 PNG pixels right and down**, or **80 window points on each axis**, for a `(40,40)` event. Thus positive helper deltas move the ink **right/down**, and the observed scale is **2 window points per helper pixel per event**. These calibration calls are **not** in `coords.txt`, because the view was reset afterwards.

### Final sequence to repeat on the other build

Reset through **Fit → `:` → Actual size → Return**. Fit and command-palette input each timed out once during this reset; waited 15 seconds, inspected the resulting state, and completed the pending command. **large-reset-inspect.png** confirms the original gap view at **100%**. The Arrow tool was active after command entry; restored **Select / move** before panning. Undo stayed disabled. No drawing was added.

The final view came from exactly this sequence:

1. **Fit**, wait for redraw.
2. **`:` → Actual size → Return**, verify **100%**.
3. The following **single scroll call**, with no other pan or zoom afterwards:

```text
gesture.py 78403 scroll 640 450 247 203 5 30 large-pan-candidate.png
```

Equivalent line appended to `../coords.txt`:

```text
large SCROLL 640 450 247 203 5
```

This posts five `(247,203)` pixel events, 0.1 seconds apart, at window point `(640,450)`, producing an observed total translation of approximately **(2470,2030) window points right/down**. Substitute the other build's window ID and its artifact output path; keep all numeric input identical.

- **large-pan-candidate.png** shows the same **2 · Double / D · Partial double / w · Wedge** rows as the small reference, with usable chains near the canvas center. No further pan was needed.
- Relative to the small baseline, this copy's ink is about **2.5 points left and 4–4.5 points down**. This is a documented view difference from the small run; the other large-build run should reproduce this large view, not copy the small drag-start coordinates.
- Parked the pointer on empty canvas at **(250,650)** with `gesture.py 78403 hover 250 650 250 650 30 large-00-view.png`.
- **large-00-view.png**: final baseline, **30 s** wait, **100%**, **Keyboard drawing off**, no popup/dialog/tooltip or other-window overlap. The pointer is far from the chains. Visually inspected and accepted.

## D. Atom verification and coordinates

The target is the free, unlabeled **left carbon endpoint of the chain above “w · Wedge”**, matching the structure used in the small run. It has one bond, with empty paper to its left.

- **large-check-hover.png**: Select tool; `hover 250 500 440 517 30`. A green circle highlights the endpoint at **(440,517)**, confirming an atom hit. Final wait **30 s**; clean and accepted.
- The ring-hover destination preserves the small run's relative location near the chosen chain. The ring drag is 45 points left; the bond drag is 60 points left.
- Appended these lines to `../coords.txt`:

```text
large RING_HOVER_FROM 250 500
large RING_HOVER_TO 457.5 469.5
large RING_DRAG_FROM 440 517
large RING_DRAG_TO 395 517
large BOND_DRAG_FROM 440 517
large BOND_DRAG_TO 380 517
```

## E. Ring hover

- Opened the ring-tool palette and clicked **Benzene**. Verified `Benzene · j` active and the palette closed before preview gestures.
- Exact final gesture: `gesture.py 78403 hover 250 500 457.5 469.5 180 large-01-ring-hover.png`.
- First attempt at **30 s** was incomplete: a benzene preview appeared at the gesture's starting point `(250,500)`, not its destination. Repeated at **180 s**; the preview reached the destination and showed the expected six atom handles and alternating bonds. There were four 180-second hover attempts in total while trying to obtain a clean toolbar.
- **Final wait: 180 s.** The saved **large-01-ring-hover.png** has the correct preview centered at `(457.5,469.5)`, **100%** zoom, status **Keyboard drawing off**, and the Benzene hint: “Drag rotates in 15° steps · Option/Alt rotates freely and connects from an atom · Escape cancels”. The surrounding drawing matches the final baseline.
- **Unresolved capture defect:** a small blue **A** indicator overlays the context toolbar near PNG `(736,337)` / window `(368,168.5)`. It does not cover the molecular preview, but it violates the requested clean-window condition. The hover image is therefore **affected evidence**, not a fully clean comparison screenshot. It was not cropped, painted out, composited, or otherwise modified.
- Tried waiting, Escape cancellation, reselecting Benzene, and selecting it through the mouse-driven palette instead of its shortcut. The indicator persisted or returned in the settled hover shots. Asked the user asynchronously whether this indicator could be dismissed; continued the authorized preview work while leaving system settings and other apps untouched. Its exact source was not established.
- Hover was recaptured after the accepted ring drag to try to remove this defect; the pan, zoom, target coordinates, and drawing remained unchanged. A final cleanup test after the accepted bond drag used the identical hover path with **90 s**, saved separately as **large-hover-90-test.png**. Its geometry also reached the correct destination, but the same A badge remained. The numbered hover file remains the unmodified **180 s** capture; the 90 s test did not replace it.
- After each hover attempt, checked the app state. Undo remained disabled. Escape used during the cleanup attempts returned to Select. No Cmd+Z was needed.

## F. Ring drag

- Kept/restored **Benzene** active with the palette closed.
- First attempt: `drag 440 517 395 517 30 large-02-ring-drag.png`. At **30 s**, the screenshot still showed an old hover preview at `(250,650)`, rather than the drag. Rejected and replaced it.
- Waited for the helper's Escape/release to be processed. Verified Select active and Undo still disabled before retrying.
- Exact final gesture: `gesture.py 78403 drag 440 517 395 517 180 large-02-ring-drag.png`.
- **Final wait: 180 s.** **large-02-ring-drag.png** shows a green benzene preview attached by its rightmost vertex to the endpoint at `(440,517)` and extending left into clear paper. Captured while the mouse button was still held. The rest of the ink is unchanged; zoom **100%**, status **Keyboard drawing off**, Benzene hint visible.
- This final drag screenshot is **clean**: no blue A indicator, popup, tooltip, dialog, notification, or other-window overlap. Inspected directly and independently reviewed by a read-only worker.
- After capture, the helper sent Escape, then released. The first state query timed out; waited 15 seconds and retried. Select was active and Undo remained disabled. No Cmd+Z was needed.

## G. Bond drag

- Selected the visible **plain Single bond · 1** toolbar button at PNG `(138,542)`. Verified Single active; no popup. Default **Length 14.4 pt** and **Angles** remained checked.
- First attempt: `drag 440 517 380 517 30 large-03-bond-drag.png`. At **30 s**, no bond preview had appeared. Rejected and replaced it.
- Waited for the first attempt's Escape/release to be processed; several state queries timed out, each followed by a 15-second wait and retry. Eventually verified Select active and Undo still disabled, then restored plain Single bond.
- Exact final gesture: `gesture.py 78403 drag 440 517 380 517 180 large-03-bond-drag.png`.
- **Final wait: 180 s.** **large-03-bond-drag.png** shows a horizontal single-bond preview extending left from `(440,517)`, with green handles at both ends. The default fixed-length setting means the visible bond stops short of the 60-point pointer destination, as in the small run.
- Captured while the button was held; helper then sent Escape and released. **100%** and **Keyboard drawing off** are visible. Remaining ink matches the baseline.
- This screenshot is **clean**: no blue A badge, popup, tooltip, dialog, notification, or other-window overlap. Inspected directly and independently reviewed by a read-only worker.
- After capture, the first state query timed out; waited 15 seconds and retried. Select was active and Undo remained disabled. No Cmd+Z was needed.

## H. Integrity and rough responsiveness

- **Undo remained disabled after all E, F, and G attempts**, including retries. No Cmd+Z was needed. No ring, bond, or other drawing object was committed.
- The helper's drag captures were taken while the button was still held, followed by Escape before release; `--release` was never used.
- **large-ring-tool-inspect.png** was redone as a final integrity capture after the accepted bond drag: Select active, pointer parked at `(250,650)`, `hover 250 650 250 650 30`. It visually confirms the original chains with no added ring or bond. It is an **auxiliary affected capture** because the blue A indicator returned over the toolbar; it is not comparison evidence. The earlier version caught the open ring palette while AX exposed only the window shell; it was overwritten after the popup closed.
- **Rough debug-build impression:** 30 seconds was insufficient for the ring hover to reach the final pointer position, for ring drag to replace an old hover, or for bond drag to appear. At 180 seconds, each required preview geometry was present. Separate attempts showed correct hover geometry at 90 seconds and correct drag geometry at 180 seconds. Because these were separate attempts with queued events and observation overhead, they do not establish preview-settling bounds. Exact onset was not sampled and this is not a performance benchmark. A separate 90-second hover cleanup test is documented below.
- Tool changes and cancellation checks also sometimes needed multiple 15-second retries. One Benzene tool-change readiness check required several retries and minutes before AX reported it active. These are tool/app observation delays under load, not isolated render timings.

## I. Quit

- Final state query after the 90-second hover test still showed Undo disabled; no edit or save was needed.
- Sent **Cmd+Q** at approximately **2026-11-15 12:58:05–12:58:10 UTC** (21:58 JST).
- No save prompt was presented. At **12:58:14 UTC**, `pgrep -x reshiki-bin` returned no process, confirming exit. No `kill` was needed.
- Did not query the app after quitting. Subsequent work was limited to the report, coordinates, and saved PNGs.

## Screenshot inventory and final waits

Every saved image is a window-only capture at **2560 × 1704 pixels**. Each was visually inspected. Preview/hover/drag/pan captures used the supplied helper; ordinary setup inspections used `screencapture -x -o -l 78403`. Rejected attempts were overwritten by later captures as described above; no image was retouched.

| Filename | State / use | Final explicit wait |
| --- | --- | --- |
| `large-open.png` | Full 8 × 8 gallery, 2%, Document opened; keyboard drawing initially on | No additional capture sleep; first verified capture about 108 s after launch |
| `large-before-scroll.png` | Initial Actual size gap/text view, 100%, Keyboard drawing off | No additional sleep beyond completed UI observation |
| `large-scroll-test.png` | Discarded calibration, five `(40,40)` events | 30 s |
| `large-scroll-calibration.png` | Discarded calibration, one more `(40,40)` event; landmark moved +80 pt on each axis | 30 s |
| `large-reset-inspect.png` | Reset gap/text view at 100%; Arrow tool active before restoring Select | No additional sleep beyond completed UI observation |
| `large-pan-candidate.png` | Final one-call pan lands on Double / Partial double / Wedge rows | 30 s |
| `large-00-view.png` | **Clean final baseline**, pointer parked `(250,650)` | **30 s** |
| `large-check-hover.png` | **Clean Select atom hit check**, green highlight at `(440,517)` | **30 s** |
| `large-01-ring-hover.png` | Correct settled benzene hover; **affected by blue A toolbar indicator** | **180 s** |
| `large-02-ring-drag.png` | **Clean held benzene drag**, attached to endpoint and extending left | **180 s** |
| `large-03-bond-drag.png` | **Clean held single-bond drag**, fixed-length preview extending left | **180 s** |
| `large-ring-tool-inspect.png` | Final Select integrity view after bond cancellation; original chains; **affected by A indicator** | 30 s |
| `large-hover-90-test.png` | Additional cleanup attempt, correct hover geometry; **affected by A indicator** | 90 s |

The primary comparison files are the numbered baseline and three previews. The ring hover is explicitly flagged as affected evidence; only the two held-drag previews fully meet the clean screenshot condition.

## Friction

- **Shared-instance gate:** another ReShiki run was active initially. Waited approximately six minutes without touching it, then launched exactly one instance of the supplied wrapper.
- **Slow debug build and heavy load:** initial connection, tool switches, palette operations, and post-Escape state queries frequently timed out. Waited 15 seconds and retried, up to several times per affected operation. No operation required more than the allowed ten retries. Kept waiting for verified state rather than piling on drawing gestures.
- **Keyboard drawing on open:** the large gallery opened in keyboard drawing, as in the earlier report. The visible Keyboard context button switched it off. AX clicks on some web controls reported `elementHasNoFrame`; visible coordinate clicks worked.
- **Palette accessibility:** with the ring palette open, AX sometimes returned only the window frame and menu bar. A setup inspection exposed the open palette and was redone after closure; selected Benzene using its visible tile and verified its active AX state before captures.
- **Actual size reset:** a timed-out command-entry batch left the palette pending. Inspected it, completed Actual size, verified 100%, and restored Select after observing Arrow active. The atom-label preset also read I afterwards, but it was never used. Undo stayed disabled; no document change was committed.
- **Pan calibration:** positive scroll helper deltas move the drawing right/down at the observed two-window-point scale. Calibration was discarded with Fit → Actual size. The final sequence has one recorded scroll call, so the other large run can reproduce it without exploratory panning.
- **Preview lag:** 30 seconds was insufficient on all three first preview attempts. Retried with 180 seconds. The separate 90-second hover test also reached the final geometry. These are rough observations with queued events and tool overhead, not benchmarks.
- **Persistent blue A badge:** it appeared over the context toolbar in settled hover/Select captures, remained after Escape and long waits, and returned after mouse-driven palette selection. It was absent from both accepted held-drag images. Did not establish its source, alter system settings, touch another app, or retouch images to remove it. Requested user context asynchronously; no response arrived before quitting. This is the remaining clean-hover limitation.
- **Fixed bond length:** the checked Length 14.4 pt and Angles options produce a bond shorter than the 60-point pointer travel. Preserved these defaults for comparison.
- **Shell convenience:** bare `python` was unavailable when first appending coordinates; that attempt wrote nothing. Repeated the append successfully with `python3`. GUI gestures themselves used the exact supplied `uv run ... python gesture.py` command.

## Completion and limits

- Completed the large baseline, verified carbon endpoint, deterministic pan and all six gesture-coordinate lines, and **clean ring-drag and bond-drag comparison captures**.
- Captured the correct large **ring-hover geometry**, but **could not obtain a fully clean hover screenshot** within the allowed actions because of the persistent blue A toolbar overlay. The 180 s numbered image and 90 s cleanup image retain this visible defect and are clearly identified above.
- Could not measure precise preview onset. The final explicit waits and the incomplete first attempts are reported without treating them as benchmark results.
- No drawing object was committed, no Cmd+Z was needed, and no input drawing file was saved or modified. No other app was closed or manipulated, no system setting was changed, and the wrapper/helper files were left unchanged.
- All artifact writes are in this directory; the only intentional write outside it was appending the final large reproduction lines to `../coords.txt`.
- A read-only independent worker verified A–D consistency, the target hit, and both accepted held-drag images. All app driving stayed in the main session.

# ReShiki real-app check — main 1d94f392 (before)

- Build: release build, identified by the supplied test instructions as main `1d94f392`.
- Run: 2026-11-15, approximately 15:21:39–15:31:14 JST.
- Wrapper: `<base build>/ReShiki.app`.
- Input: `gallery-64.rsk`, the supplied 64-copy gallery.
- Launched once with the exact requested `open -n -a …` command. Attached by the exact wrapper path after launch; the wrapper process was PID 78162. Exactly one process matched this wrapper at the process checks. No window resizing, application-setting changes, or source-repository edits were made. The isolated data directory was left untouched.
- GUI input used computer use. Screenshots show only the ReShiki window. Native screenshot/accessibility calls repeatedly timed out; after waits of at least 20 seconds, the permitted `screencapture -l 74521` fallback was used where necessary.

## Timing interpretation

Each timed shortcut was preceded by a shell `time.time()` timestamp. Elapsed values below are rounded wall-clock intervals to the stated observation. They include tool overhead and required timeout/retry waits. **They are observation upper bounds, not precise application execution times.** In particular, the launch and selection completed before their first successful screenshot, but the exact completion instant was not observed. The requested ±2-second operation timing could not be established for those cases. Failed movement steps produced a visible no-op result rather than remaining stuck, so there was no reason to wait the full five-minute allowance.

## Results

“Pass” means the expected visible result was present and a subsequent observation responded. Detailed chemical geometry could not be checked at the unchanged fit scale, which the status bar rounded to **0%**.

| Step | What was observed | Screenshot | Elapsed seconds | Draws correctly and responds |
| --- | --- | --- | --- | --- |
| 0 — Launch/open | The named document opened. A thin horizontal row of repeated galleries was visible across the canvas. Status: “Document opened.” No welcome, recovery, or restore prompt appeared. Keyboard drawing mode was already active. | [01-open.png](01-open.png) | **35 s** to first screenshot showing the drawing | **PASS** for visible drawing/opening; detail limited by fit scale. |
| 1 — Clear selection, Cmd+A | Clicked once on empty canvas well below the row, then pressed Cmd+A. A green selection/bounding box appeared. Properties listed **30,592 atoms · 320 points · 8,512 objects · 27,456 bonds**, and showed “Selection” plus properties for 64 arrows. Two native observations timed out before the successful fallback screenshot. | [02-select-all.png](02-select-all.png) | Selection visible by **118 s**; responsive AX observation by **123 s** | **PASS** for visible selection and populated Properties. |
| 2 — Down once | The selection stayed at its previous vertical position. The highlighted Keyboard mode remained active and the status changed to **“No drawing hotspot in that direction.”** The requested downward nudge did not occur. The screenshot and AX observation returned. | [03-nudge.png](03-nudge.png) | No-op/error result observed by **21 s**; successful movement time unavailable | **FAIL** — responds, but does not perform the requested move. |
| 3 — Cmd+Z | The drawing remained in the same position, with the same selection and “No drawing hotspot in that direction” status. There was no preceding nudge to undo. Undo remained disabled in the accessibility state. | [04-undo.png](04-undo.png) | Unchanged drawing captured by **50 s**; AX response by **56 s** | **FAIL for the requested movement-undo check** — prerequisite nudge failed; no undo restoration could be demonstrated. The app responded. |
| 4 — Shift+Cmd+Z | The drawing again stayed in the same position. No downward movement was redone, and Redo remained disabled. | [05-redo.png](05-redo.png) | Unchanged drawing captured by **54 s**; AX response by **59 s** | **FAIL for the requested movement-redo check** — no nudge/undo history existed to redo. The app responded. |
| 4 — Additional Cmd+Z | Sent the one additional undo required after the redo check. The accessibility tree returned unchanged; selection remained active. | No additional screenshot requested; preceding state is in `05-redo.png`. | AX response by **49 s** | **PASS for returning/responding**; still no movement history to undo. |
| 5 — Cmd+Option+Shift+H | The selected row visibly changed its horizontal arrangement. Status became **“Drawing changed,”** the document acquired a modified indicator, and Undo became enabled. Properties retained the same selection counts. The first two AX observations timed out, then the next returned within the three-minute limit. | [06-distribute.png](06-distribute.png); later poll [06-distribute-check-02.png](06-distribute-check-02.png) | Redraw visible by **50 s**; second screenshot at **105 s**; responsive AX state by **109 s** | **PASS** for visible distribution/redraw and response within 180 s. Individual structures were too small for a detailed geometry judgment. |
| 5 — Distribution Cmd+Z | The previous selected-row appearance and bounding-box position returned. Status: **“History restored.”** The modified indicator disappeared, Undo became disabled, and Redo became enabled. | [07-distribute-undo.png](07-distribute-undo.png) | Restored drawing captured by **49 s**; responsive AX state by **54 s** | **PASS** — visible restoration and response. |
| 6 — Cmd+Q | The wrapper exited normally. No save prompt appeared after the distribution had been undone. A subsequent process check found no matching wrapper process. No kill command or relaunch was needed. | No screenshot requested; the ReShiki window had closed. | Exit confirmed by **7 s** | **PASS** for responding and quitting; drawing check not applicable after exit. |

## Friction

- **Keyboard mode intercepts the nudge workflow.** On opening, the Keyboard control was active. Clicking empty canvas cleared the active atom position but left Keyboard mode active. After Cmd+A, Down produced “No drawing hotspot in that direction” instead of moving the selection. This blocks the prescribed nudge and its undo/redo checks even though Select/move and the full selection are visible. No extra mode-changing action was taken because the task restricted actions to the specified sequence.
- **The fit scale makes this large document hard to inspect.** The row occupies a narrow band and the zoom readout is 0%. Structures cannot be read individually, and a small downward movement would be difficult to judge visually. The window and zoom were left as opened.
- **Properties uses separate atom and point counts.** For the input described as 30,912 atoms, the panel displayed 30,592 atoms plus 320 points. Those two counts total 30,912, but the UI does not make their relationship to the supplied input description clear. This is an observed labeling/count distinction; no data loss was established.
- **Observation responsiveness was intermittent.** Native screenshot/accessibility requests repeatedly failed with `timeoutReached` after shortcuts. Later AX requests succeeded, while window-only shell screenshots could capture the rendered state. These delays made the check slow and prevented tight timing. The observations do not distinguish application work from computer-use-server or machine-load delays.

## Could not complete or establish

The requested downward movement and its undo/redo behavior could not be demonstrated because Down was handled as keyboard-drawing navigation and returned “No drawing hotspot in that direction.” Those keys were still sent once each as instructed. No extra corrective mode changes or repeated movement keys were used.

Exact operation latency to ±2 seconds and screenshots every few seconds were not achieved: native observation calls timed out and required 20-second retry waits; fallback setup and observation overhead further widened the sampling intervals. The report therefore records first-successful-observation upper bounds rather than claiming those intervals are application processing times.

Detailed chemical rendering correctness and exact horizontal spacing could not be verified at the unmodified 0% fit-scale view. The visible redraw, modified/history states, selection counts, and distribution undo were verified. All seven required PNG files and the extra distribution polling PNG were saved in this artifact directory. The app was quit and was not relaunched.

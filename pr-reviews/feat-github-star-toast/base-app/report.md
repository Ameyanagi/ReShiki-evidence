# ReShiki GitHub-star feature — before evidence

Captured on **2026-11-15**, using the already-running main-branch debug build identified by the requester as **1d94f392**, PID **43964**. The About panel displays **Version 0.15.0**. All requested baseline expectations were observed: no idle prompt card, no GitHub-star link in About/Updates, and no About button in Help.

## Capture setup

- App wrapper: `/Users/shiranui/dev/reshiki-targets/apps/star-base/ReShiki.app`.
- Isolated data directory: `/tmp/reshiki-star-base.MmO2`.
- Document: `aspirin.mol`; its title already included the modified-state bullet when this session began.
- Evidence window: **CGWindowID 73895**, **1280 × 852 points**, at **(200, 115)**. The supplied `wins 43964` helper confirmed this geometry before the first capture and again before quitting. The window was not moved or resized.
- Every evidence PNG was captured directly with `screencapture -l 73895 <filename>.png`, retaining the default window shadow. No `-o`, crop, compositing, or image edits were used. Each PNG is **2784 × 1928 pixels** including the shadow.
- UI interactions used computer use: title-bar/control clicks and keys. The existing Select tool was used; an empty canvas position was clicked, followed by Esc before each idle interval. Keyboard drawing was already enabled at the start and remained enabled; the orange empty-position hotspot is part of the baseline UI.
- All times below are **JST (UTC+09:00)**. Idle zero is the timestamp recorded immediately after the final Esc call completed. No mouse movement, clicks, or keys were sent during either idle interval. Screenshot commands and file inspection did not provide app input.

## Steps: expected versus observed

| Step | Expected | Observed | Evidence / timing |
|---|---|---|---|
| 1. Light idle | No “Enjoying ReShiki?” card after 30 seconds; seeded prompt file unchanged. | No card in the lower-right canvas at either capture. The two independently captured PNGs are byte-identical. The seed remained exactly as supplied. | [01-idle-light-35s.png](01-idle-light-35s.png), [02-idle-light-40s.png](02-idle-light-40s.png). Final input: **12:59:37.724**. Detailed timing below. |
| 2. Light About/Updates | “Release notes ↗” present; no star link. | Clicking the header ReShiki wordmark opened the panel. It shows Version 0.15.0, Stable selected, “You’re up to date on Stable.”, update controls, checked “Check automatically”, and “Release notes ↗”. No star/GitHub link appears. Closed with Esc. | [03-updates-panel-light.png](03-updates-panel-light.png), capture command started **13:02:14.072**. No link or Check for updates button was activated. |
| 3. Light Help | Footer has no “About ReShiki” button. | Toolbar Help opened “Help & shortcuts”. Its footer was fully visible immediately, with navigation guidance, “Open shortcut examples”, and “Done”; no About button. Closed with Esc. | [04-help-light.png](04-help-light.png), **13:02:34.641**. No scrolling was needed, so `05-help-footer-light.png` was intentionally omitted. |
| 4a. Dark idle | Same absence of the idle card after approximately 40 seconds. | Opened View options, which showed Interface “Match canvas”, then used the app’s sun/moon control to switch to dark. Closed View options and repeated title-bar/Select/empty-canvas/Esc preparation. No card appeared. | [06-idle-dark-40s.png](06-idle-dark-40s.png). Final input: **13:03:42.891**; capture started **40.002 s** later. |
| 4b. Dark About/Updates | Release notes present, star link absent. | Same content and controls as light mode, rendered in dark theme; no star link. Closed with Esc. | [07-updates-panel-dark.png](07-updates-panel-dark.png), **13:04:37.217**. No update action or external link was activated. |
| 4c. Dark Help | No About button in footer. | Immediately after closing About with Esc, F1 opened Help without a canvas click. Footer was fully visible and contained no About button. Closed with Esc. | [08-help-dark.png](08-help-dark.png), **13:04:59.156**. No scrolling was needed. |
| 4d. Restore light | Return the app interface to light. | Used the same sun/moon control. Light interface and canvas were visually confirmed. The supplemental image includes the control’s “Light canvas · Switch to dark · Remembered for new drawings” tooltip. Final zoom was 245%, matching the initial evidence. | [09-light-restored.png](09-light-restored.png), **13:05:51.445**. Window still **1280 × 852 points**. |
| 5. Quit | Cmd+Q; choose Don’t Save if prompted; PID 43964 gone. | Cmd+Q sent; completion timestamp **13:06:04.725**. No save prompt was observed. PID and window queries subsequently confirmed the supplied process had exited. | At **13:06:20**, `ps -p 43964 -o pid=,stat=,command=` returned no output, exit **1**. `wins 43964` returned no windows, exit **0**. |

Opening View options temporarily reduced available canvas height and displayed 218% zoom; closing it returned to 245% before the dark evidence captures. No drawing edits were made.

### Idle timing details

A capture command’s start time and a PNG’s last-write time bracket capture processing; neither claims the exact internal compositor sampling instant.

| Filename | Requested delay | Capture command start | Elapsed at start | PNG last-write time | Elapsed at last write |
|---|---:|---|---:|---|---:|
| `01-idle-light-35s.png` | 35 s | 13:00:12.730 | **35.006 s** | 13:00:13.790 | **36.066 s** |
| `02-idle-light-40s.png` | 40 s | Scheduled for 13:00:17.724; exact actual start was not retained | Approximately **40 s** | 13:00:18.247 | **40.523 s** |
| `06-idle-dark-40s.png` | 40 s | 13:04:22.893 | **40.002 s** | 13:04:23.991 | **41.100 s** |

Both light captures were executed by a timer script in sequence. The first completed before the second deadline. The second PNG was fully written near the 40-second target, but its `screencapture` process lingered after writing, preventing the script from emitting its final timing record. Only that capture helper was terminated after validating the PNG. The exact second command-start timestamp therefore remains unavailable.

The same post-write helper behavior occurred for `07`, `08`, and `09`; for those captures, an 8-second timeout verified the complete PNG and stopped only the associated `screencapture` subprocess. No ReShiki process was stopped by these helper cleanups. All eight saved PNGs passed signature, chunk CRC, dimensions, and complete-IEND checks, and were visually inspected. The SHA-256 for both `01` and `02` is `f536c654288f721a5983cb40b8fdc4f2dfe5ac2f0c646d21ea2037ca4ff120c3`.

### Requested data-directory output after light idle

Command:

```sh
ls -la /tmp/reshiki-star-base.MmO2; cat /tmp/reshiki-star-base.MmO2/star-prompt.json
```

Output:

```text
total 16
drwx------@   5 shiranui  wheel   160 Nov 15 12:57 .
drwxrwxrwt  175 root      wheel  5600 Nov 15 13:01 ..
drwxr-xr-x@   3 shiranui  wheel    96 Nov 15 12:57 recovery
-rw-r--r--@   1 shiranui  wheel    59 Nov 15 12:57 star-prompt.json
-rw-------@   1 shiranui  wheel    62 Nov 15 12:57 update-cache.json
{"first_launch_day":"2026-11-14","uses":5,"state":"asking"}
```

The prompt file was read again after all dark captures and light restoration, before quitting. It still contained:

```json
{"first_launch_day":"2026-11-14","uses":5,"state":"asking"}
```

## UX friction

These are review findings for the captured baseline. The absent About-footer and star actions are intentional product gaps in this build, not failures of the requested before-state checks. No high-severity issue was supported by the evidence.

| Severity | Screenshot filename(s) | What happens | Why it matters | Smallest improvement idea |
|---|---|---|---|---|
| **Medium — discovery gap** | `02-idle-light-40s.png`, `06-idle-dark-40s.png`, `04-help-light.png`, `08-help-dark.png` | The header wordmark is the working About opener, but its visible label is only “ReShiki”. Help’s footer has no About route. Its accessible name does identify About/check for updates. | A user looking for version or project information must infer that branding is clickable. Someone who starts in Help must close it and discover another control. | Add **“About ReShiki”** to Help’s footer, using the existing panel. |
| **Medium — support gap** | `03-updates-panel-light.png`, `07-updates-panel-dark.png` | About/Updates offers release notes and update controls, with no GitHub or project-support action. | Even after finding app information, a user has no visible way here to support the project. | Add one secondary **“Star on GitHub ↗”** action beside or immediately after Release notes. Keep its alignment and external-link indicator consistent. |
| **Low — wording** | `04-help-light.png`, `08-help-dark.png` | The selected Shortcut finder says “Search every shortcut, with a drawing of what it does,” while its detail says “there is no drawing to preview.” | The same view creates a preview expectation and then withdraws it. | Use **“Search shortcuts and see what each does.”** Mention drawings only for entries with previews. |
| **Low — scanning / spacing pressure** | `04-help-light.png`, `08-help-dark.png` | Keys and “F8 off” conditions recur across key badges, row titles, and descriptions. The footer combines four instructional clauses on one line beside the actions. | Repetition makes the reference slower to scan and consumes room that could accommodate a clear About action. | Keep keys in their column, shorten titles, and state the keyboard-mode condition once per entry. Shorten the footer to **“↑ ↓ move · Esc closes”**, placing longer guidance with relevant content. |
| **Low — dark readability** | `07-updates-panel-dark.png`, `08-help-dark.png` | Version text, update explanations, Help descriptions, and footer guidance are visibly subdued relative to headings and principal labels. | Useful explanations take more effort to read in dark mode. | Slightly brighten shared muted text, then measure contrast against the panel background. Preserve a separate disabled-control treatment. This is visual polish, not a measured accessibility failure. |
| **Low — panel consistency** | `03-updates-panel-light.png`, `07-updates-panel-dark.png`, `04-help-light.png`, `08-help-dark.png` | About uses a top-right text “Close”; Help uses a top-right × and bottom-right “Done” for dismissal. | Different labels and patterns for the same closing action add a small interpretation cost. | Use the same top-right close control in both panels; if Help retains a footer dismissal action, label it **“Close”**. |

Alignment and spacing are orderly at **1280 × 852 points** in both themes. Primary controls and Help’s footer fit without overlap; no scrolling was required to inspect the footer. The cut-off lower shortcut entry belongs to the scrollable results list and is not a clipped footer. Main text and primary actions remain visually distinct in both themes.

Focus observations: Esc dismissed both panels in both themes. F1 worked immediately after closing dark About, without a mouse click, and Help opened with the search field visibly outlined. No input-blocking focus problem was observed. Exact focus restoration to the opener and full Tab order were not established, so no focus-restoration defect is asserted.

## Unverified items and limits

- This is evidence for the supplied main build only. The feature branch and its actual card/link/button behavior were not opened or tested. Build commit identity was supplied by the requester; the visible app version was independently observed as 0.15.0.
- The 40-second light capture’s exact command-start timestamp was not retained because of the post-write capture-helper hang. Its timer deadline, complete PNG, and last-write time support the requested approximate 40-second timing. Continuous absence between screenshots was not recorded as video.
- GitHub/release-note destinations, update checking, account actions, and network behavior were deliberately not exercised. “You’re up to date on Stable.” is the displayed UI state, not an independently verified freshness claim. Automatic checking was already enabled and was left unchanged; background app network traffic was not measured.
- Exact contrast ratios, screen-reader navigation, complete keyboard traversal, and restored focus to specific controls were not measured. The review describes what was visible and the limited keyboard transitions actually exercised.
- No save prompt appeared during the requested quit, so Don’t Save was not needed. After the target quit, a read-only accessibility observation resolved to a different existing “Untitled — ReShiki” window; no further input was sent through that app binding. Exit confirmation used the supplied PID and its window list.
- No additional ReShiki instance was launched. No links, macOS system settings, repository source files, other apps, other windows, or other ReShiki processes were changed by this task. Only the requested evidence images and this report were written in the evidence folder; capture helpers and timing scratch files were kept under `/tmp`.

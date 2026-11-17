# Step 2 timing protocol

Release builds of main and of this branch, each with the same throwaway probe (never pushed), on macOS arm64 (Apple M4), against the same local mock GitHub (80–150 ms per reply, two more delays on a connection's first reply for TCP + TLS). The protocol below was driven by a second agent with computer use; the window-focus steps (focus-steps.sh) were run from a shell afterwards, as in step 1. The mock seeds 12 more commits to routes/drawing-01.rsk for History.

```text
You are driving a local timing run of a ReShiki build for Claude, with computer use. The app writes its own timing logs; your job is to perform the user actions below in order, and to write a mark line just before each marked action. Screenshots are optional: save a few into ARTIFACT_DIR only if something goes wrong.

ARTIFACT_DIR: __RUN__
App to drive: the app bundle __APP__ (its menu-bar name starts with "ReShiki Probe"). It talks only to a local mock GitHub at http://127.0.0.1:47191 that is already running. It is NOT the real GitHub; there is no real account involved.

Hard rules
- Launch ONLY with: `open -n "__APP__"`. Never launch ReShiki by app name or by the bundle id dev.reshiki.editor. Never run any reshiki binary directly.
- Other ReShiki windows may be open on this Mac (other ReShiki builds). Do not click, type into, focus, quit or otherwise touch them. Only interact with the window of the process you launched (check the app name in the menu bar / window list before acting).
- Do not edit any repository files. Do not change system settings. Do not close other apps.
- Marks: before each marked action run exactly `__MARK__ <label>` (the label given in brackets) in a shell, then perform the action immediately. Waits are part of the protocol: after each action wait the stated time without touching the app, so the app's logs can settle.
- Do not let any tool attach to or look up the app by bundle path before you have written the 00-launch mark and launched it with `open -n` (a lookup by path launches it).
- In the picker, Backspace does not return to the repository list; the repositories stay in the picker's left sidebar, so pick repositories there.
- Do not quit the app at the end.

Protocol
0. Run `__MARK__ 00-launch` and launch the app. Wait for the window. Sign in to GitHub: click the GitHub button (in the status bar, bottom left) and choose Sign in (or "Sign in to GitHub"). A device code appears; do NOT open a browser; the mock approves the code by itself within about 15 s. Wait until the app shows you are signed in as octo-test (the code dialog closes or says signed in). If a dialog remains, close it with Escape.
1. Without a mark: open "Open from GitHub…" (GitHub button menu, or the File menu). Click the repository "group-drawings" in the left list. If the files pane shows a tree, switch to Tiles (two small icon buttons at the right end of the folder path line; Tiles is the left one). Double-click the folder tile "routes". Wait 8 s, so its six drawing tiles and previews show.
2. [04a-open-drawing] Double-click the tile "drawing-01". Wait 6 s. It opens in a new tab with a repository badge; the picker closes.
3. Without a mark: open "Open from GitHub…" again; group-drawings / routes is shown again (if not, pick group-drawings and double-click routes). Wait 4 s.
   [04b-open-drawing] Double-click the tile "drawing-06". Wait 6 s.
4. Without a mark: open "Open from GitHub…" again, as in step 3. Wait 4 s.
   [04c-open-drawing] Double-click the tile "drawing-11". Wait 6 s. Three GitHub tabs are now open (drawing-01, drawing-06, drawing-11), drawing-11 in front.
5. Saves. Three times, in the tab in front (drawing-11):
   - without a mark, click once on an empty spot of the drawing canvas (this adds a fragment with the current tool), wait 2 s;
   - then [05a-cmd-s] (then 05b-cmd-s, then 05c-cmd-s) press Cmd+S and wait 4 s. If a dialog asks something, choose the option that saves in place and note it in your report.
6. Tab switching. Click the tabs by their titles in the tab strip at the top, with a mark before each click and 2 s after each:
   [06a-tab] drawing-01, [06b-tab] drawing-06, [06c-tab] drawing-11, [06d-tab] drawing-01, [06e-tab] drawing-11, [06f-tab] drawing-06.
7. History. Click the tab drawing-01. Wait 2 s.
   [08a-history] Open the GitHub button's menu and choose "History" (or click the clock button just after the inspector's tabs on the right). Wait 8 s. The inspector shows "This computer" and "GitHub" with versions.
   [08b-history-other] Click the tab drawing-06. Wait 6 s (History follows the drawing in front).
   [08c-history-back] Click the tab drawing-01. Wait 6 s.
8. Run `__MARK__ 98-codex-done`. Do NOT quit the app: leave it running, in front, in its current state; Claude does the next steps. Do not touch it any more.

Report: write __RUN__/report.md listing each mark label, whether the action succeeded as described, anything you had to do differently (exact UI path), and anything you could not do.
```

```bash
#!/bin/bash
# focus-steps.sh <before|after>: window focus away and back, twice, then quit.
S=/private/tmp/claude-502/-Users-shiranui-dev-ReShiki/21661837-4da9-40f3-8bf6-7ae65682b395/scratchpad/ghlag2
M=$S/bin/mark
ACT="tell application id \"dev.reshiki.probe.ghlag2.$1\" to activate"
case $1 in before) Name=Before;; after) Name=After;; esac
$M 07a-focus-away; open -a Finder; sleep 4
$M 07b-focus; osascript -e "$ACT"; sleep 10
$M 07c-focus-away; open -a Finder; sleep 4
$M 07d-focus; osascript -e "$ACT"; sleep 8
$M 99-end
pkill -f "$S/app/ReShiki Probe $Name.app/Contents/MacOS/reshiki-bin"
```

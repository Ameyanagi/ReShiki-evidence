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
- When done, quit the app with `pkill -f "__APP__/Contents/MacOS/reshiki-bin"` (only that path).

Protocol
0. Run `__MARK__ 00-launch` and launch the app. Wait for the window. Sign in to GitHub: click the GitHub button (in the toolbar or the status bar) and choose Sign in (or "Sign in to GitHub"). A device code appears; do NOT open a browser; the mock approves the code by itself within about 15 s. Wait until the app shows you are signed in as octo-test (the code dialog closes or says signed in). If a dialog remains, close it with Escape.
1. [01-picker-open] Open "Open from GitHub…" (GitHub button menu, or the File menu). Wait 8 s. It lists the repositories on the left (group-drawings, lab-notes, notes, reaction-notes, spectra …).
2. [02a-choose-repo] Click the repository "group-drawings" in the left list. Wait 8 s. (The files pane shows a tree or tiles of the folders 2026, aromatics, complexes, fullerenes, routes.)
   Then, without a mark: the files pane has a Tiles/Tree switch (two small icon buttons at the right end of the folder path line). If Tiles is not the selected one, click the Tiles button (the left one). Wait 4 s. Folder tiles show.
3. [02b-open-routes] Double-click the folder tile "routes". Wait 8 s. (Six drawing tiles; previews and a second line with who/when fill in.)
4. [02c-up] Click "group-drawings" in the folder path at the top of the files pane (the breadcrumb, not the left list) to go back up. Wait 6 s.
5. [02d-reopen-routes] Double-click the folder tile "routes" again. Wait 6 s.
6. [02e-repick-repo] Click "group-drawings" in the LEFT repository list again. Wait 6 s.
7. Big folder. Click into the picker's search field (top left), select all, and type this link: `http://127.0.0.1:47191/alice/ligands/tree/main/screening`
   [03a-bigfolder-open] (mark just before pressing Return) Press Return. Wait 10 s. A folder of 240 "hit-NNN" tiles appears.
8. [03b-scroll-1] Scroll down inside the tile grid by about one screen (mouse wheel over the tiles). Wait 6 s.
9. Without a mark: click "group-drawings" in the left list, then double-click the folder tile "routes". Wait 8 s, so its tiles and previews show.
10. [04-open-drawing] Double-click the tile "drawing-01". Wait 8 s. It opens in a new tab with a repository badge; the picker closes.
11. Without a mark: click once on an empty spot of the drawing canvas (this adds a fragment with the current tool). Wait 2 s.
    [05-cmd-s] Press Cmd+S. Wait 5 s. (If a dialog asks something, read it and choose the option that saves in place; note it in your report.)
12. [06a-send-open] Open the GitHub button's menu and choose "Send 1 drawing" (or the Send button on the status chip). Wait 3 s. A small Send box appears with a message.
    [06b-send] Click the Send button in that box. Wait 10 s. The chip should end at sent (a check mark).
13. Run `__MARK__ 99-end`, then quit the app as described.

Report: write __RUN__/report.md listing each mark label, whether the action succeeded as described, anything you had to do differently (exact UI path), and anything you could not do.

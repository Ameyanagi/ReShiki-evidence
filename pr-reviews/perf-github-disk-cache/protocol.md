# Disk cache timing protocol

Release builds of `04e88c10` (main, before) and of this branch at `4ebbb35b` (after; the later commits change folder names, the entry checksum and eviction bookkeeping, not what is requested), each with step 2's throwaway probe (never pushed), on macOS arm64 (Apple M4). Both ran against the same local mock GitHub: the after build's mock, which answers every GET with an ETag and a matching `If-None-Match` with 304; 80–150 ms per reply, and two more delays on a connection's first reply for TCP + TLS. The mock seeds `octo-test/group-drawings` (30 drawings) and 12 more commits to `routes/drawing-01.rsk` for History, as in step 2. Each build ran with its own fresh `RESHIKI_DATA_DIR`, kept between its two launches.

The after probe adds to step 2's probe: `KD` lines for replies read from disk, and `D cache::load` / `D cache::store` spans, which name the thread they ran on. `analyze4.py <run> [-t]` reads `probe.log`, `mock.log` and `marks.txt`; everything is counted within 6 s of each flow's trigger.

The protocol below was driven by a second agent with computer use. The sign-in is not kept between launches of a build talking to a test server, so part B signs in again.

```text
You are driving a local timing run of a ReShiki build for Claude, with computer use. The app writes its own timing logs; your job is to perform the user actions below in order, and to write a mark line just before each marked action. Screenshots are optional: save a few into ARTIFACT_DIR only if something goes wrong.

ARTIFACT_DIR: __RUN__
App to drive: the app bundle __APP__ (its menu-bar name starts with "ReShiki Probe"). It talks only to a local mock GitHub at http://127.0.0.1:47191 that is already running. It is NOT the real GitHub; there is no real account involved.

Hard rules
- Launch ONLY with: `open -n "__APP__"`. Never launch ReShiki by app name or by the bundle id dev.reshiki.editor. Never run any reshiki binary directly.
- Other ReShiki windows may be open on this Mac (other ReShiki builds). Do not click, type into, focus, quit or otherwise touch them. Only interact with the window of the process you launched (check the app name in the menu bar / window list before acting).
- Do not edit any repository files. Do not change system settings. Do not close other apps.
- Marks: before each marked action run exactly `__MARK__ <label>` (the label given in brackets) in a shell, then perform the action immediately. Waits are part of the protocol: after each action wait the stated time without touching the app, so the app's logs can settle.
- Do not let any tool attach to or look up the app by bundle path before you have written the A0-launch mark and launched it with `open -n` (a lookup by path launches it). The same before B0-launch.
- In the picker, Backspace does not return to the repository list; the repositories stay in the picker's left sidebar, so pick repositories there.
- Quit the app only with `pkill -f "__APP__/Contents/MacOS/reshiki-bin"` (only that path), and only where the protocol says so.

Signing in (used twice below): click the GitHub button (in the status bar, bottom left) and choose Sign in (or "Sign in to GitHub"). A device code appears; do NOT open a browser; the mock approves the code by itself within about 15 s. Wait until the app shows you are signed in as octo-test (the code dialog closes or says signed in). If a dialog remains, close it with Escape. Then wait 5 s more.

Part A: first launch (fills the app's caches)
0. Run `__MARK__ A0-launch` and launch the app. Wait for the window. Sign in.
1. [A1-picker-open] Open "Open from GitHub…" (GitHub button menu, or the File menu). Wait 6 s.
2. [A2-choose-repo] Click the repository "group-drawings" in the left list. Wait 6 s. If the files pane shows a tree, switch to Tiles (two small icon buttons at the right end of the folder path line; Tiles is the left one) and wait 4 s.
3. [A3-open-routes] Double-click the folder tile "routes". Wait 8 s, so its six drawing tiles and previews show.
4. Click into the picker's search field (top left), select all, and type this link: `http://127.0.0.1:47191/alice/ligands/tree/main/screening`
   [A4-bigfolder-open] (mark just before pressing Return) Press Return. Wait 10 s. A folder of "hit-NNN" tiles appears.
5. Without a mark: click "group-drawings" in the left list, then double-click the folder tile "routes". Wait 6 s.
   [A5-open-drawing] Double-click the tile "drawing-01". Wait 6 s. It opens in a new tab with a repository badge; the picker closes.
6. [A6-history] Open the GitHub button's menu and choose "History" (or click the clock button just after the inspector's tabs on the right). Wait 10 s. The inspector shows "This computer" and "GitHub" with versions.
7. Run `__MARK__ A9-quit`, then quit the app with the pkill command above. Wait 5 s and check that its window is gone.

Part B: the same again after a restart (this is what is timed)
8. Run `__MARK__ B0-launch` and launch the app again with `open -n "__APP__"`. Wait for the window, then wait 5 s more. Sign in again (the sign-in is not kept between launches of this test build).
9. [B1-picker-open] Open "Open from GitHub…". Wait 6 s.
10. [B2-choose-repo] Click the repository "group-drawings" in the left list. Wait 6 s. (If it shows a tree, switch to Tiles without a mark and wait 4 s.)
11. [B3-open-routes] Double-click the folder tile "routes". Wait 8 s.
12. Click into the picker's search field, select all, and type the same link: `http://127.0.0.1:47191/alice/ligands/tree/main/screening`
    [B4-bigfolder-open] (mark just before pressing Return) Press Return. Wait 10 s.
13. Without a mark: click "group-drawings" in the left list, then double-click the folder tile "routes". Wait 6 s.
    [B5-open-drawing] Double-click the tile "drawing-01". Wait 6 s. It opens in a tab.
14. [B6-history] Open the GitHub button's menu and choose "History" (or the clock button). Wait 10 s.
15. Run `__MARK__ 99-end`, then quit the app with the pkill command above.

Report: write __RUN__/report.md listing each mark label, whether the action succeeded as described, anything you had to do differently (exact UI path), and anything you could not do.
```

The after probe was made from the branch with this script, after `git apply --exclude=src/github/client.rs --exclude=src/github/mock.rs` of step 2's probe and a copy of the before probe's `mock.rs`:

```python
# Run in the after-probe worktree, after `git apply --exclude` of the probe patch
# without client.rs and mock.rs, and after copying the before probe's mock.rs.
def edit(p, pairs):
    s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a)
        s = s.replace(a, b)
    open(p, 'w').write(s)

edit('src/github/mock.rs', [
("""    pub most_busy: usize,
}""", """    pub most_busy: usize,
    pub unchanged: usize,
}"""),
("""    let reply = respond(&mut model.lock().unwrap(), base, request);
    tokio::time::sleep""", """    let asked = (request.method == "GET").then(|| request.headers.get("if-none-match").cloned());
    let mut reply = respond(&mut model.lock().unwrap(), base, request);
    if let Some(asked) = asked
        && reply.status == 200
    {
        let etag = format!("\\"{}\\"", sha(&reply.body));
        if asked.as_ref() == Some(&etag) {
            (reply.status, reply.body) = (304, Vec::new());
        }
        reply.headers.push(("ETag", etag));
    }
    tokio::time::sleep"""),
])
edit('src/github/client.rs', [
("""    let build = || {
        let builder""", """    let build = || {
        let _probe = crate::probe::Span::new("C", "new reqwest::Client");
        let builder"""),
("""            true => builder.no_proxy(),""", """            // PROBE: the mock speaks HTTP/2 as GitHub does over TLS.
            true => builder.no_proxy().http2_prior_knowledge(),"""),
("""        if let Some(bytes) = self.replies().get(path) {
            return Ok(bytes);
        }
        let kept""", """        if let Some(bytes) = self.replies().get(path) {
            crate::probe::emit("K", 0, path);
            return Ok(bytes);
        }
        let kept"""),
("""            Some(on_disk) => on_disk.bytes,""", """            Some(on_disk) => {
                crate::probe::emit("KD", 0, path);
                on_disk.bytes
            }"""),
("""    ) -> Result<Option<(Vec<u8>, Option<String>)>, Error> {
        let mut access""", """    ) -> Result<Option<(Vec<u8>, Option<String>)>, Error> {
        let mut probe = crate::probe::Span::new("H", format!("{method} {path}"));
        let mut access"""),
("""            let status = response.status();
            if status == StatusCode::NOT_MODIFIED""", """            let status = response.status();
            probe.note(&format!("status={}", status.as_u16()));
            if status == StatusCode::NOT_MODIFIED"""),
])
print("ok")
```

## Why it matters

Step 1 (#1219) removed most of the network waiting in the GitHub integration. What is left are short hitches on the window's own thread and one slow panel:

- Opening a drawing from GitHub wrote the working copy with two `fsync`s inside the window's update: 11–22 ms, about one dropped frame per open. **Update** and a conflict choice wrote the same way.
- Every save, Send, window focus, tab close and drawing open re-read and SHA-256-hashed every tracked working copy of the repository on the window's thread, twice per save. It grows with the number and size of drawings opened in a repository.
- **History** asked three requests one after another (branch, commit, commit list) before showing anything, then downloaded every listed version, 0.5–1.0 s at 80–150 ms per reply.

This is step 2 of the plan the owner approved on 2026-11-18. The disk cache with ETags (item 3 of that plan) is proposed as its own PR; it is not in this one.

## Approach

### 1. Working-copy reads and writes off the window's thread

- **Writes.** Opening from the picker, **Update** and a conflict choice (Keep mine, Keep GitHub's, Keep both) now write in a `spawn_blocking` task (`App::github_write`). The window keeps the picker busy until the write lands, then takes in the new base, persists `state.json` and opens the tab. Opening and Update write through `workcopy::checkout_synced`, which refuses to write over a file that differs from what was last synced (changed in another app meanwhile); Update then reads that file back, so the chip says **Review** instead.
- **Unsent is derived, not scanned.** The window keeps, per working copy, the SHA-256 it last read or wrote (`State::hashes`), and "unsent" is computed from that and `state.json`'s base hash. Nothing reads files on the window's thread any more. Reads run in the background when a drawing opens and on window focus (for edits made in another app), and after a save only the saved drawing is read back. Until it is, it counts as unsent, so the count never dips.
- **Late results.** Every read carries the `seq` it began at; per file, the read begun last wins, and a write made here counts as newer than every read begun before it. A result for a picker request that moved on still records the file it wrote, but opens nothing.

### Why the order is safe

- **A write finishes before Send reads the file.** `State::writes` counts writes in flight. A Send started meanwhile is marked as sending and queued (`deferred`); when the last write's result has been taken in (new base and hash applied), `github_wrote` starts the queued Sends, which only then clone the state and read the files (`send::outgoing`, still off the window's thread). A conflict choice that ends with a Send issues it after its own write.
- **Quitting never drops a write in flight.** A write counts as running until the `state.json` that records its new base is written too (`Persisted(true, _)`). If the window is closed meanwhile, the close waits (`quit_after`) and starts again once both have landed, so the Send question sees what was written. Every write is atomic (temporary file, `fsync`, rename, folder `fsync`), as before: a crash mid-write leaves the old file or the new one.
- **A save that goes on with a close.** Answering **Save** when closing a GitHub drawing marks the file unread before the close continues (`github_unread`), so the close still asks whether to send it.
- **An edit made while Update writes** keeps the tab unsaved: GitHub's version replaces it as one undo step, and closing asks.
- **What did not change:** `send::outgoing` still reads and hashes every unsent file from disk when a Send starts, so what is sent is decided by the files, not by the cached hashes.

### 2. History lists first, reads previews as rows show

- GitHub's versions are listed from the branch in one request (`commits?sha=<branch>&path=…`), instead of branch → commit → list. **Load more** lists from the oldest commit shown, which no push moves, so a branch that moves (or is moved back) between pages neither skips nor repeats a version.
- No version drawing is read when the list arrives. Each row without its drawing is wrapped in a `sensor`; the drawing is asked for once, when the row first comes into view (100 px ahead). `api::raw_at` asks by commit, so its reply is kept in the session cache.
- A drawing's list and the drawings read so far are kept per drawing for the session (`Versions::kept`) and shown at once when its History opens again, while the list is asked again. Commit SHAs never change, so a kept drawing is never stale. A drawing whose row left the first page while it was read is asked again when its row returns.
- **Accounts.** Only a list read while signed in is kept. Signing out forgets every kept list, clears GitHub's versions on screen and drops late replies, so another account never sees them.

## Before/after timings

Release builds of `df1f03d4` (main, before) and this branch (after), each with the same throwaway timing probe (never pushed), run on macOS arm64 (Apple M4) against the same local mock of GitHub: 80–150 ms per reply, plus two more delays on a connection's first reply for TCP + TLS. The same protocol drove both builds through a second agent with computer use; the window-focus steps ran from a shell afterwards, as in step 1. "Window thread" is the time the window's own thread spent: the slowest `App::update` of the flow and its synchronous disk work. Times run from the input to the first frame after the flow's last reply or write.

| Flow | Window thread before | Window thread after | Before | After | Requests before → after |
|---|---|---|---|---|---|
| Open a drawing from the picker (×3) | **10.8–12.0 ms** update (`Downloaded`), 11.8–13.2 ms of it disk with `fsync` | **0.3–0.9 ms**, no disk (the write takes 20–35 ms off the thread) | 142–198 ms | 161–208 ms | 0 → 0 (blobs read by the preview) |
| ⌘S on a GitHub drawing (×3) | 1.3–1.5 ms (`Saved`) + 0.7–1.0 ms (`Recorded`): two scans of all 3 tracked files | **0.01 ms each**, no disk; only the saved file is read back, off the thread | – | – | 0 → 0 |
| Switch among 3 GitHub tabs (×6) | ≤ 0.4 ms, no disk | ≤ 0.5 ms, no disk | 21–64 ms | 15–53 ms | 0 → 0 |
| Window focus (newer check) | 1.4 ms (`Newer`, a scan on the thread) | **0.2 ms**; the scan runs off the thread | 190 ms | 222 ms | 2 → 2 |
| Open History (12 versions; first request on a new connection in both) | ≤ 0.6 ms | ≤ 0.6 ms | **rows 457 ms**, all previews 688 ms | **rows 369 ms**, all previews 603 ms | 15 → 13: ref + commit + list + 12 previews → list + 12 previews (all 12 rows were on screen) |
| Another drawing's History (1 version) | ≤ 0.3 ms | ≤ 0.2 ms | rows 223 ms, done 359 ms | **rows 100 ms**, done 197 ms | 3 → 2 |
| Back to the first drawing's History | ≤ 0.4 ms | ≤ 0.4 ms | rows 272 ms, previews 508 ms | **rows and previews in the first frame, 130 ms**; the list is checked again (189 ms) | **15 → 1** |

- The saving is on the window's thread, not in wall time: the network part of these flows is unchanged, so wall times move with the mock's random 80–150 ms per reply.
- History's first open saves two round trips; both builds paid a new connection for its first request, because the connection had gone idle during the saves. The 12 rows all fit on screen, so all 12 previews were still read; a longer list now reads only the rows shown.
- Going back to a drawing's History shows the remembered rows and previews in one frame. That frame drew all 12 previews at once (115 ms of drawing, two of them C60 drawings); before, the same drawing work was spread over the 0.5 s in which previews arrived.
- Per-flow update, disk-span and request logs, the mock's logs and the runner's step reports: [before](https://github.com/Ameyanagi/ReShiki-evidence/blob/bd2eedd767246a97c236fe4741b0665ac962f251/pr-reviews/perf-github-lag-step2/timing-before/summary.txt) ([report](https://github.com/Ameyanagi/ReShiki-evidence/blob/bd2eedd767246a97c236fe4741b0665ac962f251/pr-reviews/perf-github-lag-step2/timing-before/report.md)), [after](https://github.com/Ameyanagi/ReShiki-evidence/blob/bd2eedd767246a97c236fe4741b0665ac962f251/pr-reviews/perf-github-lag-step2/timing-after/summary.txt) ([report](https://github.com/Ameyanagi/ReShiki-evidence/blob/bd2eedd767246a97c236fe4741b0665ac962f251/pr-reviews/perf-github-lag-step2/timing-after/report.md)), [protocol](https://github.com/Ameyanagi/ReShiki-evidence/blob/bd2eedd767246a97c236fe4741b0665ac962f251/pr-reviews/perf-github-lag-step2/protocol.md), analysis script [analyze3.py](https://github.com/Ameyanagi/ReShiki-evidence/blob/bd2eedd767246a97c236fe4741b0665ac962f251/pr-reviews/perf-github-lag-step2/analyze3.py).

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | pass · fmt, workspace + wasm32 clippy, lib/bin and renderer tests, Python, docs checks |
| PR CI | pending |

macOS arm64 (Apple M4), every run with a fresh `RESHIKI_DATA_DIR` and the InChI and naming helpers pointed at the built binary:

- Before the rebase onto main, at `c929c8cf` (now `915e7764`): `cargo fmt --all --check`; workspace clippy `--all-targets --all-features -D warnings`; wasm32 clippy as in checks.yml; Python unittest via `uv run --locked` (292 run, 9 skipped; the InChI helper protocol tests pointed at the built binary); `module_index.py --check`; `copy_lint.py`; `assemble_changelog.py --check`; `check_docs_tree.mjs`; `bun run docs:check`; the GitHub tests (86 lib + 149 app).
- At `cb1bc7a3` (now `3c946f55`; the same code but for the History follow-up, whose tests are in the GitHub set above): `cargo test --locked --no-default-features -p reshiki --lib --bins` (497 lib + 1817 bin passed) and the renderer tests `--bin reshiki -- --include-ignored --test-threads=1 --skip manual_` (1974 passed).
- After rebasing onto main (`4ffd8deb`, one conflict in `github_signed_out` beside the star reset): fmt, workspace clippy and the GitHub tests again (86 lib + 150 app).

New tests: the read begun last wins and a write beats older reads; a save reads back only its own drawing, counted unsent at once; opening from the picker writes off the window's thread and opens once written; Update never writes over a change made in another app and then shows Review; a Send and closing the window wait for Update's write; History lists without reading any drawing, reads one when its row shows and never twice; a drawing's History shows again at once with what was read, and a newer commit comes first; signing out forgets what History kept and what it shows; a drawing whose row left the list is asked again when it shows; listing from a branch is one request and a commit's drawing is asked once (counted with the mock's request log).

## Reviews

Two adversarial passes by a second model (gpt-6.2-sol), focused on data loss, write ordering, stale cache and cross-account leaks.

- First pass: an edit made while Update writes was marked saved; a save answering a close skipped the Send question; quit could beat the `state.json` write after a working-copy write. All three fixed with tests in `3c946f55`. It also raised races that need a second action within a write's milliseconds; see Risk.
- Second pass: History could skip a version when the branch moved between pages, and leave a row's drawing unread if the row left the first page while it was read; the versions on screen stayed after signing out. Fixed with tests in `915e7764`. Its other points repeat the first pass's millisecond races or behaviour this change did not alter (listed under Risk).

## Risk

- An edit made to a working copy in another app is seen on window focus, when a drawing opens, or by Send itself, no longer on every save or tab close. Send always reads the files.
- A Send pressed while a working copy is being written starts some milliseconds later.
- Races that need a second action inside a write's 10–20 ms, explained rather than handled:
  - **A save landing between Update's check and its write.** Update writes only a drawing with no unsaved edits, and an edit made meanwhile keeps the tab unsaved (tested), so this needs an edit *and* a completed save inside the write. Opening from the picker only writes a drawing that is not open in a tab.
  - **Dismissing the conflict dialog, editing and saving while the choice is written.** The choice was made on what the dialog showed; the window would need a save to land within the write.
  - **Signing out and in as another account while a Send waits for a write.** A deferred Send that finds no sign-in is dropped; a new sign-in takes seconds.
- An app changing the files in ReShiki's data folder while ReShiki stays in front: Send still reads and sends them, as it already did for a change made after the Send box opened; the Send box lists them after the next focus or open.
- History reads each preview only when its row shows; a row scrolled past quickly is read once it is on screen.
- Returning to a drawing's History draws its remembered previews in one frame (115 ms for 12 here, two of them C60 drawings).
- Not handled, as before this change: quitting while a picker download is still on the network (not yet writing), and a `state.json` write that fails (its error shows; the close is not held for a retry).

## Changelog

- Opening a drawing from GitHub, **Update** and a conflict choice no longer pause the window while the drawing is written, and saving a GitHub drawing checks only that drawing for unsent changes.
- **History** lists GitHub's versions as soon as they arrive, fills in each picture as its row comes into view, and shows a drawing's History again at once.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

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
- **Quitting never drops a write in flight.** If the window is closed while a write runs, the close waits (`quit_after`) and starts again once the write has landed, so the Send question still sees what was written. Every write is atomic (temporary file, `fsync`, rename, folder `fsync`), as before: a crash mid-write leaves the old file or the new one.
- **What did not change:** `send::outgoing` still reads and hashes every unsent file from disk when a Send starts, so what is sent is decided by the files, not by the cached hashes. The `state.json` write after a checkout is asynchronous, as it already was.

### 2. History lists first, reads previews as rows show

- GitHub's versions are listed from the branch in one request (`commits?sha=<branch>&path=…`), instead of branch → commit → list. **Load more** counts pages from the branch too; a commit made in between shifts a page by one, and the duplicate is dropped.
- No version drawing is read when the list arrives. Each row without its drawing is wrapped in a `sensor`; the drawing is asked for once, when the row first comes into view (100 px ahead). `api::raw_at` asks by commit, so its reply is kept in the session cache.
- A drawing's list and the drawings read so far are kept per drawing for the session (`Versions::kept`) and shown at once when its History opens again, while the list is asked again. Commit SHAs never change, so a kept drawing is never stale. Signing out forgets them, and only a list read while signed in is kept, so another account never sees them.

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
- Per-flow update, disk-span and request logs, the mock's logs and the runner's step reports: [before](https://github.com/Ameyanagi/ReShiki-evidence/blob/98f642beddd635492d988fe9cca56797f530b061/pr-reviews/perf-github-lag-step2/timing-before/summary.txt) ([report](https://github.com/Ameyanagi/ReShiki-evidence/blob/98f642beddd635492d988fe9cca56797f530b061/pr-reviews/perf-github-lag-step2/timing-before/report.md)), [after](https://github.com/Ameyanagi/ReShiki-evidence/blob/98f642beddd635492d988fe9cca56797f530b061/pr-reviews/perf-github-lag-step2/timing-after/summary.txt) ([report](https://github.com/Ameyanagi/ReShiki-evidence/blob/98f642beddd635492d988fe9cca56797f530b061/pr-reviews/perf-github-lag-step2/timing-after/report.md)), [protocol](https://github.com/Ameyanagi/ReShiki-evidence/blob/98f642beddd635492d988fe9cca56797f530b061/pr-reviews/perf-github-lag-step2/protocol.md), analysis script [analyze3.py](https://github.com/Ameyanagi/ReShiki-evidence/blob/98f642beddd635492d988fe9cca56797f530b061/pr-reviews/perf-github-lag-step2/analyze3.py).

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | GitHub tests and fmt pass; full checks running |
| PR CI | pending |

macOS arm64: `cargo test --locked --no-default-features -p reshiki --lib --bins github` (86 lib + 148 app GitHub tests) and `cargo fmt --all --check` pass; the full check list (workspace and wasm32 clippy, all lib/bin tests, renderer tests, Python, docs) is running and this section is updated when it lands. Every run with a fresh `RESHIKI_DATA_DIR`.

New tests: the read begun last wins and a write beats older reads; a save reads back only its own drawing, counted unsent at once; opening from the picker writes off the window's thread and opens once written; Update never writes over a change made in another app and then shows Review; a Send and closing the window wait for Update's write; History lists without reading any drawing, reads one when its row shows and never twice; a drawing's History shows again at once with what was read, and a newer commit comes first; signing out forgets what History kept; listing from a branch is one request and a commit's drawing is asked once (counted with the mock's request log).

## Risk

- An edit made to a working copy in another app is seen on window focus, when a drawing opens, or by Send itself, no longer on every save or tab close. Send always reads the files.
- A Send pressed while a working copy is being written starts some milliseconds later.
- Races that need a second action inside a write's 10–20 ms, explained rather than handled:
  - **A save landing between Update's check and its write.** Update writes only a drawing with no unsaved edits, and an edit made meanwhile keeps the tab unsaved (tested), so this needs an edit *and* a completed save inside the write. Opening from the picker only writes a drawing that is not open in a tab.
  - **Dismissing the conflict dialog, editing and saving while the choice is written.** The choice was made on what the dialog showed; the window would need a save to land within the write.
  - **Signing out and in as another account while a Send waits for a write.** A deferred Send that finds no sign-in is dropped; a new sign-in takes seconds.
- An app changing the files in ReShiki's data folder while ReShiki stays in front: Send still reads and sends them, as it already did for a change made after the Send box opened; the Send box lists them after the next focus or open.
- History reads each preview only when its row shows; a row scrolled past quickly is read once it is on screen.

## Changelog

- Opening a drawing from GitHub, **Update** and a conflict choice no longer pause the window while the drawing is written, and saving a GitHub drawing checks only that drawing for unsent changes.
- **History** lists GitHub's versions as soon as they arrive, fills in each picture as its row comes into view, and shows a drawing's History again at once.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

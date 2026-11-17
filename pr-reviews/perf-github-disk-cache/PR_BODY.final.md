## Why it matters

Steps 1 (#1219) and 2 (#1229) made the GitHub integration fast while ReShiki runs, but everything they keep lives in memory. After a restart, choosing a repository opened yesterday downloads its whole tree, every folder, every tile's preview and last commit, and History's previews again: 7–30 requests per flow at 80–150 ms each, plus a connection handshake.

This is the last part of the GitHub lag plan the owner approved on 2026-11-18 (the disk cache step 2 proposed).

## Approach

- **Under the session cache, not beside it.** `Client::get_kept` (step 1's cache of what GitHub never changes) now looks in memory, then on disk, then asks GitHub, and keeps what it reads in both. One new module, `src/github/cache.rs`.
- **What is kept, and how it stays right.**
  - Objects by name (trees, blobs, commits by SHA, a file at a commit, a file's last commit as of a commit) never change, so they are used from disk with no request.
  - Every other GET (a branch head, a repository, the account's repositories, a drawing's History list) is kept with GitHub's `ETag` and asked again each time with `If-None-Match`. GitHub's 304 means unchanged and costs no download; anything else replaces the entry. Nothing that can change is ever used without asking, so a moved branch, Send's conflict check and the window-focus check see what they saw before.
- **Where.** `cache/github/<login>/` in the data folder: `~/.reshiki/cache/github/` on macOS and Linux, `%LOCALAPPDATA%\reshiki\ReShiki\cache\github\` on Windows (the existing `compatibility::cache_directory()`). Signed-out reading keeps its own in `_public/`: a client keeps only logins of letters, digits, hyphens and underscores (as GitHub names accounts, managed users included) and never one named `_public`, so no account shares it. One folder per account keeps one account's private repositories from another, so signing out clears nothing. With `RESHIKI_GITHUB_API` or `RESHIKI_GITHUB_WEB` set, replies go to `cache/github-<hash of the API address>/`, so a test server's never pass for GitHub's or another's (and an address's credentials never name a folder).
- **Size.** 200 MB in total; past it, the entries used least recently (file modified time, set on every read) go until 180 MB are left, so the next writes list nothing. Writing an entry again counts only the difference. Eviction lists only real account folders, never through a link, so it can never remove a file outside the cache.
- **Robustness.** An entry is `<SHA-256 of the rest>\n<ETag>\n<reply>`, written to a temporary file and renamed into place, with no `fsync`: an entry cut short by a crash fails its sum. Any entry that fails to read or to match its sum (reply or ETag) is removed and read from GitHub again; nothing here is shown to the user. A read that finds no entry removes nothing, so an entry written meanwhile stays. Reads and writes run in `spawn_blocking`, off the window's thread.
- **The mock** answers every GET with an `ETag` and an `If-None-Match` that matches with 304, as GitHub does, and counts those.

## Before/after timings

Release builds of `04e88c10` (main, before) and this branch at `4ebbb35b` (after; later commits change folder names, the entry checksum and eviction bookkeeping, not what is requested), each with step 2's throwaway probe (never pushed), on macOS arm64 (Apple M4) against the same local mock GitHub: 80–150 ms per reply, plus two more delays on a connection's first reply for TCP + TLS. Each build launched twice with its own data folder: part A fills the caches (sign in, pick `group-drawings`, open `routes`, the 240-file folder, `drawing-01` and its History), then the app is quit and launched again, and part B repeats the same steps. The same protocol drove both builds through a second agent with computer use. Times run from the input to the first frame after the flow's last reply; "names" is when the folder's names (or History's rows) first show.

**After a restart (part B):**

| Flow | Before | After | Requests before → after |
|---|---|---|---|
| Open the picker (the account's repositories, then the last repository's head and folders) | names 338 ms, settled 397 ms | **127 ms**, 336 ms | 7 → 4, **all 304**; 3 from disk |
| Choose the same repository | 98 ms | 115 ms | 1 → 1, the branch head (304) |
| Open `routes` (6 drawings: names, dates, previews) | names 142 ms, settled 317 ms | **33 ms, 56 ms** | **13 → 0**; 13 from disk |
| Open the 240-file folder (pasted link) | names 399 ms, settled 708 ms | **123 ms, 215 ms** | **29 → 1** (the branch head, 304); 28 from disk |
| Open `drawing-01` from the picker | 106 ms | 80 ms | 0 → 0 (its preview had read it) |
| History of `drawing-01` (12 versions) | rows 117 ms, settled 337 ms | rows 134 ms, **225 ms** | **13 → 1** (the list, 304); 12 previews from disk |
| Launch to first frame | 500 ms | 348 ms | – |

**First launch (part A), cache empty:** the same requests in both builds (choose repository 4, `routes` 13, 240-file folder 30, History 13), and settled times within the mock's noise (`routes` 318 → 303 ms, 240 files 794 → 837 ms, History 348 → 346 ms). Writing the cache costs no request and no time on the window's thread.

- **Disk work:** 128 reads (0.9 ms on average, 6.3 ms at most) and 63 writes (1.8 ms on average, 14.4 ms at most), every one on a background thread; no update on the window's thread grew. After both launches the cache held 740 KB.
- The branch head is still asked each time a repository is picked, as before, so a new commit shows at once; GitHub answers 304 when it has not moved.
- Opening a drawing makes no request in either build: its tile preview already read it.
- Per-flow request, update and disk-span logs, the mock's logs and the runner's step reports: [before](https://github.com/Ameyanagi/ReShiki-evidence/blob/62b3b2e2673a58070758970432c5d34ae706522e/pr-reviews/perf-github-disk-cache/timing-before/summary.txt) ([report](https://github.com/Ameyanagi/ReShiki-evidence/blob/62b3b2e2673a58070758970432c5d34ae706522e/pr-reviews/perf-github-disk-cache/timing-before/report.md)), [after](https://github.com/Ameyanagi/ReShiki-evidence/blob/62b3b2e2673a58070758970432c5d34ae706522e/pr-reviews/perf-github-disk-cache/timing-after/summary.txt) ([report](https://github.com/Ameyanagi/ReShiki-evidence/blob/62b3b2e2673a58070758970432c5d34ae706522e/pr-reviews/perf-github-disk-cache/timing-after/report.md)), [protocol](https://github.com/Ameyanagi/ReShiki-evidence/blob/62b3b2e2673a58070758970432c5d34ae706522e/pr-reviews/perf-github-disk-cache/protocol.md), analysis script [analyze4.py](https://github.com/Ameyanagi/ReShiki-evidence/blob/62b3b2e2673a58070758970432c5d34ae706522e/pr-reviews/perf-github-disk-cache/analyze4.py).

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | running |
| PR CI | running |

New tests (lib, against the mock and its request log):

- after a restart (a new client and session over the same folder) choosing the repository, opening a folder, its dates and a drawing ask only for the branch head, which the mock answers 304;
- a branch that moved is read again and kept with its new ETag, and a refusal (404) is never answered from what was kept;
- a drawing changed on GitHub reads new after a restart, by download and in History's list;
- trees and blobs are read from disk with no request;
- each account and signed-out reading keep their own: account B never sees A's, a managed user's login gets its own folder, and a login named `_public` is kept nowhere;
- past the cap the least recently used go first (times set a minute and a second apart, so no clock's resolution matters), and writing an entry again evicts nothing;
- an entry that is garbage, cut short, empty or has a damaged ETag is a miss and removed; through a client it is read again and kept again;
- eviction never reaches through a linked folder (Unix).

App: a new app reads what an earlier run kept on disk, signed out and signed in, with GitHub unreachable (`a_new_app_reads_what_github_sent_before_from_the_data_folder`).

## Reviews

Two adversarial passes by a second model (gpt-6.2-sol), focused on stale data versus conflict detection, cross-account leaks, atomicity and eviction races. Both found no path where a cached reply hides a moved branch from Send, the window-focus check or History: everything that can change is asked again.

- First pass, fixed in `0a819d3d`: an ETag damaged on disk (the sum covered only the reply) could make one request unsendable, now a miss; a miss that found nothing could remove an entry written meanwhile; one shared `github-override` folder for every test server, now one per server address; only GitHub-shaped logins name folders.
- Second pass, fixed in `6651d5c7` with tests: eviction followed a linked account folder and could remove files elsewhere; a replaced entry was counted twice and could evict below the cap; a test server's address (which may hold credentials) named its folder, now a hash; managed users' logins (with `_`) got no cache. The LRU test now sets times far apart.
- Explained rather than handled (see Risk): a renamed account's old login on a commit's tile, a login reassigned to someone else on the same computer account, two processes over the cap, a damaged entry removed just as another task rewrites it (one extra download), the cache folder resolved at startup with the same few `stat`s the working-copy folder already makes.

## Risk

- Disk use: up to about 200 MB more in the data folder. Deleting `cache/` at any time is safe.
- A login renamed on GitHub starts a new folder; the old one ages out by LRU. A login GitHub later gives to someone else, who signs in on the same computer account, would find the old folder; every way the app reaches a kept object starts with a live request for the branch or repository, which that person's sign-in would be refused.
- What never changes is never asked again, so a commit's tile keeps the GitHub login it was first shown with if that account is renamed, and a drawing listed while its repository was public opens from the disk, without asking again, if the repository turns private while the picker shows it. The session cache already behaved this way within a run.
- Two ReShiki windows of different processes share the folder: writes are atomic, and the size each counts is corrected at its next eviction, so the folder can pass 200 MB by what the other wrote until then.

## Changelog

- **Open from GitHub…** remembers what GitHub sent across restarts. Choosing a repository you opened before asks GitHub only whether its branch moved, and its folders, previews and drawings open without downloading them again. The cache keeps up to 200 MB in the data folder, one folder per GitHub account, and can be deleted at any time.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

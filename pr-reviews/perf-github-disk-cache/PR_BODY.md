## Why it matters

Steps 1 (#1219) and 2 (#1229) made the GitHub integration fast while ReShiki runs, but everything they keep lives in memory. After a restart, choosing a repository opened yesterday downloads its whole tree, every folder, every tile's preview and last commit, and History's previews again: 7–30 requests per flow at 80–150 ms each, plus a connection handshake.

This is the last part of the GitHub lag plan the owner approved on 2026-11-18 (the disk cache step 2 proposed).

## Approach

- **Under the session cache, not beside it.** `Client::get_kept` (step 1's cache of what GitHub never changes) now looks in memory, then on disk, then asks GitHub, and keeps what it reads in both. One new module, `src/github/cache.rs`.
- **What is kept, and how it stays right.**
  - Objects by name (trees, blobs, commits by SHA, a file at a commit, a file's last commit as of a commit) never change, so they are used from disk with no request.
  - Every other GET (a branch head, a repository, the account's repositories, a drawing's History list) is kept with GitHub's `ETag` and asked again each time with `If-None-Match`. GitHub's 304 means unchanged and costs no download; anything else replaces the entry. Nothing that can change is ever used without asking, so a moved branch, Send's conflict check and the window-focus check see what they saw before.
- **Where.** `cache/github/<login>/` in the data folder: `~/.reshiki/cache/github/` on macOS and Linux, `%LOCALAPPDATA%\reshiki\ReShiki\cache\github\` on Windows (the existing `compatibility::cache_directory()`). Signed-out reading keeps its own in `_public/` (no GitHub login has an underscore). One folder per account keeps one account's private repositories from another, so signing out clears nothing. With `RESHIKI_GITHUB_API` set, replies go to `cache/github-override/`, so a test server's never pass for GitHub's.
- **Size.** 200 MB in total; past it, the entries used least recently (file modified time, set on every read) go until 180 MB are left, so the next writes list nothing.
- **Robustness.** An entry is `<SHA-256 of the reply>\n<ETag>\n<reply>`, written to a temporary file and renamed into place, with no `fsync`: an entry cut short by a crash fails its sum. Any entry that fails to read or to match its sum is removed and read from GitHub again; nothing here is shown to the user. Reads and writes run in `spawn_blocking`, off the window's thread.
- **The mock** answers every GET with an `ETag` and an `If-None-Match` that matches with 304, as GitHub does, and counts those.

## Before/after timings

TIMINGS_PENDING

## Verification

VERIFICATION_TABLE

New tests (lib, against the mock and its request log): after a restart only the branch head is asked and the mock answers 304; a branch that moved is read again and kept with its new ETag; trees and blobs are read from disk with no request; each account and signed-out reading keep their own (account B never sees A's); past the cap the least recently used go first; an entry that is garbage, cut short or empty is a miss and removed, and through a client it is read again and kept again. App: a new app reads what an earlier run kept, signed out and signed in, with GitHub unreachable.

## Risk

- Disk use: up to about 200 MB more in the data folder. Deleting `cache/` at any time is safe.
- A login renamed on GitHub starts a new folder; the old one ages out by LRU.
- Two ReShiki windows of different processes share the folder: writes are atomic, and the size each counts is corrected at its next eviction, so the folder can pass 200 MB by what the other wrote until then.

## Changelog

- **Open from GitHub…** remembers what GitHub sent across restarts. Choosing a repository you opened before asks GitHub only whether its branch moved, and its folders, previews and drawings open without downloading them again. The cache keeps up to 200 MB in the data folder, one folder per GitHub account, and can be deleted at any time.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

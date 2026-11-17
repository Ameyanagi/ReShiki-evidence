> **Draft.** The before/after timing table, evidence, full check suite and adversarial review below are **pending**; this PR is opened early so CI runs in parallel.

## Why it matters

The GitHub integration feels slow. Measured with a local mock of GitHub at 80–150 ms per reply, almost all of the lag is network round trips the app makes one after another, not CPU: at 0 ms every flow settles in under 0.2 s, at ~120 ms the same flows take 0.3–1.5 s while the UI thread is idle.

- Opening a drawing from the picker made 5–6 sequential requests (ref, commit, one tree per folder level, blob) for things the picker already knew: ~0.7 s.
- reqwest was built without HTTP/2, so every parallel preview/date request opened its own TCP + TLS connection: a 6-file folder took ~0.6 s and the 240-file folder ~1.5 s, and the file names stayed hidden until the slowest date arrived.
- Going up a folder, back into it, or choosing the same repository again re-fetched everything.
- Send made 10 strictly sequential requests (~1.5 s), and the chip said nothing while it saved first.

This is step 1 of the plan the owner approved on 2026-11-17. Not in this PR: moving working-copy writes and unsent scans off the UI thread, History, and a disk cache with ETags (step 2).

## Approach

1. **HTTP/2 and one transport.** reqwest gains its `http2` feature (still rustls with the ring provider through `crate::http::client()`; the lockfile still has no aws-lc). One `reqwest::Client` is shared by the signed-in client, signed-out public reads and sign-in polling (`github::client::http`), and signed-out reading keeps one `Client` for the session. Real api.github.com negotiates h2 over ALPN; the local mock stays HTTP/1.1 and works unchanged.
2. **Open by blob.** Opening from the picker reads the file by the blob SHA the listing named (`api::download_listed`): one request, or none when the preview already read those bytes. The working copy's base is the listing's commit and blob.
3. **Names at once.** The "hide files until the slowest date arrives" barrier is gone. A folder shows folders first, then files by name; who changed each file and its preview fill in as they arrive and nothing reorders. Dates are asked with `per_page=1` as of the listed commit (`api::last_commit`), and a folder you return to reuses the dates it already has. A date request that fails is asked again the next time the file shows; one with no history is not.
4. **Session cache.** Replies GitHub never changes (commits, trees and blobs by SHA, and a file's last commit as of a commit) are kept per client for the app session, up to 64 MB, least recently used first. Branch refs and the repository are never cached, so choosing a repository still re-checks its head and new commits show. Nothing is written to disk.
5. **Parallel Send.** Drawing and SVG blobs upload four at a time (`buffered(4)`, results in input order); tree → commit → ref order, the conflict checks and the reuse of uploaded blobs on a branch-race retry are unchanged. The chip says **Saving…**, then **Sending…**, from the moment Send is pressed.

### Why conflict detection stays safe

Opening from the listing records the listing's commit and the file's blob as the working copy's base, exactly what the old five-request path would have recorded had the branch not moved in between. If the branch moved after the listing, Send still reads the branch head fresh, walks its tree and compares that file's blob with `base_blob`: a different blob is a conflict, as before. The focus check (`newer`) also compares against the same base, so it offers **Update**. The cache only holds content addressed by an immutable SHA; refs, the repository and anything named by a branch are always asked.

## Before/after timings

_Pending: release builds of main and this branch with throwaway instrumentation, mock at 80–150 ms with handshake simulation, same flows and machine as the earlier measurement._

## Evidence

_Pending._

## Verification

VERIFICATION_TABLE

_Pending: full macOS arm64 check suite and adversarial review._

## Risk

- Name order replaces newest-first in the picker (the approved plan chose a stable order so nothing moves under the pointer).
- Memory: at most 64 MB of cached replies per client for the session.
- A shared transport across clients: tokens and reply caches stay per `Client`; only connections are pooled.

## Changelog

- **Open from GitHub…** feels faster. A folder's files show as soon as it is listed, folders first, then by name; who changed each file and its preview fill in as they arrive, and no tile moves under the pointer.
- Opening a drawing from the picker reads only the drawing, and nothing at all once its preview has loaded. Going back up, into a folder again or choosing the same repository again no longer waits for GitHub.
- **Send** uploads several drawings at once, and the status bar chip says **Saving…**, then **Sending…**, from the moment you press it.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

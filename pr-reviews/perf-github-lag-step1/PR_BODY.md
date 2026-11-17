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

Release builds of `dc6a5408` (main, before) and `14ee832d` (this branch, after), each with the same throwaway timing instrumentation (never pushed), run on macOS arm64 (Apple M4) against the same local mock of GitHub: 80–150 ms per reply, plus two more delays on a new connection's first reply to stand in for TCP + TLS. Real GitHub negotiates HTTP/2 over TLS (ALPN); the mock is plain http, so the after build talks HTTP/2 to it by prior knowledge to match. One protocol, the same flows in the same order, driven by a second agent with computer use. Times run from the input to the first frame after the last reply; "names" is when the file names first show.

| Flow | Before | After | Requests before → after (cached) | New connections |
|---|---|---|---|---|
| Choose a repository | 314 ms folders, 411 ms settled | 399 ms, 507 ms | 4 → 4 | 0 → 0 |
| Open `routes` (6 drawings) | **664 ms names** (hidden until the dates arrived), 664 ms settled | **122 ms names**, 301 ms settled | 13 → 13 | 11 → 0 |
| Up one level | 158 ms | **20 ms** | 1 → 0 (1) | 0 → 0 |
| Open `routes` again | 280 ms | **35 ms** | 7 → 0 (1) | 0 → 0 |
| Choose the same repository again | 455 ms | **151 ms** | 4 → 1, the branch head (3) | 0 → 0 |
| Open the 240-file folder (pasted link) | **1125 ms names**, 1125 ms settled | **504 ms names**, 849 ms settled | 30 → 30 | 12 → 0 |
| Scroll one screen in it | 198 ms | 205 ms | 24 → 24 | 0 → 0 |
| Open a drawing from the picker | **665 ms** | **52 ms** | 5 → 0 (1, the preview's blob) | 0 → 0 |
| Send one drawing | **1542 ms** | **974 ms** | 11 → 8 (3) | 2 → 1 |
| Open the picker (account re-list, unchanged) | 352 ms | 369 ms | 3 → 3 | 0 → 0 |

- "Choose a repository" makes the same 4 sequential requests in both builds (the head is always re-checked); the difference is the mock's random 80–150 ms per reply. Scrolling makes the same requests and lands within noise too.
- The slowest `App::update` in any flow stayed under 18 ms in both builds (opening a drawing: 17.4 → 12.7 ms, the working-copy write; moving it off the UI thread is step 2).
- Per-flow request lists, probe logs, mock logs and the runner's step report: [before](timing-before/summary.txt) ([requests](timing-before/requests.txt), [report](timing-before/report.md)), [after](timing-after/summary.txt) ([requests](timing-after/requests.txt), [report](timing-after/report.md)), [protocol](protocol.md), analysis scripts [analyze2.py](analyze2.py) and [scroll.py](scroll.py).
- **Real GitHub:** `curl --http2` to `https://api.github.com/` answers over HTTP/2, and the network test `http::tests::ring_completes_a_handshake_with_the_release_server`, which builds the app's own rustls/ring client, now also asserts `HTTP_2` against api.github.com; it passed on macOS arm64. Signed-out, read-only, no account.
- **Binary size:** the two stripped release probe builds are 80,340,896 → 81,144,720 bytes (+785 KiB, +1.0%), almost all of it the `h2` crate. The lockfile still has no aws-lc.

## Verification

VERIFICATION_TABLE

macOS arm64 at `14ee832d`: `cargo fmt --all --check`; workspace clippy `--all-targets --all-features -D warnings`; wasm32 clippy as in checks.yml; `cargo test --locked --no-default-features -p reshiki --lib --bins` (497 lib + 1807 bin passed); renderer tests `--bin reshiki -- --include-ignored --test-threads=1 --skip manual_` (1960 passed); the ignored network test above; Python unittest (288; the InChI helper protocol module needs a built helper and passed with it pointed at the built binary); `module_index.py --check`; `copy_lint.py`; `assemble_changelog.py --check`; `check_docs_tree.mjs`; `bun run docs:check`. InChI and naming helpers pointed at the built binary; every run with a fresh `RESHIKI_DATA_DIR`.

New tests, counting requests with the mock's request log: names show before their dates and open at once; dates fill in without moving a tile; a folder opened again asks for no date twice; a date that failed is asked again, one with no history is not; files open as listed at the repository's commit; a listed file opens by its blob alone, and with no request once its preview was read; a drawing opened from an older listing meets the change on Send as a conflict; what never changes is asked once and the branch every time; a file's last change is one `per_page=1` request; the reply cache is bounded and evicts least recently used first; uploads go four at a time, then tree, commit and branch in that order; the chip says **Saving…** then **Sending…** from the moment Send is pressed.

Reviews: two adversarial passes by a second model, focused on caching versus conflict detection, stale data and concurrency. The first found one low-severity regression (a date request that failed was never asked again until the repository was chosen again); it is fixed with a failing-first test in `2b49dd3c`. The second pass found nothing to change. The pre-push clippy hook then caught indexing in the Send upload pairing, fixed in `14ee832d`.

## Risk

- Name order replaces newest-first in the picker (the approved plan chose a stable order so nothing moves under the pointer).
- Memory: at most 64 MB of cached replies per client for the session.
- A date request that keeps failing (offline) is asked again each time its tile shows; it is never retried on its own.
- A shared transport across clients: tokens and reply caches stay per `Client`; only connections are pooled.

## Changelog

- **Open from GitHub…** feels faster. A folder's files show as soon as it is listed, folders first, then by name; who changed each file and its preview fill in as they arrive, and no tile moves under the pointer.
- Opening a drawing from the picker reads only the drawing, and nothing at all once its preview has loaded. Going back up, into a folder again or choosing the same repository again no longer waits for GitHub.
- **Send** uploads several drawings at once, and the status bar chip says **Saving…**, then **Sending…**, from the moment you press it.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

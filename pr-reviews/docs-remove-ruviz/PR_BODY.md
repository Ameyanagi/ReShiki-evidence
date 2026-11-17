## Why it matters

`docs/ruviz-integration.md` describes what ReShiki would need from ruviz, a separate plotting library, for a future spectrum panel. ReShiki never depended on ruviz: no crate uses it and `Cargo.lock` has no ruviz entry. The page was included by mistake and shows up in the developer docs as if it were an integration.

## Approach

- Delete `docs/ruviz-integration.md`.
- Remove its website sidebar entry and its old `/reference/ruviz-integration` redirect (`website/astro.config.mjs`).
- Drop the sentence in `docs/changes/capabilities.md` that pointed to it.

The frozen hash list in `tests/fixtures/nmr/mock-alignment/evidence/build/source-manifest.json` still names the file. It is an evidence snapshot of an older worktree and is left as is.

## Evidence

`ruviz` references before and after, and the `Cargo.lock` count: [grep.txt](grep.txt)

## Verification

VERIFICATION_TABLE

macOS arm64: `bun scripts/check_docs_tree.mjs`, `python3 scripts/copy_lint.py`, `bun run docs:check` (0 errors, 0 warnings). A Codex review found no remaining reference outside the frozen evidence fixture.

## Risk

Very low; docs only. `tests/fixtures/nmr/mock-alignment/verify_evidence.py` re-hashes every file of that frozen snapshot, so it now also reports this file as missing. It is a manual script (no CI job runs it) and already fails on main because other docs changed since the snapshot.

## Changelog

None; developer docs only.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

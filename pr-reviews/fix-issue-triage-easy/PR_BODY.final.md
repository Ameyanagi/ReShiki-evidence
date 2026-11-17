## Summary

Five small, independent fixes from the open-issue triage, approved by the owner on 2026-11-18. Each has its own commit.

- Fixes #1160: an Arial added with `addFont` is used instead of the bundled stand-in.
- Refs #1183: Python and `reshiki --cli` read the editable drawing inside a ReShiki PNG, SVG or PDF (read side only).
- Refs #88: the porphine template's round-trip test covers CDX and checks the two N–H sites (test only).
- Refs #431: `<reshiki-editor>` loads a changed `src` or `format`, after a cancelable `beforeload` event.
- Refs #430: "Opening…" and "Preparing … export…" show before the browser's page thread is held (partial).

Evidence and verification are being collected; this description is filled in before the PR leaves draft.

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | in progress |
| PR CI | pending |

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none added.

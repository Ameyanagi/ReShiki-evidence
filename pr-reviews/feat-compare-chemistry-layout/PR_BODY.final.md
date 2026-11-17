## Why

History's **Compare** and the **changed on GitHub** dialog compare each saved object as a whole, positions included. Moving one molecule, or the whole scheme, paints every atom and bond as changed, so a real chemical edit is lost in the noise and "is it still the same compound?" has no answer.

## Approach

This is C1 of two PRs: the core.

- **`reshiki::compare`** (new, pure, in `crates/model`) takes two documents and returns a structured report: matched molecules, typed changes per object (chemical, reaction role, added, removed, couldn't verify, whole scheme moved, moved, rotated, redrawn, style, text), the fit of each object, and the right side lined up with the left. One object can carry several kinds.
- **Matching:** molecules (connected atoms, as `reactions::molecules` builds them) by shared ids, accepted only with a bond both sides keep, so a reused id is not a match; then by canonical isomeric SMILES, duplicates by distance once the common move is removed. Text, arrows and graphics by id, then by content and place.
- **Chemistry** is compared over the prepared, sanitized structure (`chemistry::document::prepare`): aromatic vs Kekulé, which bond carries the wedge, a collapsed label and refreshed CIP/H labels are not changes; isotopes, charges, H counts and stereo (including unknown stereo and AND/OR groups) are. Generic structures and anything that cannot be prepared are **Couldn't verify**, never equal. For an id-matched molecule the edit is local: only the atoms and bonds that changed are painted.
- **Layout:** a proper 2D Kabsch fit (no reflection, no scale) per matched object. RMS ≤ 0.01 and max ≤ 0.03 bond lengths is a rigid move; more, with the same chemistry, is a redraw. A move that at least two objects and three in four share is one **Whole scheme moved** line.
- **UI:** a verdict badge, **Chemistry / Layout / Everything** (Everything by default) with counts, **Line up moved molecules** (on by default), colours plus text tags (CHEM, MOVED, STYLE, TEXT, RXN, ADDED, REMOVED, SAME, ?), **What changed** with SMILES before → after, click a line to point at it in both panes, and a legend. The marks are a transient layer; neither drawing, nor its own highlights, is changed.
- **Background:** the comparison runs in `spawn_blocking`, tagged with a generation so a late result never replaces a newer comparison; the dialog says **Comparing…** meanwhile.

## Evidence

_Pending: real window captures, before (main) and after, of History → Compare and the changed-on-GitHub dialog, for whole scheme moved, moved + NO₂ added, and cleanup/redraw; after in Everything, Chemistry and Layout, line-up on and off, light and dark._

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | pending · model compare tests 28/28 pass; full checks pending |
| PR CI | pending |

## Risk

- Matching a molecule whose ids changed **and** whose chemistry changed is left to C2: it shows as removed and added.
- A mirrored or scaled molecule shows as redrawn (C2 gives them their own kinds).
- The verdict follows ReShiki's own chemistry model; drawings it cannot prepare are reported as unverified rather than guessed.

## What C2 will add

- Re-import matching by substructure when ids changed.
- Mirror and scale as their own kinds.
- Atom-number wording ("OH added at C4").

## Changelog

`docs/changes/unreleased/feat-compare-chemistry-layout.md`

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

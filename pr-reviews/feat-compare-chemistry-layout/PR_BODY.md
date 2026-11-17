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

Real window captures from macOS arm64, of a debug build of `main` (before) and of this branch (after), driven against ReShiki's local mock GitHub with a fresh data folder. Scheme: acetic acid + ethanol → ethyl acetate + water. Each scenario has the original commit and a change; History compares the original with the drawing now, and the changed-on-GitHub dialog shows GitHub's original beside yours.

### 1. Whole scheme moved

| Before (`main`) | After |
|---|---|
| ![before](before/history-moved.png) | ![after](after/history-moved-everything.png) |

Before: every atom, bond, label and the arrow are painted. After: **Chemically identical**, one **MOVED · Whole scheme moved** line (1.3 cm left, 0.5 cm down), nothing painted. [Chemistry](after/history-moved-chemistry.png) · [Layout](after/history-moved-layout.png) · [line-up off](after/history-moved-original-positions.png) · [changed-on-GitHub, after](after/conflict-moved-everything.png) · [before](before/conflict-moved.png)

### 2. Moved, plus NO₂ added

| Before (`main`) | After |
|---|---|
| ![before](before/history-nitro.png) | ![after](after/history-nitro-everything.png) |
| ![before](before/conflict-nitro.png) | ![after](after/conflict-nitro-everything.png) |

After: **1 chemical change**. The CHEM row says **NO₂ added** with SMILES before → after, and only the nitro group and its carbon are painted; the move is one line.

| Chemistry | Layout | Line up off | Row clicked |
|---|---|---|---|
| ![](after/history-nitro-chemistry.png) | ![](after/history-nitro-layout.png) | ![](after/history-nitro-original-positions.png) | ![](after/history-nitro-pointed.png) |

### 3. Clean up / redrawn

| Before (`main`) | After |
|---|---|
| ![before](before/history-redrawn.png) | ![after](after/history-redrawn-everything.png) |

After: **Chemically identical**; **MOVED · Molecule redrawn** (ethanol's shape changed) and **STYLE · Arrow style changed**. [Chemistry](after/history-redrawn-chemistry.png) · [Layout](after/history-redrawn-layout.png) · [changed-on-GitHub, after](after/conflict-redrawn-everything.png) · [before](before/conflict-redrawn.png)

### Which side is current

The owner's pick (variant A): the version compared is on the **left** in a dashed grey frame with a **COMPARED** pill; the drawing now is on the **right** in a solid green frame with a **CURRENT** pill. Headers name the version (**Version · saved 14:02 · …**, **On GitHub · @alice · 14:05 · …**, **Your drawing · open now** / **not sent**); screen readers hear "Current: …" and "Compared: …"; the footer says **Changes read from … (left) to … (right)**. Green and grey are used only for this, so they never meet the change colours. The sides were already compared-left / current-right in both dialogs; only the frames, headers and footer are new.

| Before (panes unmarked) | After, light | After, dark |
|---|---|---|
| ![](after/history-nitro-everything.png) | ![](after/identity/history-nitro-identity.png) | ![](after/identity/history-nitro-identity-dark.png) |
| ![](after/conflict-nitro-everything.png) | ![](after/identity/conflict-nitro-identity.png) | ![](after/identity/conflict-nitro-identity-dark.png) |

### Dark interface

| History, moved + NO₂ | Changed on GitHub, redrawn |
|---|---|
| ![](after/history-nitro-everything-dark.png) | ![](after/conflict-redrawn-everything-dark.png) |

Also: [moved](after/history-moved-everything-dark.png) · [moved, Chemistry](after/history-moved-chemistry-dark.png) · [NO₂, Chemistry](after/history-nitro-chemistry-dark.png) · [redrawn](after/history-redrawn-everything-dark.png) · [conflict moved](after/conflict-moved-everything-dark.png) · [conflict NO₂](after/conflict-nitro-everything-dark.png). Light contact sheet: [contact-sheet-light.png](contact-sheet-light.png).

The scenario captures are of the build at `5d57161`; later commits change only marks for stereo, hydrogen bonds and arrow anchors, none of which these drawings have, and the pane frames, captured at `fd2c815` (History) and `d9a2980` (changed on GitHub), show the same rows.

## Verification

VERIFICATION_TABLE

## Review

Three adversarial passes (gpt-6.1-sol, read-only) on the model and the dialog, focused on false "equal" verdicts, stereo/aromaticity, matching and stale results. Fixed, each with a test:

- Unresolved labels (`*` with a free label) and axial stereo are **Couldn't verify**; unpaired electrons and singlet spin are compared; AND/OR groups compare by membership, not number; a stereo group shared by two molecules is **Couldn't verify** per molecule.
- Unknown stereo is keyed to its stereocentre or double bond, not the bond drawn wavy.
- A molecule is fitted on its own atoms only; symmetric atoms pair as drawn (no false 180° turn), and only when every bond is kept.
- An arrow given a bend is **redrawn**; a hydrogen bond added or removed between molecules is a chemical line.
- A changed atom or bond hidden in a collapsed label is marked on the label; a comparison that stops says **Couldn't compare**.

Greptile, three rounds (5/5 at the final head, no open threads), each finding fixed with a failing-first test: a changed stereocentre or E/Z double bond is marked beside other edits; a restyled hydrogen bond between molecules is a style line (once, not twice inside one molecule); an arrow that lets go of an atom is listed, compared by anchor target so turning the scheme does not count.

No stale-result race was found: each comparison has its own generation, and a result for another one is dropped (tested).

## Risk

Known limits, all reported as a change or as unverified rather than hidden:

- A molecule whose ids changed **and** whose chemistry changed shows as removed and added (C2 matches by substructure). A re-created molecule's style is not compared, and a hydrogen bond between molecules with new ids is listed again.
- Mirror and scale show as redrawn (C2 gives them kinds). Lone-pair and label offsets are not turned back when lined up, so a turned molecule with those may also list a style line.
- Over-reporting in rare cases: inverting a whole AND group, a drawn H next to a radical, moving the wave on an unknown allene, or a control point added on a straight arrow.
- The conflict dialog compares a snapshot of yours taken when it opens, as before.

## What C2 will add

- Re-import matching by substructure when ids changed.
- Mirror and scale as their own kinds.
- Atom-number wording ("OH added at C4").

## Changelog

`docs/changes/unreleased/feat-compare-chemistry-layout.md`

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

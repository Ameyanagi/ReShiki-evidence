## Why

Compare C2a, after C1 (#1222) and the polish PR (#1235). C1 left three gaps the owner wanted closed before matching by structure (C2b):

- A molecule flipped with the Flip tool, or drawn larger, was a **redraw**, and the Flip tool's wedge swap was listed as a **Style** change.
- A mirror image of a chiral molecule had no words for what it is.
- A chemical line said **O added**, not **OH added at C4**.

## Approach

Plan sections 1–2 with the critic's corrections and decisions 1, 4, 5, 6 and 9.

- **Fit** (`compare/fit.rs`) gains `scale` and `mirror`; `Fit::similar(pairs, mirror, scale)` fits a reflection, a scale or both, and `axis_degrees()` gives the mirror line. Each molecule or graphic is fitted rigidly first, then mirrored, then scaled (by ≥ 1%), then both, at C1's tolerances (0.01 / 0.03 bond lengths). Only objects with three points off one line get mirror or scale, so an arrow drawn longer stays **redrawn**.
- **Whole scheme** refits with the winning model. An object the scheme fit carries within the tolerances has no line of its own, so a scaled scheme's straight arrow is not redrawn; it lines up by the scheme fit. The displayed scale is the reciprocal of the alignment scale.
- **New kinds** `Mirrored` and `Scaled`, tags **MIRRORED** and **SCALED** in the MOVED blue, legend **Moved, mirrored, scaled**. Rows read **Molecule flipped left–right / top–bottom / mirrored** and **Molecule scaled to 120%**.
- **One reflection function**, `editing::transform_display`: everything but positions that a planar transform carries (fixed hydrogens, number, stereo and map offsets, marks, bond indicators) and, for a reflection, wedges ↔ hashes and double-bond sides. The Flip tool, rotate/scale and Compare's lined-up view all use it; the lined-up view therefore undoes a mirror with the full Flip display transform, and Style is compared on the lined-up values (rounded to 0.01), so the Flip tool's swap is not a style change.
- **Mirror vs stereo:** chemistry is still decided by the signature. Flip tool → same chemistry + **MIRRORED**, detail **Wedges swapped; same configuration**. Positions mirrored without the swap → **Mirror image: every stereocentre inverted**, only when every centre has the same mapped neighbours and opposite parity and double-bond stereo and stereo groups are unchanged.
- **Wording:** `chemistry::edit_mapped(left, right, map)` replaces `edit` (identity maps for id matches; C1's stereo marks unchanged) and carries centres, double bonds and groups through the map, ready for C2b. `chemistry::parts` splits an edit into added/removed/replaced groups (formulas `OH`, `NH₂`, `NO₂`, `CO₂H`, `OCH₃`, `CN`), atoms changed in place (charge, isotope, H, radicals), bond orders, and inverted centres. Wording is not paint: the attachment carbon that only lost an H is painted but not worded. Positions use the drawing's own atom numbers (`4` → **C4**, `N1′` as written), qualified when one side lacks the number (**C4 (current)**) or the sides differ (**C5 → C4**); hidden atoms of collapsed labels are not used; no number, no position.

## Evidence

_Pending._

## Verification

VERIFICATION_TABLE

## Risk

- Lined-up view and Style now go through `transform_display`; offsets of rotated molecules are compared rounded to 0.01 drawing units.
- Most drawings carry no atom numbers, so most rows name no position.
- `map_positions` no longer moves offsets itself; every caller (rotate, flip, scale about a pivot, stretch) calls `transform_display` first.

## Changelog

`docs/changes/unreleased/feat-compare-c2a.md`

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

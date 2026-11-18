## Why

Follow-up to #1235. Clicking a change in **What changed** zoomed both panes to the changed atoms alone, so the zoom went as far as the preview allows: labels beside the change were cut at the pane edge ("H2SO4, heat" read "I2SO4, heat"), the compared pane cut off an O, and the painted NO₂ filled the pane.

## Approach

- The zoom box is the change's objects (for a chemical change, its whole molecule) together with its painted atoms; the selection outline still marks just the changed atoms and bonds.
- Both panes keep one size, so one scale, each centred on the change on its side.
- The box is at least half the whole drawing in each direction, so a selected change is shown at most about twice as large as the full view.
- Each spot now carries both boxes (`Spot { outline, context }`).

## Evidence

_Pending._

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | pending |
| PR CI | pending |

## Risk

- A very large changed molecule now zooms little or not at all, since its whole molecule is the context.

## Changelog

`docs/changes/unreleased/fix-compare-zoom.md`

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

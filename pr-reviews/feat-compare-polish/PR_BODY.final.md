## Why

Follow-ups to Compare C1 (#1222), from its review and from the evidence:

- A reaction scheme is much wider than it is tall, so in the side-by-side panes it is drawn small with most of each pane empty.
- A long SMILES wrapped glyph by glyph, breaking inside `[N+]` or between `C` and `l`, with before and after run together.
- In History, the verdict badge sat at the far right edge; in the changed-on-GitHub dialog it sat beside the title.
- Clicking a change outlined it, but a small edit in a big drawing stayed small.

## Approach

UI only; `reshiki::compare` is unchanged.

- **Stack wide schemes.** The panes are laid out in `responsive`. Using the panes' own zoom formula (`compare_zoom`, now shared with the preview), the panes stack, the compared one on top, when that draws the drawing at least 10% larger. The footer then reads **Changes read from … (top) to … (bottom)**. The dialogs pass their footer as a closure so it can follow.
- **SMILES on two lines.** Before, then **→ after** under it, with word wrapping. A zero-width space goes only between tokens: never inside a bracket atom, inside `Cl`/`Br`, or before a ring bond (`1`, `%12`). The row's accessible name carries the raw SMILES.
- **Badge beside the title** in both dialogs, through one shared title row.
- **Zoom to the selected row.** Both panes zoom to the change at one scale, each centred where the change is on its side. A chemical change is bounded by its painted atoms and bond endpoints, not its whole molecule; anything else by its objects.

## Evidence

_Pending: before (`main`) and after captures of History › Compare and the conflict dialog, light and dark._

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | pending |
| PR CI | pending |

## Risk

- Stacking depends on the dialog's size; a window resize can switch between the two layouts, which is intended.
- The pane zoom estimate uses fixed header and footer heights; an error of a few pixels only shifts the 10% threshold slightly.

## Changelog

`docs/changes/unreleased/feat-compare-polish.md`

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

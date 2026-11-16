## Why it matters

Rings and Clean up behaved unlike ChemDraw, and Clean up shrank drawings:

- **Ring tool:** every free ring was drawn at 14.4 pt with a vertex pointing right, so hexagons were flat, and in a Nature-style document (10.8 pt) rings came out a third larger than the bonds next to them.
- **Clean up size:** it redrew every molecule at the style's bond length. A drawing made at 1.5x shrank to about 0.66x. Ring templates ignore the requested length, so norbornane and cyclododecane shrank even at the default size. On the 62-input ChemDraw corpus, main kept the size in 29 of 62 cases (down to 0.63x); ChemDraw kept it in 62.
- **Clean up orientation:** six-membered rings stayed flat or tilted.
- **Clean up flow:** it refused to run without a selection, and every run went through a preview with Show original, Apply and Cancel, which took two steps for one edit.

The owner approved every behaviour below ("ring-cleanup-picks").

## Approach

| # | Approved item | What changed |
|---|---|---|
| 1 | Ring tool keeps one vertical side | Free rings use the phase π/n for even sizes: square, hexagon and octagon stand upright (hexagon vertex at top). Odd rings still point right, as in ChemDraw. |
| 2 | Ring tool size | Free rings and the aromatic ring use the document's bond length. |
| 3 | New depictions upright | SMILES and name import straighten, then turn each component's six-membered rings upright. |
| 4 | Templates upright | `scripts/regenerate_templates.py` gains the same upright step for entries without an explicit orientation; `assets/templates.json` is regenerated, and a rerun is byte-identical. 25 of the 108 templates turned upright (benzene, pyridine, Ph3P, tryptophan, ...). Cages and entries with an explicit IUPAC orientation are unchanged. |
| 5 | Clean up keeps the size | Each molecule keeps its median drawn bond length. |
| 6 | Keep turns rings upright | Turn of at most 30°; a flat ring's tie goes to the turn leaving more fusion bonds vertical. Each component turns on its own, so salts and multi-component drawings work too. Cages, and components whose six-membered rings disagree (fluorene), keep their orientation. |
| 7 | Free orientation | Rings upright, then the existing conventional reflections. |
| 8 | No selection | Cleans the whole drawing (`Scope::Drawing`). |
| 9 | Apply at once | One Undo step. The preview state, its bar, Show original, Apply/Cancel and the modal gate are removed. Undo/Redo is the comparison. |
| 10 | Split button | The toolbar button runs Clean up. The ▾ opens **Orientation** (Keep, Free, IUPAC fused rings) and **With a selection** (Selected atoms, Whole molecules). These options exist only in that menu. |

**Shrink fix.** The root cause is the RDKit ring templates. They place their atoms at RDKit's 1.5 bond length and ignore the requested length. A layout with at most one fixed atom is now drawn at 1.5, then scaled to the kept median (about the fixed atom when there is one). Mixed template-and-chain layouts stay consistent this way. The upright turn runs before straightening, and straightening is skipped once the rings set the orientation, so a side chain cannot tilt the rings afterwards.

**Kept as before.** RDKit-parity mode (`refine() == false`) keeps the style length and the old orientation bit for bit. IUPAC orientation is unchanged.

## Evidence

The GUI captures are ReShiki window captures made through Codex computer use, each run with a fresh data directory. Before is `origin/main` 8a2e018. After is this branch at an earlier commit with the same UI. Later commits changed only cleanup geometry details: median of even counts, cages per component, the one-fixed-atom rescale, and the straightening order. The headless renders and the corpus come from the final commit.

### 1–2. Ring tool in a Nature-style document (10.8 pt), one ring click and one single bond

<img src="compare/ring-tool-compare.png" width="900">

On main the hexagon is flat and its sides are longer than the bond. With this PR the hexagon stands upright, as ChemDraw draws it, and its sides match the bond.

| Before (main) | After (this PR) |
|---|---|
| <img src="before/ring-tool-nature.png" width="420"> | <img src="after/ring-tool-nature.png" width="420"> |

### 9–10. Toolbar: "Clean up…" with a preview → split button with options

| Before: tooltip "Clean up…" | After: ▾ menu |
|---|---|
| <img src="before/cleanup-button-crop.png" width="420"> | <img src="after/cleanup-menu-crop.png" width="420"> |

### 5–6, 9. Messy benzene (1.5x size, turned 20°): Clean up and the Undo comparison

On main, nothing selected gives "Select a molecule or atoms to clean up". After Cmd+A, Clean up opens the preview bar, and **Show original** shows the input under it. Apply then gives a ring shrunk to about two thirds.

| main: nothing selected | main: preview | main: Show original | main: applied (shrunk) |
|---|---|---|---|
| <img src="before/benzene-nothing-selected.png" width="220"> | <img src="before/benzene-preview.png" width="220"> | <img src="before/benzene-show-original.png" width="220"> | <img src="before/benzene-cleaned.png" width="220"> |

With this PR, Shift+Cmd+K with nothing selected applies at once: the ring stands upright at the drawn size, and the status reads "Cleaned up · ⌘Z undoes". Undo and Redo compare the two.

| this PR: input | Clean up | Undo | Redo |
|---|---|---|---|
| <img src="after/benzene-messy.png" width="220"> | <img src="after/benzene-cleaned.png" width="220"> | <img src="after/benzene-undo.png" width="220"> | <img src="after/benzene-redo.png" width="220"> |

### 8. Nothing selected cleans the whole drawing (messy benzene, naphthalene and cyclohexane)

| main: input | main: nothing selected | main: Cmd+A, Clean up, Apply | this PR: nothing selected, Clean up |
|---|---|---|---|
| <img src="before/whole-open.png" width="220"> | <img src="before/whole-nothing-selected.png" width="220"> | <img src="before/whole-cleaned.png" width="220"> | <img src="after/whole-cleaned.png" width="220"> |

### Fused systems and a salt

| | Input | main | this PR |
|---|---|---|---|
| Naphthalene drawn flat | <img src="before/naphthalene-open.png" width="220"> | <img src="before/naphthalene-cleaned.png" width="220"> | <img src="after/naphthalene-cleaned.png" width="220"> |
| Estradiol, messy | <img src="after/estradiol-open.png" width="220"> | <img src="before/estradiol-cleaned.png" width="220"> | <img src="after/estradiol-cleaned.png" width="220"> |
| Sodium benzoate, messy | <img src="before/salt-open.png" width="220"> | <img src="before/salt-cleaned.png" width="220"> | <img src="after/salt-cleaned.png" width="220"> |

The flat naphthalene turns 30° the way that stands its fusion bond vertical. Window zoom differs between the estradiol captures (each fits its own result); the rows below compare sizes at one scale.

### Same inputs, one scale: main, this PR and ChemDraw 26.1

These are corpus inputs rendered by ReShiki's renderer at 1200 dpi and drawn at one scale, so sizes compare directly. ChemDraw's output is its own Clean Up Structure on the same file.

<img src="compare/corpus-rings.png" width="900">

<img src="compare/corpus-fused.png" width="900">

Cages (norbornane, adamantane) keep their drawn orientation, as in ChemDraw. Cyclododecane uses RDKit's macrocycle template; it now keeps its size. Its shape differs from ChemDraw's round 12-gon, as it did on main.

### 3–4. New depictions and templates

| SMILES import (main vs this PR) | Bundled templates (main vs this PR) |
|---|---|
| <img src="compare/depictions.png" width="440"> | <img src="compare/templates.png" width="440"> |

## Corpus summary

This run uses the 62 ChemDraw-reference inputs: 31 molecules, each clean and messy (1.5x, turned 20°, jittered). The throwaway harness wrote `*-pr-cleanup.cdxml` beside the ChemDraw and main results, and was not committed. The full table is [compare/corpus-metrics.md](compare/corpus-metrics.md).

| | ChemDraw 26.1 | main | this PR (Keep) |
|---|---|---|---|
| Size kept (mean bond within 5% of input) | 62/62 (0.98–1.03x) | 29/62 (0.63–1.00x) | **62/62 (0.98–1.02x)**; Free and IUPAC also 62/62 |
| Six-ring cases upright | 26/46 | 22/46 | **43/46** (the 3 others are cages, kept as drawn; ChemDraw also leaves them tilted) |
| Clean, flat six-ring inputs turned upright | 11/15 | 0/15 | **15/15** |
| Ring orientation same as ChemDraw | — | 22/46 | 29/46 (ChemDraw leaves 14 messy inputs tilted) |
| Largest turn of a six-ring input | — | — | 30° |

norbornane-messy now keeps 1.005x (main 0.65x), cyclododecane 1.00x (0.95x), and cyclododecane-messy 0.998x (0.63x).

## Verification

VERIFICATION_TABLE

Tests updated for the new behaviour, with no coverage dropped: the eraser stroke across an upright hexagon; the colliding-vertex ring rejection; Keep cleanup turning a substituted or tilted ring upright by ≤30°; template-retry and import expectations; scaled-cleanup bond length; the hidden 3D molecule test input; and the app tests for apply, stale results, background tabs, gates, results, focus and the palette.

Tests added:

- the ring tool follows the style length and keeps a vertical side, for sizes 3–8 and the aromatic ring;
- Clean up keeps the size for benzene, cyclododecane, norbornane and adamantane at 0.7/1/1.5x in Keep, Free and IUPAC, and with one fixed atom;
- the median of an even count;
- Keep turns a flat or tilted ring upright within 30°, and a flat naphthalene's tie goes to the vertical fusion bond;
- a side chain never tilts upright rings;
- no selection cleans each component on its own (a two-component, salt-like drawing at two sizes);
- new depictions stand each component's rings upright beside a chain and beside a cage;
- one Undo step for an applied cleanup, cancel and stale results change nothing, and no selection cleans every structure with the menu options;
- the split button fits and clicks;
- focus returns to the drawing from the toolbar and its menu.

## Risk

- **Visible defaults change.** Ring-tool rings, imported structures, templates and cleaned drawings now stand six-membered rings upright. Users who liked flat hexagons can still draw or rotate them. Keep turns rings by up to 30°.
- **1,10-Phenanthroline's template** loses its mirror-symmetric flat pose, as ChemDraw's cleanup does to phenanthrene.
- **Known limit, also on main:** a template ring system with two or more fixed atoms outside it (Selected atoms with a partial selection) is still drawn at template scale. Fixing that needs scaling inside RDKit's fragment assembly.
- **Rejected review finding:** a drawing whose substituent bonds are 7–13 times the ring bond can make Keep's existing least-squares fit turn the whole molecule. The ring outline still changes by at most 30° modulo its symmetry.
- **No more preview.** Clean up no longer has a preview step; Undo is the way back.
- **Windows.** Windows x64 runs in PR CI.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

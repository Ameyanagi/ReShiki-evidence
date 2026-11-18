Fixes #1203 (PR 2 of 2: labels; #1231 added the prediction).

## Why it matters

#1231 made NMR prediction scriptable, but the last step of @ssiddhantsharma's design in #1203 still needed the app: putting the shifts on the atoms. Open structure-elucidation tools return SMILES, and a journal-styled structure with the assigned shifts was a manual step. This PR lets Python, `reshiki --cli` and `reshiki --mcp` write the labels, in the formats of **Show labels**, into files that keep them, laid out for a journal figure. It follows the design and the owner's decisions of 2026-11-18. Thanks to @ssiddhantsharma for the design.

## Approach

One core function, three thin surfaces, a shared layout, and the canvas sharing the label text:

- **Core** (`crates/io/src/nmr/labels.rs`):
  - `LabelFormat { Numbers, Ppm, Both }` and `label_text(format, atom, ppm, decimals)`: `#3`, `1.28 ppm`, `#3 · 1.28 ppm`.
  - `default_decimals(nucleus)`: 2 for ¹H (`7.26 ppm`), 1 for ¹³C (`128.4 ppm`), 2 when the rows do not name a nucleus; 0 to 4 on request.
  - `write_labels(doc, rows, format, decimals)` writes each row's label into the atom's number (`AtomDisplay.number`). Every row is checked before anything changes: an ID that is not an atom, a ppm that is not finite, a label over 32 characters or decimals over 4 is an error, and nothing is written. Rows with no ppm are skipped. Listed atoms keep their number style and lose their offset; an atom without a number gets the shift-label style (below). Other atoms are untouched.
- **Layout** (`crates/model/src/atom_labels/long_numbers.rs`), shared by canvas, SVG, PNG and PDF:
  - **Switch:** atom numbers ending in ` ppm`, which every `ppm` and `both` label does. Every other number (`3`, `12a`, `#3`, free text) keeps today's layout; no golden changed.
  - Candidates around the atom, outward first (away from the drawing around it) and nearest first, in 7.5° steps and half-text-height distance steps. The first box that touches no bond (with room for double and triple bond rails), atom label, other label or leader, and stays outside its molecule's convex hull, wins. Text uses its real advance width and height.
  - Labels that fit beside their atom go first, those with the least room first; the rest are placed after them.
  - A **leader** (a thin line, half the bond width) joins a label to its atom when the label sits more than 1.5 bond lengths away or another atom is as near to it. A spot whose leader would cross text or another leader is not used; a leader may cross a bond when there is no other way.
  - Deterministic: the order and candidates depend only on the drawing.
  - **Size:** labels written without a style are 65% of the drawing's atom-label size (6.5 pt with 10 pt atom labels), and never below 4 pt. At the previous 7.5 pt (75%) a row of shift labels read as full-size text next to the atoms.
- **Canvas** (`src/canvas/nmr.rs`): the **Show labels** overlay builds its text with `label_text` (3 decimals, as before). A test checks the overlay text equals the atom numbers scripts write. The overlay stays on screen only.
- **Python**: `Drawing.with_labels(rows, *, format="both", decimals=None) -> Self`. `rows` is an `NmrPrediction`, or `NmrShift` rows, `{"atom", "ppm"}` mappings or `(atom, ppm)` tuples; the nucleus default applies when every row names the same nucleus. A changed drawing is reconciled as the app reconciles an atom-number edit. Errors are `ReShikiError` with code `invalid_arguments`.
  - **RDKit `atomNote`** (as the reply on #1203 promised): `to_rdkit()` sets `atomNote` on each numbered atom, by position in the MOL block ReShiki writes (`doc.atoms` order). `from_rdkit()` puts each note on the atom imported from that RDKit atom (MOL atom ID = atom-block position) and skips, with one `StructureWarning` saying how many, notes whose atom was dropped on import (a folded explicit H) or whose text is not 1 to 32 printable characters.
- **MCP** (`crates/agent/src/ops/label_atoms.rs`): `label_atoms {document, rows: [{atom, ppm|null}], format, decimals, base_revision, idempotency_key}`. Mutating, destructive (it replaces numbers), idempotent, closed-world, one undo step.
  - `base_revision` is required and is the `revision` `predict_nmr` returned, so rows never land on atoms that an edit since then removed or renumbered (`stale`).
  - It reuses `apply`'s receipt replay and atomic commit (`apply`'s `prepare`, `replace` and `commit` are shared; `apply` behaves the same and its tests are unchanged). A call that writes nothing commits the snapshot unchanged (`recorded: false`), which binds its key without normalizing the drawing.
  - `decimals` is 0 to 4, or `null` for 2 (MCP rows do not carry a nucleus). An atom not in the drawing is `unknown_object`; another bad row or decimals out of range is `invalid_arguments`; both change nothing.
- **CLI**: `reshiki --cli convert … --nucleus 1H|13C --labels numbers|ppm|both [--decimals N]` runs `import`, `predict_nmr`, `label_atoms` (bound to the predicted revision, decimals from the nucleus unless given) and `export`.
  - Only for outputs that keep atom numbers: svg, png, pdf, cdxml, cdx (`convert` cannot write `.rsk`; use Python's `rsk()` or MCP `file_save`).
  - Another output, `--labels` without `--nucleus`, `--nucleus` without `--labels`, `--decimals` without `--labels` or outside 0 to 4 is a usage error (exit 2).
- **CDXML/CDX** keep writing plain atom numbers; ChemDraw places them itself, without leaders.

## Label formats and storage trade-offs

| `format` | ¹H | ¹³C |
| -------- | -- | --- |
| `numbers` | `#3` | `#3` |
| `ppm` | `1.28 ppm` | `128.4 ppm` |
| `both` | `#3 · 1.28 ppm` | `#3 · 128.4 ppm` |

Labels are stored as atom numbers (static text), as the owner decided:

- No `.rsk` format change. The test keeps the input's version floor (30 for a plain drawing, 35 for one that already needs it), and reopening keeps the numbers.
- They render in SVG, PNG and PDF and go to ChemDraw as `AtomNumber`/`ShowAtomNumber`.
- They do not update after later edits: the user owns them, as with any atom number. Predict and label again to refresh.
- Labelling ¹H after ¹³C replaces only the atoms the ¹H rows list.
- If **Show labels** is on while a labelled drawing is open, both show.
- Data credit: documented (cite the prediction's `credit` with a published figure). No caption is added.

## Evidence

EVIDENCE_PLACEHOLDER

## Verification

VERIFICATION_TABLE

VERIFICATION_DETAILS

## Risk

- Overwrites the numbers of the listed atoms, including numbers a user typed. Only listed atoms change, and it is one undo step in MCP.
- Labels go stale after a chemistry edit (documented).
- Crowded molecules: a label that cannot sit beside its atom gets a leader, which may cross a bond when there is no clear path (morphine ¹H #18 below). Labels never overlap text, bonds or other labels in the two test molecules, and leaders never cross text; the search is capped at 8 bond lengths, after which the least-bad spot is used.
- Hit testing, Print Selection and molecules shown only in 3D use the same placement as before for picking; a long label's leader is drawn but not itself pickable, and a 3D-only neighbour can shift where a picking pass expects a label. Both are edge cases of the existing indicator code.
- Numbers inside a collapsed abbreviation make CDXML/CDX export ask for the abbreviation to be expanded, as for any atom number there (documented).
- MCP catalog: CATALOG_SIZE characters, under the 21,500 cap that #1231 set; not raised. `agent-api.txt`: LLMS_SIZE bytes, under the 220 KiB cap; not raised.

## Review

REVIEW_SECTION

## Changelog

`docs/changes/unreleased/feat-nmr-labels-scripting.md` (Changes, `issues: [1203]`, `credit: [@ssiddhantsharma]`). Every commit carries `Co-authored-by: Siddhant Sharma`.

## Docs updated

`docs/python.md` (Label the atoms, decimals, RDKit `atomNote`), `docs/agent-cli.md` (NMR labels, `--decimals`), `docs/agent-api.md` (18 tools, `label_atoms`, `decimals`), `docs/nmr-prediction.md` (Labels from scripts, layout), the website NMR guide, `docs/atom-labels.md`, `docs/architecture.md`, `crates/python/README.md`, the Agent Skill (a labelled-convert recipe), the generated agent reference and module index.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none new. The evidence images and test values show shifts predicted from the bundled nmrshiftdb2-derived index (`licenses/nmrshiftdb2/DATABASE-LICENSE.txt`). Contains information from nmrshiftdb2 (https://nmrshiftdb.nmr.uni-koeln.de), available under the nmrshiftdb2 Database License.

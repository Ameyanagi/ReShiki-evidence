Fixes #1203 (PR 2 of 2: labels; #1231 added the prediction).

## Why it matters

#1231 made NMR prediction scriptable, but the last step of @ssiddhantsharma's design in #1203 still needed the app: putting the shifts on the atoms. Open structure-elucidation tools return SMILES, and a journal-styled structure with the assigned shifts was a manual step. This PR lets Python, `reshiki --cli` and `reshiki --mcp` write the labels, in the formats of **Show labels**, into files that keep them. It follows the design and the decisions the owner approved on 2026-11-18. Thanks to @ssiddhantsharma for the design.

## Approach

One core function, three thin surfaces, and the canvas sharing the label text:

- **Core** (`crates/io/src/nmr/labels.rs`):
  - `LabelFormat { Numbers, Ppm, Both }` and `label_text(format, atom, ppm)`: `#3`, `1.280 ppm`, `#3 · 1.280 ppm`.
  - `write_labels(doc, rows, format)` writes each row's label into the atom's number (`AtomDisplay.number`).
  - Every row is checked before anything changes. An ID that is not an atom (in any row), a ppm that is not finite, or a label over 32 characters is an error, and nothing is written.
  - Rows with no ppm are skipped. Listed atoms keep their number style (`number_style()` if they had none) and lose their offset. Other atoms are untouched.
- **Canvas** (`src/canvas/nmr.rs`): the **Show labels** overlay now builds its text with `label_text`. A test checks that the overlay text equals the atom numbers scripts write, for all three formats. The overlay is otherwise unchanged: on screen only, never exported.
- **Python**: `Drawing.with_labels(rows, *, format="numbers" | "ppm" | "both" = "both") -> Self`. `rows` is an `NmrPrediction`, or an iterable of `NmrShift`, `{"atom", "ppm"}` mappings or `(atom, ppm)` tuples. Errors are `ReShikiError` with code `invalid_arguments`.
- **MCP** (`crates/agent/src/ops/label_atoms.rs`): `label_atoms {document, rows: [{atom, ppm|null}], format, base_revision, idempotency_key}`. It is mutating, destructive (it replaces numbers), idempotent, closed-world, and one undo step.
  - `base_revision` is required and is the `revision` `predict_nmr` returned, so rows never land on atoms that an edit since then removed or renumbered (`stale`).
  - It reuses `apply`'s receipt replay and atomic commit. `apply`'s `prepare`, the reconcile-and-commit tail (`replace`) and the effect (`commit`) are now shared functions; `apply` behaves the same (its tests are unchanged).
  - An atom not in the drawing is `unknown_object`; another bad row is `invalid_arguments`; both change nothing.
  - Value: `{effect, document, revision, recorded, labeled}`.
- **CLI**: `reshiki --cli convert … --nucleus 1H|13C --labels numbers|ppm|both` runs `import`, `predict_nmr`, `label_atoms` (bound to the predicted revision) and `export`.
  - Only for outputs that keep atom numbers: svg, png, pdf, cdxml, cdx. `convert` cannot write `.rsk`; the SVG, PNG and PDF it writes carry the editable drawing with the labels.
  - Another output, `--labels` without `--nucleus`, `--nucleus` without `--labels`, or a bad value is a usage error (exit 2). `render` does not take them.

## Label formats and storage trade-offs

| `format` | Label on atom 3 |
| -------- | --------------- |
| `numbers` | `#3` |
| `ppm` | `1.280 ppm` |
| `both` | `#3 · 1.280 ppm` |

Labels are stored as atom numbers (static text), as the owner decided:

- No `.rsk` format change. The test keeps the input's version floor (30 for a plain drawing, 35 for one that already needs it), and reopening keeps the numbers.
- They render in SVG, PNG and PDF with the existing collision-aware placement, and go to ChemDraw as `AtomNumber`/`ShowAtomNumber`.
- They use the drawing's atom-number style, not the teal overlay, and have no leader lines. An atom inside a collapsed abbreviation shows its label only when expanded.
- They do not update after later edits: the user owns them, as with any atom number. Predict and label again to refresh.
- Labelling ¹H after ¹³C replaces only the atoms the ¹H rows list.
- If **Show labels** is on while a labelled drawing is open, both show.
- Data credit: documented (cite the prediction's `credit` with a published figure). No caption is added.

## Evidence

Being gathered; it is added inline before this PR leaves draft.

## Verification

VERIFICATION_TABLE

## Risk

- Overwrites the numbers of the listed atoms, including numbers a user typed. Only listed atoms change, and it is one undo step in MCP.
- Labels go stale after a chemistry edit (documented).
- `apply.rs` was restructured to share its prepare, replace and commit steps; its behaviour and tests are unchanged.
- MCP catalog: 21,382 (was 20,250) characters, under the 21,500 cap that #1231 set; not raised. `agent-api.txt`: LLMS_SIZE bytes, under the 220 KiB cap; not raised.

## Changelog

`docs/changes/unreleased/feat-nmr-labels-scripting.md` (Changes, `issues: [1203]`, `credit: [@ssiddhantsharma]`). Every commit carries `Co-authored-by: Siddhant Sharma`.

## Docs updated

`docs/python.md` (Label the atoms), `docs/agent-cli.md` (NMR labels), `docs/agent-api.md` (18 tools, `label_atoms`), `docs/nmr-prediction.md` (Labels from scripts), the website NMR guide, `docs/atom-labels.md`, `docs/architecture.md`, `crates/python/README.md`, the Agent Skill (a labelled-convert recipe), the generated agent reference and module index.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none new. The evidence images and test values show shifts predicted from the bundled nmrshiftdb2-derived index (`licenses/nmrshiftdb2/DATABASE-LICENSE.txt`). Contains information from nmrshiftdb2 (https://nmrshiftdb.nmr.uni-koeln.de), available under the nmrshiftdb2 Database License.

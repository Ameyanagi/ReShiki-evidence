Refs #1203 (PR 1 of 2: prediction; PR 2 adds the labels).

## Why it matters

NMR prediction was only in the desktop app (**Properties → Predict NMR…**). The Python package, `reshiki --cli` and `reshiki --mcp` could draw a structure but not predict its shifts, so scripted NMR work stopped at the GUI. @ssiddhantsharma designed this in #1203: the same rows as the palette, the metadata **Export…** writes, and one contract across the three scriptable surfaces. This PR builds the prediction half of that design, as the owner approved on 2026-11-18.

## Approach

One core function, three thin surfaces:

- **Core** (`crates/io/src/nmr.rs`, `crates/io/src/nmr/shifts.rs`): `predict_drawing(doc, ids, nucleus) -> Result<Shifts, String>`.
  - `None` predicts the whole drawing, which must be exactly one molecule; otherwise it fails with `NMR prediction needs exactly one molecule; this drawing has N`.
  - IDs predict the molecule they belong to (`...; the given IDs cover N` when they span several).
  - It then runs the existing `prepare` and `predict` unchanged, so a molecule without sites for the nucleus is still an error, as in the app. `SELECT_ONE_MOLECULE`, which the GUI compares, is untouched.
  - The broad match is now data: `broad: bool` on the core `Prediction` and on `Row`. The limitation text the GUI prints is unchanged.
  - `Row::note(nucleus)` is the Limitations column; `to_tsv` now calls it. The TSV **Export…** writes is byte-identical, pinned by goldens written by `to_tsv` on `main` before the change (ethyl acetate ¹H/¹³C, paracetamol ¹H/¹³C; the ¹³C ethyl acetate golden is the existing desktop acceptance export).
- **MCP** (`crates/agent/src/ops/predict_nmr.rs`): read-only, idempotent, closed-world tool after `analyze`. Schema `{document, nucleus: enum["1H","13C"], ids: null | [1..5000 IDs]}`, all required.
  - `ids: []` is `invalid_arguments`; unknown IDs are `unknown_object` (`ids::resolve`); other failures are `failed`.
  - The value is the prediction plus `revision`, the document revision it was predicted from. PR 2 will require it as `base_revision` when writing labels.
- **CLI** (`src/cli/predict_nmr.rs`): `reshiki --cli predict-nmr (INPUT | - | --smiles TEXT) [--from FORMAT] --nucleus NUCLEUS` imports, then calls the same tool, and prints one labelled JSON line. `--nucleus` is required and parsed explicitly (`1H`/`13C`); `render --nucleus` and `analyze --nucleus` are rejected by name.
- **Python**: `Drawing.predict_nmr("1H" | "13C") -> NmrPrediction` (frozen dataclasses; iterating yields `NmrShift` rows; `atom` and `hydrogens` are `int`). Errors are `ReShikiError` with `code` `invalid_arguments` or `failed`.
- The nucleus is required on every surface and parsed explicitly: Rust's derived names `H1`/`C13` are rejected everywhere.
- **Catalog cap**: the serialized catalog is 20,250 characters (was 19,418, cap 19,500). The cap is now 21,500, leaving about 1,250 for PR 2's `label_atoms`; the reason is commented at the assertion.

## Result schema

The MCP `value` and the CLI `value` (Python has the same fields without `revision`):

```json
{"revision": "0", "nucleus": "13C", "solvent": "CDCl3",
 "rows": [{"atom": "1", "nucleus": "13C", "ppm": 14.2, "shell": 3, "references": 58,
           "sd": 0.504020137, "min": 12.4, "max": 16.927, "broad": false,
           "hydrogen_count": null, "hydrogens": [], "note": null}],
 "method": "…", "data_version": "…", "conditions": "…", "limitations": "…",
 "credit": "Contains information from nmrshiftdb2 …", "data_access": "…"}
```

- One row per site in drawing order. `ppm`, `shell`, `references`, `sd`, `min` and `max` are `null` for a site without data, and `note` says why (for example the exchangeable OH of ethanol).
- `hydrogen_count` is set for ¹H only; `hydrogens` lists H drawn as atoms.
- Floats are rounded to 9 decimal places, as `analyze` does. IDs are decimal strings on the wire.
- `credit` is in every prediction and documented as the attribution to cite with published values. No caption is added anywhere.

## Atom numbering

- `atom` is the drawing atom ID: the GUI's `#N`, and the ID `inspect` and `analyze` report. A ¹H row names the heavy atom carrying the H.
- SMILES: atom `N` is the `N`th SMILES atom after default H removal, which is RDKit `Chem.MolFromSmiles` index `N − 1`.
- MOL: the atom's number in the file.
- `.rsk`: the stored IDs, which can have gaps. `clean()` keeps them.
- `crates/python/tests/test_nmr.py` pins the SMILES and MOL mappings against RDKit (H counts per ¹H row, carbons per ¹³C row), including a `[H]`-containing SMILES.

## Evidence

Before, on `main` at 0d97885cb ([cli-before.txt](cli-before.txt)):

```text
$ reshiki --cli predict-nmr --smiles CCOC(C)=O --nucleus 1H
reshiki: unknown command `predict-nmr`; run `reshiki --cli help`
[exit 2]
```

After ([cli-after.txt](cli-after.txt), full JSON lines), ethyl acetate:

| Nucleus | atom | H | ppm | shell | refs | SD | min–max |
| ------- | ---- | - | --- | ----- | ---- | -- | ------- |
| ¹H | 1 | 3 | 1.28 | 4 | 17 | 0.064 | 1.17–1.40 |
| ¹H | 2 | 2 | 4.16 | 3 | 17 | 0.375 | 2.735–4.45 |
| ¹H | 5 | 3 | 2.095 | 4 | 4 | 0.024 | 2.05–2.10 |
| ¹³C | 1 | | 14.2 | 3 | 58 | 0.504 | 12.4–16.927 |
| ¹³C | 2 | | 61.05 | 2 | 58 | 1.444 | 57.1–65.9 |
| ¹³C | 4 | | 170.7 | 2 | 28 | 1.254 | 167.07–175.1 |
| ¹³C | 5 | | 20.9 | 3 | 28 | 1.005 | 19.55–25.8 |

- Python session for ethyl acetate ¹H and ¹³C, with the RDKit index check: [python-session.txt](python-session.txt).
- MCP: the `tools/list` entry, both call results, an `ids` selection and the error cases: [mcp.txt](mcp.txt).
- CLI usage and operation errors: [cli-errors.txt](cli-errors.txt).

Errors, the same on every surface:

| Case | MCP / CLI | Python |
| ---- | --------- | ------ |
| nucleus `H1` | `invalid_arguments` (CLI: usage, exit 2) | `ReShikiError`, `code == "invalid_arguments"` |
| `ids: []` | `invalid_arguments` | n/a |
| unknown ID | `unknown_object` | n/a |
| two molecules | `failed`: needs exactly one molecule; this drawing has 2 | `failed`, same message |
| water, ¹³C | `failed`: This molecule has no supported ¹³C sites | `failed`, same message |
| Fe, ²H, charged | `failed` | `failed` |

## Verification

VERIFICATION_TABLE

Run on macOS arm64 (Apple M4):

- `cargo fmt --all --check`; workspace `cargo clippy --all-targets --all-features -D warnings`; wasm32 clippy as in checks.yml.
- `cargo test -p reshiki-io`, `-p reshiki-agent` (unit, contract, headless), `-p reshiki-model`; `cargo test --no-default-features -p reshiki --lib --bins`; the `it` modules `cli::`, `mcp_stdio::`, `mcp_tools::`, `mcp_shutdown::`, `headless_parity::`.
- The Python wheel built as CI builds it (`maturin build --locked`), then `pytest crates/python/tests` with rdkit, ruff and ty.
- `uv run --locked python -m unittest discover -s tests`, ruff and ty for scripts.
- Goldens regenerated and verified: CLI help (`predict-nmr.txt`, `help.txt`), `ops-catalog.json`, `cli-tools.json`, `cli-help.json`, the Agent Skill folder, `docs/agent-reference.md`, `parity.json`, and the four MCP transcripts (tool lists; modern and legacy `tools-*` add a `predict_nmr` success and an invalid nucleus).
- `module_index.py --check`, `copy_lint.py`, `assemble_changelog.py --check`, `check_docs_tree.mjs`, `bun run docs:check`, and `check_runtime_dependencies.verify_agent_api` on the built binary (the packaged client's ordered tool list).

## Risk

- Nothing in the GUI changes visibly. `Row` gains `broad`; the palette still prints the limitation text, and the TSV is byte-identical (goldens).
- The MCP catalog grows by 832 characters; the cap rises to 21,500.
- The Python wheel now uses the bundled NMR index (about 0.4 MB); its licence was already in the wheel.
- The core's other error messages are written for the GUI (for example "Select a molecular structure…"); only the one-molecule case is reworded for scripts.
- The 3-second engine deadline applies on slow machines, as in the app.
- No `operation_api` bump: adding a tool is additive.

## What PR 2 adds

`with_labels(rows, format="numbers" | "ppm" | "both")` in Python, a `label_atoms` MCP tool that requires this PR's `revision` as `base_revision`, and `--nucleus/--labels` for `convert`. Labels are stored as native atom numbers in `.rsk` and drawn in SVG, PNG and PDF.

## Changelog

`docs/changes/unreleased/feat-nmr-predict-scripting.md` (Changes, `issues: [1203]`, `credit: [@ssiddhantsharma]`). Every commit carries `Co-authored-by: Siddhant Sharma`.

## Docs updated

`docs/python.md` (Predict NMR), `docs/agent-cli.md` (command, options, example), `docs/agent-api.md` (17 tools, `predict_nmr`), `docs/nmr-prediction.md` (From scripts), `docs/architecture.md`, `crates/python/README.md`, the Agent Skill template, the generated agent reference and module index.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none new. The TSV goldens and parity rows hold values predicted from the bundled nmrshiftdb2-derived index (`licenses/nmrshiftdb2/DATABASE-LICENSE.txt`) and carry its attribution.

## Summary

Wave 2 of the agent API audit: the MCP server, the command line, Python and JavaScript now answer the same way. This is operation API 2, a breaking change that was approved.

- Every MCP tool returns one envelope, `{value, warnings, validation, versions}` (A6).
- Errors carry `code`, `retryable`, and `reason`, `param` or `current_revision` where they apply. The CLI prints `reshiki: error[code]:`. Python and JavaScript errors have `.code` (A5).
- `import` reads chemical names, and a new `name` tool returns a drawing's systematic name (A1).
- A new `convert` tool turns structure text into a file or a PNG preview in one call (A4).
- The same format names work everywhere: `rsk`, `cdx`, `rxn`, `rsmi`, `svg_text` (A7).
- The PNG preview and property rounding are shared in `reshiki-io`, and one parity fixture is checked by the CLI, Python and JavaScript tests (A10).
- `compose` no longer carries the sketch schema. A new `schema` tool returns it on demand. The tool list drops from 24,409 to 19,418 characters while it gains three tools.

No issue is filed for these items, so this PR closes none.

## Why it matters

The audit found these by calling the tools. The numbers below come from the base and branch binaries in Evidence.

- **A6: five tools had a different shape.** `info`, `document_new`, `document_list`, `document_close` and `inspect` put their fields next to `versions`. The other 8 tools wrapped them in `value`. A client had to know which tool used which shape. The handle of a new document sat at `document` after `document_new` but at `value.document` after `import`.
- **A5: errors had only `code` and `message`.** To learn which argument was wrong, whether a file already existed, or what the current revision was, an agent had to parse the message text. The CLI printed `reshiki: error:` for every failure, so a script could not tell a bad argument from a bad structure.
- **A1: names did not work over MCP.** `import` with `format: "name"` failed with ``unknown variant `name` ``. The server instructions told agents to "Provide SMILES". An agent then wrote SMILES from memory, which is where structure mistakes come from. The CLI had `name`, but MCP did not.
- **A4: one picture took three calls.** A preview of a SMILES needed `import`, `render` and `document_close`, and held a document slot in between.
- **A7: format names differed by surface.** MCP `export` could not write `cdx`, `rxn` or `rsmi`, which JavaScript could. `import` refused `rsk`, the file extension of a ReShiki drawing. JavaScript drew SVG text live by default, while the other surfaces outlined it.
- **A10: the same answer was computed in several places.** The PNG preview code was copied into the browser crate. Python `properties()` did not round values the way the CLI and MCP did. Nothing checked that the surfaces agree.
- **Tool list size.** Every MCP client loads the whole tool list into the model's context at the start of each session. `compose` alone was 12,128 of 24,409 characters, mostly the sketch schema, which only a sketch call needs.

## Approach

- **A6.** All 16 tools return the envelope. `compose` reports `bounds` as `{min, max}`, like `inspect`. `OPERATION_API_VERSION` is 2. `reshiki --cli info` prints the same envelope with `cli` beside `value`. The contract test checks the envelope keys and the `value` keys of every tool against the catalog. Migration steps are in `docs/agent-api.md#changes-in-operation-api-2` and the changelog. Rejected: keeping the flat shapes and adding wrapped copies. That leaves two shapes to document and test for good.
- **A5.** `OpError` gains `retryable` (true only for `busy` and `timeout`), `reason` (for file errors), `param` and `current_revision`. Messages are unchanged, so a client that reads only `code` and `message` keeps working. Python raises `reshiki.ReShikiError`, a subclass of `ValueError`, so existing `except ValueError` still catches it. Rejected: new error codes per case. `reason` refines the code without breaking clients that switch on `code`.
- **A1.** The agent crate defines a `Naming` hook. The app supplies it for both `reshiki --mcp` and `reshiki --cli`. A host without the hook answers `unsupported`. The hook returns the prepared graph, the parser warnings and an identity check, as the GUI uses. So `(1M)-` and `(1P)-BINOL` keep their axis, and warnings such as `Rotation sign (+) ignored` reach `warnings`. `reshiki --cli name --json` builds its value with the same function as the MCP tool. Rejected: resolving names to SMILES only. The review showed that this drops axial configuration (see Risk).
- **A4.** `convert` takes `{input: {format, text}, to, pages, svg_text, max_width, max_height}`. `to` is an export format, or `preview` for the PNG that `render` draws. It keeps no document. It reuses the `import` decoder and the `export` and `render` code, so the bytes match. Not built: applying a list of edits inside `convert`.
- **A7.** `rsk` is accepted wherever `reshiki` is. `cdx`, `rxn` and `rsmi` are written by MCP `export`, `file_save` and `convert`, by the CLI (never `cdx` to a terminal) and by Python (`cdx()`, `rxn()`, `rsmi()`). The SVG text option is `svg_text` everywhere (`svgText` in JavaScript), and text is outlined by default on every surface. Python gains `export()` (the new name of `render()`, which stays), `svg_text=` (`text=` stays) and `save(overwrite=)`.
- **A10.** `reshiki-io` holds `preview::png` and `Analysis::rounded`. MCP, the canvas tools, the browser crate and Python use them. `tests/fixtures/agent-api/parity.json` is written from the CLI by `scripts/agent_parity_fixture.py`. `tests/cli.rs`, `crates/python/tests/test_parity.py` and `packages/editor/test/parity.test.ts` all check it. It holds only values expected to be the same on every platform (SMILES, InChI, InChIKey, formula, rounded properties, reaction SMILES), not MOL coordinates.
- **On-demand schema.** `compose` lists `sketch` as a plain object with a short description. `schema` with `{name: "sketch"}` returns the sketch schema as the assistant's pinned Proposal schema states it. The `compose` decoder is unchanged, so any valid sketch is still valid. The in-app assistant's pinned schemas are byte-identical. The contract test caps the catalog at 19,500 characters (it was 25,000). It still runs the whole sketch case corpus against `compose`. Rejected: shrinking the pinned schema. The in-app assistant depends on it.

## Evidence

All captures: macOS arm64 debug builds of base `1d94f392` and branch `35ca456d`. Each was built fresh in a new target folder, because another lane once wrote into this lane's old target folder. SHA-256: base `d851719f…667695b`, branch `f677a916…6dd6ed978` (full values in [verify-macos-arm64.txt](verify-macos-arm64.txt)). Every server and CLI run had a fresh `RESHIKI_DATA_DIR` from `mktemp -d`, and `RESHIKI_INCHI_HELPER` and `RESHIKI_NAMING_HELPER` pointed at the same binary. A small Python JSON-RPC driver ran `reshiki --mcp` over stdio with protocol `2025-11-25`: `initialize`, `notifications/initialized`, then the calls shown. No app window is involved. Transcripts are text, rendered from a monospaced page 1000 px wide at 2× (2000 px wide). Highlighted lines are the ones that change. Document handles show as `<doc#n>` and the temporary folder as `<dir>`. The full text is in the linked `.txt` files.

### A6: one result envelope

`info`, `document_new`, `document_list`, `inspect` and `document_close`, the same calls in both builds.

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392: info, document_new, document_list, inspect and document_close return their fields at the top level next to versions; the new document's handle is at document](a6-envelope-base.png) | ![Branch 35ca456d: all five return validation, value, versions and warnings, with the fields under value; the handle is at value.document](a6-envelope-branch.png) |

Transcripts: [a6-envelope-base.txt](a6-envelope-base.txt), [a6-envelope-branch.txt](a6-envelope-branch.txt).

### A5: structured errors

Four failures: `render` with `max_width: 0`, a second `apply` at an old `base_revision`, and `file_save` outside the granted folder and onto an existing file (`--allow-write out`, `overwrite: false`).

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392: each error has only code and message; the argument, the file reason and the current revision are only in the message text](a5-errors-base.png) | ![Branch 35ca456d: the same errors add param max_width, current_revision 1 and param base_revision, reason path_not_granted and reason file_exists with param path, and retryable false](a5-errors-branch.png) |

Transcripts: [a5-errors-base.txt](a5-errors-base.txt), [a5-errors-branch.txt](a5-errors-branch.txt).

On the command line, an operation error now names its code. The same image shows names and `cdx` on the CLI (A1, A7).

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392: reshiki: error: for an invalid SMILES and for a width of 9000; --from name and --to cdx are refused as unknown formats; info has its fields at the top level](a5-a7-cli-base.png) | ![Branch 35ca456d: reshiki: error[failed] and error[invalid_arguments]; caffeine converts to Cn1c(=O)c2c(ncn2C)n(C)c1=O; ethanol.cdx is written with the VjCD0100 header; info prints the envelope with cli](a5-a7-cli-branch.png) |

Transcripts: [a5-a7-cli-base.txt](a5-a7-cli-base.txt), [a5-a7-cli-branch.txt](a5-a7-cli-branch.txt).

### A1: chemical names over MCP

`import` with `format: "name"` for caffeine, then `name` on that document. Then `convert` from name to MOL for both BINOL atropisomers, re-importing each MOL and naming it. Then `(R)-(+)-lactic acid` to SMILES.

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392: import fails with unknown variant name; name and convert are unknown tools](a1-names-base.png) | ![Branch 35ca456d: caffeine imports as Cn1c(=O)c2c(ncn2C)n(C)c1=O and is named 1,3,7-trimethyl-3,7-dihydro-1H-purine-2,6-dione; the (1M) and (1P) BINOL MOL files name back to (1M) and (1P); lactic acid carries the warning Rotation sign (+) ignored](a1-names-branch.png) |

Transcripts: [a1-names-base.txt](a1-names-base.txt), [a1-names-branch.txt](a1-names-branch.txt).

The server instructions changed to match: 899 → 1,320 characters. "Provide SMILES; chemical names are not resolved." is replaced by a sentence on names. The instructions also state the envelope, point to `convert`, and say to inspect again after `stale` before retrying.

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392 server instructions, 899 characters, ending with Provide SMILES; chemical names are not resolved](instructions-base.png) | ![Branch 35ca456d server instructions, 1,320 characters, describing the envelope, convert, the stale rule and chemical names](instructions-branch.png) |

### A4: a preview in one call

Aspirin, `CC(=O)Oc1ccccc1C(=O)O`. Each build ran `import`, `render` and `document_close`, then `convert` with `to: "preview"` on a fresh server.

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392: import, render and document_close take 3 calls for a 22,040-byte PNG; convert is an unknown tool](a4-convert-base.png) | ![Branch 35ca456d: convert returns the same 22,040-byte PNG, the same SHA-256 as render, in 1 call, and leaves 0 documents open](a4-convert-branch.png) |

The PNG from base `render` and the PNG from branch `convert` have the same SHA-256 (`453a37b9…`), so moving the preview code into `reshiki-io` (A10) did not change a byte. Images: [a4-render-preview-base.png](a4-render-preview-base.png), [a4-convert-preview-branch.png](a4-convert-preview-branch.png). Transcripts: [a4-convert-base.txt](a4-convert-base.txt), [a4-convert-branch.txt](a4-convert-branch.txt).

### A7: one vocabulary

The `format` enums from `tools/list`, then `export` of the reaction `CCO>>CC=O` as `cdx`, `rxn` and `rsmi`, then `import` of a saved `.rsk` file with `format: "rsk"`.

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392: export lacks cdx, rxn and rsmi and refuses each; import refuses rsk](a7-formats-base.png) | ![Branch 35ca456d: export writes cdx starting VjCD0100, rxn starting $RXN V3000 and rsmi CCO>>CC=O; import accepts rsk](a7-formats-branch.png) |

Transcripts: [a7-formats-base.txt](a7-formats-base.txt), [a7-formats-branch.txt](a7-formats-branch.txt).

### On-demand schema: tool list size

`tools/list`. Size is the number of characters in the result's `tools` array as compact JSON.

| Base `1d94f392` | Branch `35ca456d` |
| --- | --- |
| ![Base 1d94f392: 13 tools, 24,409 characters; compose 12,128; schema is an unknown tool](q-a2-tools-list-base.png) | ![Branch 35ca456d: 16 tools, 19,418 characters; compose 3,684; convert 2,012, name 633, schema 506; schema sketch returns 10,125 characters](q-a2-tools-list-branch.png) |

| | Base `1d94f392` | Branch `35ca456d` | Change |
| --- | ---: | ---: | ---: |
| Whole tool list | 24,409 (13 tools) | 19,418 (16 tools) | −4,991 (−20.4%) |
| The 13 tools of base | 24,409 | 16,264 | −8,145 |
| `compose` | 12,128 | 3,684 | −8,444 |
| New: `convert`, `name`, `schema` | – | 2,012 + 633 + 506 | +3,151 |

The sketch schema now comes from one `schema` call only when an agent draws a sketch (10,125 characters). Tables: [q-a2-tools-list-base.txt](q-a2-tools-list-base.txt), [q-a2-tools-list-branch.txt](q-a2-tools-list-branch.txt). Full arrays: [q-a2-tools-list-base.json](q-a2-tools-list-base.json), [q-a2-tools-list-branch.json](q-a2-tools-list-branch.json).

A10 and the Python and JavaScript sides have no transcript here. They are covered by the parity fixture tests listed under Verification.

## Verification

macOS arm64, branch `35ca456d`, each run with its own `CARGO_TARGET_DIR`. `RESHIKI_INCHI_HELPER` and `RESHIKI_NAMING_HELPER` were set to the built binary, and `RESHIKI_DATA_DIR` to a fresh folder.

| Command | Result |
| --- | --- |
| `cargo fmt --all --check` | pass |
| `cargo clippy --workspace --lib --bins --all-features --locked -- -D warnings` | pass |
| `cargo clippy -p reshiki -p reshiki-agent -p reshiki-mcp -p reshiki-python --all-targets --all-features --locked -- -D warnings` | pass |
| `cargo clippy -p reshiki-web -p reshiki-web-worker --lib --target wasm32-unknown-unknown --locked -- -D warnings` | pass (before the review fixes, which did not touch these crates) |
| `cargo test --locked -p reshiki-agent -p reshiki-mcp` | agent 310 + 34 + 4 passed (2 ignored); mcp 57 + 2 + 18 passed |
| `cargo test --locked -p reshiki-io` | 643 passed (5 ignored), plus 10 + 3 + 1 (before the review fixes) |
| `cargo test --locked -p reshiki --test cli --test agent_api_runtime --test agent_api_cli_files --test agent_api_labels --test agent_api_malformed --test agent_api_grants` | 19, 6, 5, 5, 5, 10 passed |
| `cargo test --locked -p reshiki --test mcp_tools --test mcp_stdio --test mcp_shutdown --test headless_parity --test headless_launch --test assistant_contract` | all passed (before the review fixes) |
| `cargo test --locked -p reshiki --lib naming::` | 130 passed, 2 ignored (see Risk) |
| `cargo test --locked --bin reshiki` | 1580 passed, 182 ignored |
| maturin debug wheel, `pytest crates/python/tests` with RDKit | 153 passed, 3 skipped |
| `ruff check`, `ruff format --check`, `ty check` (`crates/python`, `reference`, `scripts`, `tests`) | pass |
| `bun fmt --check .`, `bun run lint:js`, `bun run docs:check` | pass |
| `uv run python scripts/assemble_changelog.py --check` | pass |
| `bun test` in `packages/editor` | not run: no wasm-bindgen CLI on this Mac |
| Base and branch binaries over `reshiki --mcp` and `reshiki --cli` | as shown in Evidence |

Summary: [verify-macos-arm64.txt](verify-macos-arm64.txt).

VERIFICATION_TABLE

## Risk

- **Breaking for clients (approved).** MCP clients must read the five changed tools under `value`, and `compose` bounds as `{min, max}`. Scripts that match `reshiki: error: ` for operation failures must match `reshiki: error[`. File and input errors still print `reshiki: error: `. JavaScript `convert(…, "svg")` and `renderSvg` now outline text. Pass `{ svgText: "live" }` for the old output. The migration steps are in the docs and the changelog.
- **JavaScript is not tested yet.** `packages/editor/test/parity.test.ts` and `editor.test.ts` did not run locally. The browser crate only passed clippy for wasm32. CI must show that outlined SVG works in wasm with the bundled font and that rejected `Error`s carry `.code`. `editor.test.ts` "SVG preview matches the desktop CLI" now compares live text on both sides, and it only runs when `RESHIKI_CLI` is set.
- **Other platforms.** Everything ran on macOS arm64 only. Arch Linux x64, Ubuntu arm64 and Windows x64 still need `tests/cli.rs`, `tests/mcp_tools.rs`, `tests/mcp_stdio.rs` and the real-hook naming tests in `src/naming/agent.rs`. Those tests start the naming worker from the server process. `parity.json` was generated on macOS. It holds only values expected to be the same on every platform. The Python wheel was tested as a macOS arm64 debug build only.
- **Partial or left as is.**
  - Python `save()` still overwrites by default so that existing scripts keep working. `file_save` and the CLI refuse by default, so the defaults still differ. This is a decision for the owner.
  - The review's nit is not fixed. In `crates/agent/src/ops/headless/tests.rs`, the catalog test zips 16 tools with 13 expected hint entries. So it never checks hints, names or schema shape for `convert`, `name` and `schema`.
  - `convert`, `name` and `schema` have no schema/decoder cases file. Their own rules are unit-tested. The `cite` line numbers in `tests/fixtures/agent-contract/*-cases.json` were not updated. The gate only checks that the lines exist, and they had already drifted on main.
  - Not built: a `--name TEXT` CLI flag (a name goes in on stdin or a file with `--from name`), and applying `edits[]` inside `convert`.
  - Salt names imported through the agent API get the engine's default layout, not the GUI's side-by-side arrangement.
  - `reshiki --cli name --json` reports only the import's warnings, not the `name` tool's.
  - The offline name parser does not know some trade names. `aspirin` fails, while `caffeine`, `paracetamol` and `acetylsalicylic acid` work. The docs say so and use `caffeine` in their examples.
- **Hand-edited goldens.** The MCP transcripts in `crates/mcp/tests/transcripts` and `tests/fixtures/mcp` have no generator. They were migrated by script and by hand, and the replay tests pass against the real binary. `docs/development.md` now says this.
- **One flaky naming test.** `naming::reverse::tests::native_worker_then_local_opsin_verifies_supported_names` failed once when two copies of the suite ran at once. It passed when run alone. It does not call the changed code.
- **Instructions text changed.** A client that snapshots the server instructions outside this repo will see new text.

## Changelog

`docs/changes/unreleased/wave2-api-consistency.md`:

```markdown
---
section: Changes
issues: []
---

- **Agent tools: one result shape (breaking).** Every MCP tool now returns
  `{value, warnings, validation, versions}`. `info`, `document_new`,
  `document_list`, `document_close` and `inspect` used to return their fields
  next to `versions`; read them under `value` now, so a new document's handle
  is `value.document` after `document_new` as it is after `import`.
  `compose` reports `bounds` as `{min, max}`, as `inspect` does, instead of
  `[min, max]`. `operation_api` is 2.
  [Changes in operation API 2](agent-api.md#changes-in-operation-api-2) lists
  what a client has to change.
- **Agent tools: errors you can act on.** A tool error is
  `{code, message, retryable}`, with `reason` for file errors (such as
  `path_not_granted`), `param` for the argument at fault and
  `current_revision` after `stale`, so a client no longer reads them out of
  the message. After `stale`, inspect the document again before you retry:
  `current_revision` only says which revision the document has now. On the command line an operation error is
  `reshiki: error[code]: message`; it was `reshiki: error: message`. In Python,
  errors are `reshiki.ReShikiError` (a `ValueError`) with `.code`, and in
  JavaScript every rejected `Error` has `.code`. In Python an unknown input
  format and a constructor given another kind of content, such as a reaction
  for `Molecule.from_smiles`, are `invalid_arguments`.
- **Agent tools: chemical names.** `import` reads a chemical name with
  `format: "name"`, and the new `name` tool returns a drawing's systematic
  name with its status, reason, aliases and alternatives. Both work offline.
  A name's axial configuration is kept, so `(1M)-` and
  `(1P)-[1,1'-binaphthalene]-2,2'-diol` import as two structures, and the
  name parser's warnings and those about the named drawing are in `warnings`.
  On the command line: `echo caffeine | reshiki --cli convert - --from name --to smiles`.
  The server's instructions used to tell agents to write SMILES themselves.
- **Agent tools: `convert`.** One call reads structure text and returns a file
  or a PNG preview, and keeps no document. A picture of a SMILES took
  `import`, `render` and `document_close`.
- **Agent tools: a smaller tool list.** The tool list every MCP client loads
  is 19,418 characters for 16 tools; it was 24,409 for 13. `compose` no
  longer lists the fields of a sketch diagram: the new `schema` tool returns
  them when an agent draws one. A sketch that was valid is still valid.
- **The same names everywhere.** `rsk` and `reshiki` both name a ReShiki
  drawing in MCP, the command line, Python and JavaScript. `cdx`, `rxn` and
  `rsmi` (reaction SMILES) can be written by `export`, `file_save`,
  `reshiki --cli convert` and Python (`cdx()`, `rxn()`, `rsmi()`), as
  JavaScript already could. The option for SVG text is `svg_text`
  (`svgText` in JavaScript) on every surface, and text is outlined unless it
  is `live`.
- **JavaScript package (breaking).** `convert(…, "svg")` and `renderSvg`
  now outline text by default, as the other surfaces do; they kept live text.
  Pass `{ svgText: "live" }` for the earlier output.
- **Python package.** `export()` is the new name of `render()`, which stays.
  `save(path, overwrite=False)` raises `FileExistsError` instead of replacing
  a file; the default still replaces. `svg_text=` is the option's name and
  `text=` still works. `properties()` rounds mass, exact mass, logP and TPSA
  to 9 decimal places, as the command line and MCP do. `export`, `render` and
  `convert` have typed overloads: text formats return `str`, binary ones
  `bytes`.
- **Developer.** The PNG preview and the rounding of properties are in
  `reshiki-io` (`preview::png`, `Analysis::rounded`), shared by the
  assistant, MCP, the command line, the browser library and Python.
  `tests/fixtures/agent-api/parity.json` holds one molecule and one reaction
  with the answers the command line, Python and JavaScript must all give;
  each test suite checks it.
```

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

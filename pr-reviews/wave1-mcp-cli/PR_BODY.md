## Summary

Four fixes to the agent tools and the command line from the wave 1 audit. A tool call may now leave out an argument that can be `null`. The MCP server's instructions name the granted folders. `reshiki --cli name --json` has `warnings` and `versions` like the other commands, and a test keeps the CLI guide in step with the command table. The tool list that every MCP client loads shrinks from 27,316 to 24,409 characters.

No issue is filed for these items, so this PR closes none.

## Why it matters

The wave 1 audit found all four items by reading the code and the published tool list. The numbers below come from the base and branch binaries in the Evidence section.

- **A3: an omitted nullable argument fails the call.** 16 top-level arguments in 7 tools can be `null`: `analyze`, `apply`, `compose`, `export`, `file_save`, `inspect` and `render`. On main, leaving one out fails the whole call with `invalid_arguments`. For example, `render` with only `document` and `format` fails with ``missing field `max_width` ``. An agent that leaves out an argument it does not use has to read the error, add `null` for each such argument and call again.
- **A9: the agent does not know which folders it may use.** `file_open` and `file_save` work only in folders granted with `--allow-read` and `--allow-write`. On main, the server instructions only say "Call info first". An agent that skips `info` can try `file_save` without a grant and get an error. The instructions are the one text every client reads when it connects.
- **A8: `name --json` is wrapped differently, and the CLI guide is out of date.** `reshiki --cli name --json` printed only `api`, `experimental` and `value`. The other commands also print `warnings` and `versions`. A script that reads `versions` from every command got nothing from `name`. `docs/agent-cli.md` lacked `--isotope-style`, showed the `schema` usage with a fixed name, and said salts are errors. `name` accepts charge-balanced salts. Nothing checked the guide against the command table, so it drifted.
- **A2: the tool list is large.** Every MCP client loads the whole tool list into the model's context at the start of each session. On main it is 27,316 characters. `compose` alone is 15,155, and 14,271 of that is its input schema. That schema repeated the molecule list, point and color subschemas, and listed `explanation` and `replace_ids`, which `compose` fills in itself.

## Approach

- **A3:** Every nullable field in the argument structs is now `Option` with `#[serde(default)]`, so an omitted field reads as `null`. Before, `deserialize_with = "Option::deserialize"` made an omitted field a serde error. The published schemas are unchanged: they still list every property in `required`. Rejected alternative: removing the nullable properties from `required`. Clients that validate in strict mode need every property listed as required, so the schema stays strict and only the decoder is lenient.
- **A9:** `Identity` carries the startup `GrantSummary`, and `instructions()` adds one sentence between the workflow and the SMILES sentence: `Granted folders: file_open reads "…"; file_save writes "…".`, or `No folders are granted: use import and export.` Folder paths are Debug-formatted, so each is quoted and control characters are escaped. A folder name cannot add text to the instructions. Rejected alternative: relying on `info` alone. An agent may not call it first, and the instructions are already sent on every connection.
- **A8:** `name` now calls the `import` tool through the session, keeps the import result, and adds its `warnings` and `versions` to the JSON line next to `value`. The new test `cli::reference::tests::the_cli_guide_states_every_usage_and_option` checks that `docs/agent-cli.md` contains each command's usage (line wraps aside) and an options-table row for every option with the commands that take it. The guide is fixed to pass it.
- **A2:** `compose` publishes a Proposal schema derived from the pinned one. It leaves out `explanation` and `replace_ids`, which the decoder still reads and fills in. It states the molecule list, point and color subschemas once under `$defs`. Three sentences of the sketch description that repeat other text are removed. In every tool, the notes on one parameter move from the tool description into that property's `description`, and "Read-only" sentences that repeat `readOnlyHint` are removed. Descriptions shrink from 7,134 to 3,378 characters in all. Some input schemas grow because they now carry those notes. `reshiki --cli schema proposal` still prints the full pinned schema. The agent reference and `schema --help` say that `compose` publishes a shorter form and reads both. Rejected alternative: shrinking the pinned schema itself. ReShiki's assistant uses that schema, so changing it would change the assistant's contract as well.

## Evidence

All captures: macOS arm64 debug builds. Base `e80cbf4f` and branch `6ca4080b`, each built in its own target folder. The binaries differ (SHA-256 `a28cfd55…` and `7658ec49…`). Each run used a fresh `RESHIKI_DATA_DIR` from `mktemp -d`, and `RESHIKI_INCHI_HELPER` and `RESHIKI_NAMING_HELPER` pointed at the same binary. A small Python JSON-RPC driver ran `reshiki --mcp` over stdio with protocol `2025-11-25`: `initialize`, `notifications/initialized`, then the calls shown. No app window is involved. The transcripts are text, shown as images rendered from a monospaced page 1000 px wide at 2× (2000 px wide), at 100% zoom. The highlights mark the lines that change. The full text is in the linked `.txt` files.

### A3: render without the nullable arguments

Steps, the same in both builds: `import` `{"format": "smiles", "text": "CC(=O)Oc1ccccc1C(=O)O"}` (aspirin), then `render` with only `{"document": <handle>, "format": "png"}`. `max_width`, `max_height`, `ids` and `svg_text` are left out.

Base `e80cbf4f`: the call fails with ``missing field `max_width` ``.

![Base e80cbf4f: render without max_width, max_height, ids and svg_text returns isError true with invalid_arguments, missing field max_width](a3-render-base.png)

Branch `6ca4080b`: the call succeeds and returns a 327 × 257 px PNG with the default limits. The attached image is shown below the result.

![Branch 6ca4080b: the same render call returns isError false, a 327 by 257 PNG preview of aspirin](a3-render-branch.png)

Transcripts: [a3-render-base.txt](a3-render-base.txt), [a3-render-branch.txt](a3-render-branch.txt). The returned PNG: [a3-render-branch-output.png](a3-render-branch-output.png).

### A9: granted folders in the server instructions

Each build was started twice: `reshiki --mcp`, then `reshiki --mcp --allow-read drawings --allow-write exports` from a folder `/tmp/reshiki-evidence` that holds both subfolders. The images show `result.instructions` from `initialize`.

Base `e80cbf4f`: the text is the same with and without grants.

![Base e80cbf4f: the instructions are identical with and without granted folders and do not name any folder](a9-instructions-base.png)

Branch `6ca4080b`: without grants, the instructions say `No folders are granted: use import and export.` With grants, they name both folders, as resolved absolute paths.

![Branch 6ca4080b: without grants the instructions say No folders are granted; with grants they say file_open reads /private/tmp/reshiki-evidence/drawings and file_save writes /private/tmp/reshiki-evidence/exports](a9-instructions-branch.png)

Transcripts: [a9-instructions-base.txt](a9-instructions-base.txt), [a9-instructions-branch.txt](a9-instructions-branch.txt).

### A8: `name --json` wrapper and the CLI guide test

`reshiki --cli name --smiles CCO --json` and `--locants`. The images pretty-print each JSON line and list its top-level keys. The raw lines are in the `.txt` files.

| Base `e80cbf4f` | Branch `6ca4080b` |
| --- | --- |
| ![Base e80cbf4f: name --json and --locants print api, experimental and value only](a8-name-json-base.png) | ![Branch 6ca4080b: name --json and --locants also print versions and warnings](a8-name-json-branch.png) |

Transcripts: [a8-name-json-base.txt](a8-name-json-base.txt), [a8-name-json-branch.txt](a8-name-json-branch.txt).

The new test, run on the branch twice: once with the base `docs/agent-cli.md` copied in (`git show e80cbf4f:docs/agent-cli.md`), and once with the branch guide. The worktree was restored afterwards.

With the base guide, the test fails and names the three gaps: the `name` usage with `--isotope-style`, the `--isotope-style STYLE` option row, and the `schema NAME` usage.

![The CLI guide test fails against the base guide: docs/agent-cli.md lacks the name usage, the --isotope-style option row and the schema NAME usage](a8-docs-test-base-guide.png)

With the branch guide, it passes.

![The CLI guide test passes against the branch guide: 1 passed, 0 failed](a8-docs-test-branch-guide.png)

Logs: [a8-docs-test-base-guide.txt](a8-docs-test-base-guide.txt), [a8-docs-test-branch-guide.txt](a8-docs-test-branch-guide.txt).

### A2: tool list size

`tools/list` on each build. Size is the number of characters in the result's `tools` array as compact JSON. Whole-tool, `inputSchema` and `description` sizes are listed per tool.

| Base `e80cbf4f` | Branch `6ca4080b` |
| --- | --- |
| ![Base e80cbf4f: 13 tools, total 27,316 characters; compose 15,155, of which inputSchema 14,271](a2-tools-list-base.png) | ![Branch 6ca4080b: 13 tools, total 24,409 characters; compose 12,128, of which inputSchema 11,520](a2-tools-list-branch.png) |

| | Base `e80cbf4f` | Branch `6ca4080b` | Change |
| --- | ---: | ---: | ---: |
| Whole tool list | 27,316 | 24,409 | −2,907 (−10.6%) |
| `compose` tool | 15,155 | 12,128 | −3,027 |
| `compose` input schema | 14,271 | 11,520 | −2,751 |
| All tool descriptions | 7,134 | 3,378 | −3,756 |

Tables: [a2-tools-list-base.txt](a2-tools-list-base.txt), [a2-tools-list-branch.txt](a2-tools-list-branch.txt). The full `tools` arrays: [a2-tools-list-base.json](a2-tools-list-base.json), [a2-tools-list-branch.json](a2-tools-list-branch.json).

## Verification

macOS arm64, branch `6ca4080b`, `CARGO_TARGET_DIR` set to its own folder. `RESHIKI_INCHI_HELPER` and `RESHIKI_NAMING_HELPER` were set to `$CARGO_TARGET_DIR/debug/reshiki`, and `RESHIKI_DATA_DIR` to a fresh `mktemp -d` folder.

| Command | Result |
| --- | --- |
| `cargo fmt --all --check` | exit 0 |
| `cargo clippy --workspace --all-targets --locked --no-default-features -- -D warnings` | exit 0 |
| `cargo test --locked -p reshiki-agent -p reshiki-mcp --no-fail-fast` | 8 test binaries: 418 passed, 0 failed, 2 ignored (includes `contract` and the MCP `transcripts` goldens) |
| `cargo test --locked -p reshiki --no-fail-fast --lib --test agent_api_labels --test agent_api_grants --test cli --test mcp_stdio --test mcp_tools --test headless_parity` | 7 test binaries: 446 passed, 0 failed, 10 ignored |
| `cargo test --locked --lib -- cli::reference::tests::the_cli_guide_states_every_usage_and_option` | 1 passed; fails with the base `docs/agent-cli.md` (see A8) |
| Base and branch binaries over `reshiki --mcp` and `reshiki --cli name` | as shown in Evidence |

Summary: [verify-macos-arm64.txt](verify-macos-arm64.txt). The full workspace `cargo test` was not run on macOS arm64 for this PR.

VERIFICATION_TABLE

## Risk

- **A3** makes the decoder accept calls that the published schema does not allow. A client that leaves out a nullable argument by mistake now gets the default instead of an error. The defaults are the same values that `null` already selected.
- **A9** puts the granted folder paths into the instructions, so the model sees them. `info` already reported the same paths. The paths are quoted and escaped.
- **A8** adds two keys to the `name --json` line. A script that expects exactly `api`, `experimental` and `value` sees new keys. The existing keys are unchanged.
- **A2** changes the published `compose` schema. A client that sends `explanation` or `replace_ids` still works, because `compose` reads both forms. A client that checks its own calls against the published schema could now flag those two fields. The goldens in `crates/mcp/tests/transcripts/`, `tests/fixtures/mcp/` and `tests/fixtures/agent-contract/` are updated to the new list.

## Changelog

`docs/changes/unreleased/wave1-mcp-cli.md`:

```markdown
---
section: Changes
issues: []
---

- **Agent tools: arguments you do not use.** A tool call may leave out an
  argument that can be `null`, such as `max_width` for `render`; ReShiki reads
  it as `null`. Earlier versions failed with ``missing field `max_width` ``.
  The published schemas still list every argument as required.
- **Agent tools: granted folders in the instructions.** The MCP server's
  instructions name the folders `file_open` reads and `file_save` writes, or
  say `No folders are granted: use import and export.`
- **Agent tools: a smaller tool list.** The tool list every MCP client loads
  is 24,409 characters instead of 27,316. `compose` no longer lists
  `explanation` and `replace_ids`, which it still reads; repeated parts of the
  Proposal schema are stated once; and each parameter's notes are in its own
  description.
- **`reshiki --cli name --json`.** The JSON line also has `warnings` and
  `versions`, as the JSON of the other commands does. The
  [command-line reference](agent-cli.md#name) now covers
  `--isotope-style` and says that charge-balanced salts are named.
```

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

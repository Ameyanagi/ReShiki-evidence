## Why

The Intel macOS build is the slowest job of the nightly and has now reached its 100-minute limit. `packages / build (macos-15-intel, macos-x64, …)` in the last three nightly runs:

| Nightly run | Intel macOS build |
|---|---|
| [43772800660](https://github.com/Ameyanagi/ReShiki/actions/runs/43772800660) | 77 min |
| [43865961464](https://github.com/Ameyanagi/ReShiki/actions/runs/43865961464) | 93.5 min |
| [43935165397](https://github.com/Ameyanagi/ReShiki/actions/runs/43935165397) | over 100 min: cancelled at the limit; the rerun passed in 97 min |

A cancelled build stops the whole nightly: nothing is signed or published. The owner decided on 2026-11-17 to stop building Intel macOS for nightlies and keep it for stable releases.

## Approach

- **`release.yml`**: when `inputs.nightly` is true, the `build` and `sign` matrices leave out the `macos-x64` row. A tag push (no inputs) and a manual run without `nightly` keep all six builds and both sign jobs, with the same job names. `exclude` cannot remove an `include` row, so each list is assembled with `fromJSON(format(…))`. The timeout is unchanged.
- **`scripts/release_downloads.py`**: a nightly's package contract is eight files (five targets) instead of ten. A nightly with a missing package, or with an Intel Mac package, still fails before publishing. The download table drops the Intel row and says where Intel Mac users go: the latest stable release. `SHA256SUMS` has eight lines.
- **`nightly.yml`**: only the step name changes; its `signed-macos-*` download pattern already takes whatever was signed.
- **Updater** (`src/updates.rs`): on an Intel Mac, a check on the **Nightly** channel now answers, without a request: "Nightly builds are not made for Intel Macs. Choose Stable to get updates." Before, it would have offered the newest nightly and then failed on **Download nightly ↗** with "No matching download is available for this nightly release", or opened a missing archive when the asset lookup was offline. Stable checks and installs on Intel Macs are unchanged.
- **Docs**: `docs/releasing.md`, the install guide's nightly section, and the three "six targets" rows of `scripts/agent_api_gates.py`, which now name a non-nightly run.

## Verification

VERIFICATION_TABLE

- `uv run --locked python -m unittest discover -s tests -p 'test_*.py'`: 266 tests pass (12 skipped). New tests evaluate the two matrix expressions for a tag push, `nightly=false` and `nightly=true` (six, six and five builds; two, two and one sign jobs), and check the eight-file nightly contract.
- `cargo fmt --check`, `cargo clippy -p reshiki --all-targets --locked -- -D warnings`, `cargo test --locked -p reshiki --lib updates::` (20 pass), including the new Intel Mac test: no lookup, nothing opened, the message above.
- `ruff check` and `ruff format --check`, `scripts/module_index.py --check`, `scripts/copy_lint.py`, `scripts/assemble_changelog.py --check`, `scripts/check_docs_tree.mjs`, Prettier on the touched docs and workflow.
- actionlint on `release.yml` and `nightly.yml`: no new diagnostics against main.
- An independent review of the diff found no bug in the expressions or the updater. It asked for two wording fixes, both made: the "ten downloads" sentence in `docs/releasing.md` and the gate sources.

PR CI does not run the release workflow, and no release or nightly run was started for this PR. The next nightly after merge is the real check of the five-target matrix.

## Risk

- Intel Mac users on the **Nightly** channel get no new nightlies. The update window tells them and points to **Stable**; stable releases still ship Intel Mac DMG and ZIP.
- Intel macOS is now built only by tag pushes and manual non-nightly runs, so a break specific to it can go unseen between releases. The macOS jobs of the checks workflow still cover the Intel target. Run `gh workflow run release.yml --ref main` before tagging.
- The matrix is now an expression, which only GitHub evaluates for real. The tests evaluate the same expression text, but a mistake in it would show up in the first nightly.

## Changelog

`docs/changes/unreleased/ci-nightly-no-intel-mac.md` (Developer).

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

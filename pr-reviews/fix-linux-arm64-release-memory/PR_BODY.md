## Why

Since #1202 the nightly cannot publish: the Linux arm64 release build is killed during the final link. Nightly run [43865961464](https://github.com/Ameyanagi/ReShiki/actions/runs/43865961464) failed twice (original and rerun) in `packages / build (ubuntu-24.04-arm, linux-arm64, …)`, and every later job (sign, publish, npm, PyPI, web demo) was skipped.

The cause is memory. #1202 builds published binaries with the `dist` profile (fat LTO, one codegen unit). On Linux arm64 that link needs 18.6 GiB; the `ubuntu-24.04-arm` runner has 4 vCPU and 16 GB ([GitHub's runner table](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)).

## Approach

Two expressions in `release.yml`: Linux arm64 builds with the `release` profile's settings, `lto = false` (no LTO across crates) and 16 codegen units, which is what it built with before #1202.

```yaml
CARGO_PROFILE_DIST_LTO: ${{ startsWith(matrix.artifact, 'macos') && 'thin' || matrix.artifact == 'linux-arm64' && 'false' || 'fat' }}
CARGO_PROFILE_DIST_CODEGEN_UNITS: ${{ matrix.artifact == 'linux-arm64' && '16' || '1' }}
```

macOS stays on thin LTO; Linux x64 and both Windows builds keep fat LTO and one codegen unit, and passed in the same run. The `dist` profile in `Cargo.toml` is unchanged. The test that pins these lines, the comments and `docs/releasing.md` follow.

Thin LTO, as on macOS, also fits the runner. It was the first version of this PR and was dropped: on this platform its archive is larger than without LTO, and it builds slower (table below).

## Evidence

The failing job log: the last crate starts compiling, then nothing for 16 minutes while the fat-LTO link runs, then the runner is shut down.

```
14:05:33.0450387Z    Compiling semver v1.0.28
14:21:25.6834717Z ##[error]The runner has received a shutdown signal. This can happen when the runner service is stopped, or a manually started runner is canceled.
14:21:25.6839522Z ##[error]Process completed with exit code 143.
```

Reproduced on Ubuntu arm64 at the failing commit 5a11125a4, with the job's command and environment (`CARGO_PROFILE_DIST_STRIP=none`, `CARGO_PROFILE_DIST_SPLIT_DEBUGINFO=off`, Rust 1.99.1), pinned to 4 cores:

```sh
taskset -c 0-3 /usr/bin/time -v uv run --no-project --isolated --python 3.12.15 \
  python scripts/build_release.py --target aarch64-unknown-linux-gnu --installer
```

| `CARGO_PROFILE_DIST_LTO` | Codegen units | Memory limit | Result | Peak RSS (largest process) | Wall time | Executable (stripped) | Portable archive |
|---|---|---|---|---|---|---|---|
| `fat` (main) | 1 | none | pass | 19,505,484 KiB (18.6 GiB) | 21:11 | 79.1 MB | 35.80 MB |
| `fat` (main) | 1 | 16 GB, no swap | **killed by the OOM killer** 14.5 min into the link | – | 19:02 until killed | – | – |
| **`false` (this PR)** | **16** | none | **pass** | **2,886,420 KiB (2.8 GiB)** | **9:46** | **89.8 MB** | **36.66 MB** |
| `thin` (considered) | 1 | none | pass | 8,928,572 KiB (8.5 GiB) | 13:09 | 84.8 MB | 37.27 MB |
| `thin` (considered) | 1 | 16 GB, no swap | pass | 8,960,020 KiB (8.5 GiB) | 13:47 | 84.8 MB | 37.27 MB |

The memory limit was a cgroup (`systemd-run --user --scope -p MemoryMax=16G -p MemorySwapMax=0`). Under it the fat-LTO build stops at the same place as the runner: after `Compiling semver`, silent, then killed. The whole cgroup (compilers plus file cache) peaked at 22.9 GB for fat, 12.4 GB for thin and 8.0 GB for the chosen settings, so the chosen build was not rerun under the limit: it uses half of it.

Cargo takes both values from the environment: with `CARGO_PROFILE_DIST_LTO=false CARGO_PROFILE_DIST_CODEGEN_UNITS=16`, `cargo rustc --profile dist -v` passes `-C embed-bitcode=no -C codegen-units=16`; with `fat`/`1` and `thin`/`1` it passes `-C linker-plugin-lto -C codegen-units=1` as before. Nothing else in the repository sets a `dist` profile value.

What the chosen settings cost on Linux arm64, against a fat-LTO build that never published: the archive is 0.9 MB larger (36.66 MB instead of 35.80 MB) and the executable 10.7 MB larger. Against thin LTO the archive is 0.6 MB smaller, the build 3.5 minutes faster and the peak memory a third.

## Verification

VERIFICATION_TABLE

Run on macOS arm64 for the touched files:
- `python3 scripts/module_index.py --check`
- `uv run --locked python -m unittest discover -s tests -p 'test_*.py'`: 264 tests pass (12 skipped); `tests.test_release` pins the new workflow lines
- `uv run --locked python scripts/assemble_changelog.py --check`, `python3 scripts/copy_lint.py`, `bun scripts/check_docs_tree.mjs`
- `uv run --locked ruff check reference scripts tests` and `ruff format --check`
- actionlint on `release.yml`: no new diagnostics against main

An independent review of the diff confirmed the expressions for all six artifacts (`thin`/1 on both macOS, `fat`/1 on Linux x64 and both Windows, `false`/16 on Linux arm64; `'false'` is a non-empty string, so the expression yields it). It asked for one wording change, now made: `lto = false` drops LTO across crates and keeps it within a crate, unlike `off`.

PR CI does not run the release build. The next nightly after merge is the real check of the runner.

## Risk

- Low. Only the Linux arm64 published build changes, and it goes back to the optimization settings it shipped with until #1202. The built archive passed `build_release.py`'s own checks of the extracted application.
- Linux x64 was not measured here. It passed with fat LTO on a 16 GB runner in 16 minutes in the same nightly, but if its link needs anything near the 18.6 GiB that arm64 does, it is close to the limit. Worth measuring before the next release.
- The Linux arm64 download does not get #1202's LTO saving (0.9 MB); it keeps the rest of #1202 (the smaller TLS provider and templates).

## Changelog

`docs/changes/unreleased/fix-linux-arm64-release-memory.md` (Developer).

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

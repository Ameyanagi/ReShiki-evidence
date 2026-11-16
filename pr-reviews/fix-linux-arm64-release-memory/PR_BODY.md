## Why

Since #1202 the nightly cannot publish: the Linux arm64 release build is killed during the final link. Nightly run [43865961464](https://github.com/Ameyanagi/ReShiki/actions/runs/43865961464) failed twice (original and rerun) in `packages / build (ubuntu-24.04-arm, linux-arm64, …)`, and every later job (sign, publish, npm, PyPI, web demo) was skipped.

The cause is memory. #1202 builds published binaries with the `dist` profile (fat LTO, one codegen unit). On Linux arm64 that link needs 18.6 GiB; the `ubuntu-24.04-arm` runner has 4 vCPU and 16 GB ([GitHub's runner table](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)).

## Approach

One expression in `release.yml`: Linux arm64 builds with thin LTO, as the macOS builds already do for the same reason.

```yaml
CARGO_PROFILE_DIST_LTO: ${{ (startsWith(matrix.artifact, 'macos') || matrix.artifact == 'linux-arm64') && 'thin' || 'fat' }}
```

Linux x64 and both Windows builds keep fat LTO; they passed in the same run. The `dist` profile in `Cargo.toml` is unchanged. The test that pins this line, the comments and `docs/releasing.md` follow.

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

| `CARGO_PROFILE_DIST_LTO` | Memory limit | Result | Peak RSS (largest process) | Wall time | Executable (stripped) | Portable archive |
|---|---|---|---|---|---|---|
| `fat` (main) | none | pass | 19,505,484 KiB (18.6 GiB) | 21:11 | 79.1 MB | 35.80 MB |
| `fat` (main) | 16 GB, no swap | **killed by the OOM killer** 14.5 min into the link | – | 19:02 until killed | – | – |
| `thin` (this PR) | none | pass | 8,928,572 KiB (8.5 GiB) | 13:09 | 84.8 MB | 37.27 MB |
| `thin` (this PR) | 16 GB, no swap | **pass** | 8,960,020 KiB (8.5 GiB) | 13:47 | 84.8 MB | 37.27 MB |
| `false`, 16 codegen units (the profile before #1202, same source) | none | pass | 2,886,420 KiB (2.8 GiB) | 9:46 | 89.8 MB | 36.66 MB |

The memory limit was a cgroup (`systemd-run --user --scope -p MemoryMax=16G -p MemorySwapMax=0`). Under it the fat-LTO build stops at the same place as the runner: after `Compiling semver`, silent, then killed. The whole cgroup (compiler plus file cache) peaked at 22.9 GB for fat and 12.4 GB for thin.

What thin LTO costs on Linux arm64, against fat: the executable is 5.7 MB larger (84.8 MB instead of 79.1 MB) and the archive 1.5 MB larger. Against the profile before #1202, the executable is 5.0 MB smaller, but the compressed archive is 0.6 MB larger (37.27 MB against 36.66 MB): the thin-LTO binary compresses less well. So on this platform thin LTO keeps the installed-size win and not the download-size win. If the download size matters more, the alternative is no LTO for Linux arm64 (`'off'` for this artifact), which also builds 3.5 minutes faster.

## Verification

VERIFICATION_TABLE

Run on macOS arm64 for the touched files:
- `python3 scripts/module_index.py --check`
- `uv run --locked python -m unittest discover -s tests -p 'test_*.py'`: 264 tests pass (12 skipped); `tests.test_release` pins the new workflow line
- `uv run --locked python scripts/assemble_changelog.py --check`, `python3 scripts/copy_lint.py`, `bun scripts/check_docs_tree.mjs`
- `uv run --locked ruff check reference scripts tests` and `ruff format --check`
- actionlint on `release.yml`: no new diagnostics against main

An independent review of the diff found nothing to change: the expression gives `thin` for `macos-arm64`, `macos-x64` and `linux-arm64` and `fat` for `linux-x64`, `windows-x64` and `windows-arm64`; nothing later in the job overrides it.

PR CI does not run the release build. The next nightly after merge is the real check of the runner.

## Risk

- Low. Only the Linux arm64 published build changes, and only its LTO mode; the same setting already ships on macOS. The built archive passed `build_release.py`'s own checks of the extracted application in both thin runs.
- Linux x64 was not measured here. It passed with fat LTO on a 16 GB runner in 16 minutes in the same nightly, but if its link needs anything near the 18.6 GiB that arm64 does, it is close to the limit. Worth measuring before the next release.
- The Linux arm64 download grows by 1.5 MB against a fat-LTO build that never published.

## Changelog

`docs/changes/unreleased/fix-linux-arm64-release-memory.md` (Developer).

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

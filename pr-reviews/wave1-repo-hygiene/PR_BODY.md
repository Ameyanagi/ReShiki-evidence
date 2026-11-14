## Summary

Repository upkeep from the 0.15.0 maintenance and size audit. Release notes move to one fragment file per pull request, vendored crates get recorded patches and a check, and `AGENTS.md` lists the checks per path. macOS disk images switch to LZMA, shipped executables lose their symbols (kept as a workflow artifact), the app and `reshiki-io` move to png 0.18, and stale developer docs match the code again.

No issue is closed by this PR. The full Release builds workflow has not run on this branch.

## Why it matters

**M1 `AGENTS.md` and `CLAUDE.md`.** Contributors and coding agents had no single page that says which checks to run for a changed path, which environment variables the tests need, or what a pull request must contain. Found in the maintenance audit. `CLAUDE.md` is one line, `@AGENTS.md`, so both tools read the same file. `.claude/worktrees/` is now ignored.

**M2 Release-note fragments.** Every pull request edited `docs/changes-unreleased.md` and often `docs/contributors.md`, so parallel pull requests conflicted on the same lines. Found while merging the 0.15.0 stack. Each pull request now adds `docs/changes/unreleased/<branch>.md`; nothing shared is edited.

**M7 Vendored crates.** `vendor/` holds 8 patched crates.io crates with no record of what changed. `iced_widget` alone is 31.8k lines for a 49-line change, so a reviewer could not see the patch or check that nobody edited the copy. Found in the maintenance audit.

**D1 Documentation drift.** `docs/development.md` named Rust 1.99.0 (the pin is 1.99.1), said pull requests run macOS CI (they run Linux and Windows; macOS runs on `merge/*`, `main`, nightly and release), and did not mention cargo-nextest, which CI uses. `docs/getting-started.md` duplicated the install guide and had fallen out of date with it. The README linked 0.9.1 release highlights. `docs/architecture.md` missed `reshiki-web`, `reshiki-web-worker`, `reshiki-python` and the npm package, and gave the 3D tile cache as 128 MB (the code uses 64 MB). Found in the docs audit.

**B1 DMG compression.** The macOS disk image is the largest download. Rebuilding the released 0.15.0 app into the release layout: UDZO 42,563,362 bytes, ULMO 27,675,753 bytes (−35%). The published 0.15.0 DMG is 42,573,452 bytes.

**B2 Strip shipped executables.** 0.15.0 has no `[profile.release]`, so the shipped binary carries its full symbol table. macOS arm64: 100,855,808 → 83,492,432 bytes (−17%) with `strip -x`, which is what `strip = "symbols"` runs on Apple targets. Linux x64: 128,392,536 → 100,258,128 bytes (−22%). The Python wheel's `.so` goes from 47.2 MB to 39.2 MB. Crash reports still need line numbers, so the symbols move to a separate file instead of being dropped.

**B10 png 0.18.** The size audit found 45 duplicate crate versions; png 0.17 and 0.18 were one pair. `image` already uses 0.18. This PR moves `reshiki` and `reshiki-io` to 0.18. It does **not** remove the duplicate: `tiny-skia` 0.11.4 requires png 0.17, and `reshiki-model`, `crates/python` and `native/windows` still declare `png = "0.17"`.

## Approach

**M1.** One `AGENTS.md` at the root with a table of changed path → command, the test environment (`RESHIKI_DATA_DIR`, helper variables), code invariants, release notes and pull request rules. `CLAUDE.md` imports it instead of duplicating it. Rejected: separate files per tool, which drift.

**M2.** `scripts/assemble_changelog.py` reads `docs/changes/unreleased/*.md` (front matter `section`, `issues`, optional `credit`, then `- ` bullets).

- No option: prints `docs/changes-unreleased.md` followed by the fragments grouped into Changes, Fixes and Developer. `website/scripts/sync-docs.mjs` calls it, so the website page shows the fragments.
- `--check`: validates every fragment.
- `--release VERSION`: appends the fragments to `docs/changes-<minor>.md`, adds `credit` names to `docs/contributors.md` and deletes the fragments.

`CONTRIBUTING.md`, `docs/releasing.md` and the PR template describe the new flow. Rejected: towncrier or another tool, which adds a dependency for about 150 lines of Python, and generating the page at release time only, which would hide merged changes from the website.

**M7.** `vendor/README.md` lists each crate, its upstream version, why ReShiki changes it and its patch. `vendor/patches/<crate>.diff` is the full difference from the crates.io source in Cargo's registry. `scripts/check_vendor.py` applies each patch to the registry copy and compares every file; `--write` regenerates the patches after a deliberate change. `.ignore` hides `vendor/` from ripgrep. Rejected: git submodules or forks, which need network access and a second repository per crate.

**D1.** Fix each stale fact against the code: toolchain, uv version, CI scope and the nextest commands in `docs/development.md`; the crate list and cache size in `docs/architecture.md`; README links; `docs/roadmap.md`; the removed migration gates in `docs/structure-to-name-harness.md` (moved to `docs/changes/naming-ir-migration.md`). `docs/getting-started.md` is deleted and `/developer/getting-started` redirects to the install guide.

**B1.** `scripts/installers.py` passes `-format ULMO` to `hdiutil create`. ULMO needs macOS 10.15 or later; the app requires macOS 14.

**B2.** `[profile.release]` sets `debug = "line-tables-only"`, `split-debuginfo = "packed"`, `strip = "symbols"`. `release.yml` overrides per platform:

- macOS: Cargo strips and writes `reshiki.dSYM`.
- Windows: `strip = none`, because the MSVC linker writes no PDB for a stripped build; `reshiki.pdb` holds the symbols and the exe has none.
- Linux: `split-debuginfo = off`; `scripts/build_release.py` copies the debug info into `reshiki.debug` with `objcopy --only-keep-debug`, then strips the shipped binary and adds a debuglink.

A new step uploads these as the `symbols-<platform>` workflow artifact, before any `cargo test` step rebuilds the app and replaces the PDB. They are not release downloads. `crates/python/pyproject.toml` sets maturin `strip = true`. `panic = "abort"` stays off because the app recovers from panics with `catch_unwind`. Rejected: shipping symbols (size), and `debug = 0` (crash reports lose file and line).

**B10.** Bump the workspace and `reshiki-io` requirement; png 0.18 returns `Option` from `output_buffer_size()`, so four test call sites unwrap it.

## Evidence

All captures on macOS arm64 (macOS 27.0.1). Base: `main` e80cbf4f. Head: `wave1/repo-hygiene` e1a99203. Document renders are Markdown rendered by headless Chrome at 900 px CSS width, 2× device scale, 100% zoom. No item changes the app's UI, so there are no app screenshots.

### M1 AGENTS.md (new)

![AGENTS.md rendered](m1-agents-md.png)

### M2 Release-note fragments

| Before: `docs/changes-unreleased.md` on main | After: the page the website builds from fragments |
| --- | --- |
| ![Unreleased page before](m2-unreleased-before.png) | ![Unreleased page after](m2-unreleased-after.png) |

Fragment format: ![docs/changes/unreleased/README.md](m2-fragment-readme.png)

`--check` on the branch, then on a scratch copy with broken fragments ([m2-assemble-changelog.txt](m2-assemble-changelog.txt), [m2-assemble-changelog-broken.txt](m2-assemble-changelog-broken.txt)):

```
$ uv run --locked python scripts/assemble_changelog.py --check
1 changelog fragments are valid
exit 0

$ python3 scripts/assemble_changelog.py --check     # empty fragment body
Changelog fragment error: fix-empty.md: write the change as '- ' bullets
exit 1
$ python3 scripts/assemble_changelog.py --check     # section: Fixed
Changelog fragment error: fix-paste-bond.md: section must be one of Changes, Fixes, Developer
exit 1
$ python3 scripts/assemble_changelog.py --check     # issues: 1151
Changelog fragment error: fix-paste-bond.md: expected a [list], got '1151'
exit 1
```

### M7 Vendored crates

![vendor/README.md rendered](m7-vendor-readme.png)

Pass on the branch, then a scratch copy of `scripts/` and `vendor/` with local edits ([m7-check-vendor.txt](m7-check-vendor.txt)):

```
$ uv run --locked python scripts/check_vendor.py
8 vendored crates match their upstream source and patch
exit 0

$ echo '// local edit' >> vendor/usvg/src/lib.rs && python scripts/check_vendor.py
usvg: src/lib.rs differs from the patched upstream
exit 1
$ touch vendor/usvg/src/extra.rs && python scripts/check_vendor.py
usvg: the patched upstream has different files from vendor/usvg
exit 1
$ rm vendor/patches/svg2pdf.diff && python scripts/check_vendor.py
svg2pdf: no vendor/patches/svg2pdf.diff
usvg: the patched upstream has different files from vendor/usvg
exit 1
```

### D1 Documentation drift

| Before (main e80cbf4f) | After (e1a99203) |
| --- | --- |
| ![docs/development.md before](d1-development-before.png) | ![docs/development.md after](d1-development-after.png) |
| ![README links before](d1-readme-links-before.png) | ![README links after](d1-readme-links-after.png) |

The development excerpt shows the changed paragraphs: Build and run, Optional RDKit reference tests, CI (up to the unchanged browser-build paragraph) and Documentation.

### B1 DMG compression

Released 0.15.0 `ReShiki.app` staged the way `scripts/installers.py` stages it (app, `Applications` link, `Install ReShiki.txt`) ([b1-dmg-ulmo.txt](b1-dmg-ulmo.txt)):

```
$ hdiutil create -volname ReShiki -srcfolder staging -format UDZO -ov release-UDZO.dmg
$ hdiutil create -volname ReShiki -srcfolder staging -format ULMO -ov release-ULMO.dmg
42563362 release-UDZO.dmg
27675753 release-ULMO.dmg
$ hdiutil verify release-ULMO.dmg
hdiutil: verify: checksum of "release-ULMO.dmg" is VALID
```

An earlier run on the app alone, copied out of the published 0.15.0 DMG, measured 40,939,577 → 25,762,440 bytes (−37%).

### B2 Strip and symbols

Released 0.15.0 macOS arm64 executable ([b2-strip-size.txt](b2-strip-size.txt)):

```
$ stat -f '%z %N' reshiki-0.15.0
100855808 reshiki-0.15.0
$ nm reshiki-0.15.0 | wc -l
  160118
$ strip -x -o reshiki-0.15.0-stripped reshiki-0.15.0
83492432 reshiki-0.15.0-stripped
$ nm reshiki-0.15.0-stripped | wc -l
   14138
```

The release profile on a scratch crate keeps file and line in the dSYM ([b2-dsym-proof.txt](b2-dsym-proof.txt)):

```
$ nm target/release/symdemo | grep -c crash_here     # no function symbols
0
$ dwarfdump --uuid target/release/symdemo target/release/symdemo.dSYM
UUID: 57C995AB-3F88-35A9-BE5A-38EC38F9B7B6 (arm64) target/release/symdemo
UUID: 57C995AB-3F88-35A9-BE5A-38EC38F9B7B6 (arm64) target/release/symdemo.dSYM/Contents/Resources/DWARF/symdemo-75fd2a785a4b0eda
$ atos -o target/release/symdemo.dSYM/Contents/Resources/DWARF/symdemo-* -arch arm64 -l 0x100000000 0x$addr
_RNvCs76zrxM7ygTX_7symdemo10crash_here (in symdemo-75fd2a785a4b0eda) (main.rs:2)
```

Copied away from its dSYM, the same executable prints the panic location but no backtrace frames.

### B10 png 0.18

`cargo tree -e normal -i` for each png version ([b10-png-tree.txt](b10-png-tree.txt)):

| | png 0.17.16 used by | png 0.18.1 used by |
| --- | --- | --- |
| main e80cbf4f | reshiki, reshiki-io, reshiki-model, tiny-skia | image |
| e1a99203 | reshiki-model, tiny-skia | image, reshiki, reshiki-io |

PNG export tests on the branch ([b10-io-png-tests.txt](b10-io-png-tests.txt)): `cargo test --locked -p reshiki-io png`, 8 passed.

## Verification

macOS arm64, head e1a99203:

| Command | Result |
| --- | --- |
| `uv run --locked python scripts/assemble_changelog.py --check` | 1 fragment valid |
| `uv run --locked python scripts/check_vendor.py` | 8 vendored crates match |
| `uv run --locked python -m unittest tests.test_assemble_changelog tests.test_release tests.test_windows_signing_workflows` | 36 tests OK |
| `ruff check` / `ruff format --check` on the changed scripts and tests | passed, 5 files formatted |
| `cargo test --locked -p reshiki-io png` | 8 passed |
| ULMO image of the released 0.15.0 app in the release layout, `hdiutil verify` | VALID |

VERIFICATION_TABLE

## Risk

- **The full Release builds workflow has not run on this branch.** The per-platform strip settings, the Linux `objcopy` split and the `symbols-<platform>` upload are untested in CI. On macOS, `target/<target>/release/reshiki.dSYM` is a symlink into `deps/`; check that the uploaded artifact holds the DWARF file. Run the workflow manually before the next release.
- **ULMO can fail on some folder contents.** On macOS 27.0.1 arm64, `hdiutil create -srcfolder … -format ULMO` (default APFS) failed with "No space left on device" on every attempt for the 0.15.0 app alone (6 of 6) and for the app with only the `Applications` link (8 of 8). The exact release layout passed 8 of 8. UDZO never failed. The failure depends on contents, so the three retries in `create_disk_image` would not help. The release runner is `macos-15`, which was not tested. Adding `-fs HFS+` made the failing folder pass (26,843,777 bytes); creating UDZO and running `hdiutil convert -format ULMO` also works (25,716,676 bytes).
- **B10 is partial.** Both png versions are still compiled into the app because `tiny-skia` 0.11 needs png 0.17.
- Stripping removes symbol names from local panic backtraces in shipped builds. Crash reports need the matching symbol artifact.
- Docs and scripts only for M1, M2, M7 and D1. The website build now runs `python3` (`python` on Windows) through `sync-docs.mjs`.

## Changelog

`docs/changes/unreleased/wave1-repo-hygiene.md`:

```md
---
section: Developer
issues: []
---

- Each pull request adds its release note as one file in
  [`changes/unreleased/`](changes/unreleased/README.md) instead of editing this
  page or the contributor list. `scripts/assemble_changelog.py` checks the
  files, assembles this page and moves them into the release notes.
- macOS disk images use LZMA compression and are about a third smaller.
- Release executables and the Python package carry no symbols. The Release
  builds workflow keeps them as a separate symbol file for crash reports.
- `vendor/README.md` lists every vendored crate with its upstream version, its
  reason and its patch; `scripts/check_vendor.py` checks each one against its
  crates.io source.
- `AGENTS.md` tells coding agents and contributors which checks to run.
- The old getting-started page redirects to the
  [install guide](https://reshiki.com/guide/install/). The development,
  architecture and roadmap notes match the current toolchain, CI and crates.
```

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: `vendor/patches/*.diff` record changes to crates already vendored from crates.io under their own licenses (iced_wgpu, iced_widget, iced_winit, smithay-clipboard, svg2pdf, usvg, window_clipboard, zune-jpeg); no new third-party code is added.

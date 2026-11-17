## Summary

Two owner decisions of 2026-11-17 on the GitHub UI.

- **The GitHub button moves to the left end of the status bar.** The cloud, with its account initial and unsent dot, leaves the command bar (where it sat after Save as) and becomes the status bar's first control, before the repository chip and the status message. Its menu is the same and opens upward. Tooltip and accessible name are unchanged (**GitHub · Signed in as @login** / **GitHub · Not signed in**), and Tab reaches it, then the chip, in the order they are drawn. Signed out, it still shows. The command bar's gaps go back from 3 px to 4 px: #1199 narrowed them only to make room for the button.
- **Repository rows link to their page on GitHub.** In **Open from GitHub…**, each repository row ends in a small **↗** (tooltip **Open owner/repo on GitHub**), shown while the pointer is on the row, it has keyboard focus or the row is selected; it opens `https://github.com/<owner>/<repo>`. Right-click any row for **Open on GitHub ↗** (shared rows keep **Remove from list** under it). The ↗ has its room kept, so nothing in the row moves when it shows.

Desktop only, as before. Docs: `docs/github.md`; release note `docs/changes/unreleased/feat-github-button-status-bar.md`.

## Why it matters

The cloud sat among the editing commands although it is about where the drawing lives, which is what the status bar's chip already shows; next to the chip, the button and the state of the drawing in front read as one thing. Out of the command bar, it also gives the tabs their room back at narrow widths. In the picker there was no way to reach a repository on GitHub itself (its issues, settings or README) without leaving ReShiki and typing its name.

## Approach

- `status_bar` (`src/app/workspace.rs`) puts `github_button()` first, in its own place outside the flexible status region, so the status message gives way first when the controls on the right are wide (a long theme name), and the button keeps its 32 × 32 pt. The chip is the first item of the status region. The button uses the status bar's height (32 pt instead of 36) and its tooltip above; its badge and dot offsets follow.
- The menu is the existing popover (`src/app/popover.rs`), which already places a menu above its anchor when it does not fit below; nothing new there.
- The theme editor replaces the status bar, so the button and chip are not there, as the chip already was not. GitHub stays reachable through the command palette (Open from GitHub, Send, History, Sign out), and Send keeps its existing dialog fallback (`send_on_chip`). No new UI.
- Repository rows: the name sits in a clipped, filling container so a long name is cut off instead of pushing the state, lock or ↗ out; the ↗'s 18 pt slot is reserved at the row's end (a glyph when the row is selected, empty space otherwise) and the button is laid over it with `hover`, so it shows on the pointer or focus and keeps one place in the accessibility tree. The row menu now exists for every row. `State::repo_page` builds the URL once, and both entry points send the existing `Action::OpenRepo`, the same browser-opening path as **Open on GitHub ↗** elsewhere.
- Tests (`src/app/github/tests/status_bar.rs`, real renderer): the button's place at 1280 and 1040 pt and at a width where the controls overflow, no GitHub button in the command bar, Tab order (inspector toggle, cloud, chip, then the rest), the menu above the button with History and Open from GitHub working from there; signed out; the theme editor's palette rows and Send dialog; each repository row's ↗ (place, name, Tab order, click opens the page and not the repository), the right-click menu with the right URL, and a long name that keeps the ↗'s room. `tab_strip_clicks_switch_and_close_tabs` (three 84 pt tabs at 1040 pt) still passes.

## Evidence

Real app on macOS arm64 (debug builds), window 1280 × 852 pt unless noted, against the **local mock GitHub** (`src/github/mock.rs`, `RESHIKI_GITHUB_CLIENT_ID=mock` with the API and web overrides; user `@octo-test`), each launch with a fresh `RESHIKI_DATA_DIR`, driven by Codex computer use; every image is a capture of the ReShiki window only. Steps, the same on both builds: launch signed out, open the GitHub menu, **Sign in…** (the mock approves the code), **Open from GitHub…** → lab-notes → ring.rsk, move it and save (one unsent drawing), open the menu, open the picker and point at reaction-notes, right-click it, then two new tabs and the window set to 1040 pt.

- **Before**: main at `6cb84b674` (the later commits on main touch ChemDraw import and CI only).
- **After**: this branch, build of `05c1de1b`'s app code (the head adds only a test change).

### Idle, signed in, a GitHub drawing in front

| Before | After |
| --- | --- |
| <img src="before/light-03-idle-signed-in.png" width="440"><br>The cloud sits in the command bar after Save as; the chip **● lab-notes · 1 unsent [Send]** comes after the status message **Document saved**. | <img src="after/light-03-idle-signed-in.png" width="440"><br>The command bar has no cloud. The status bar starts with the cloud (dot and **O** badge), then **● lab-notes · 1 unsent [Send]**, then **Document saved**. |
| <img src="before/dark-03-idle-signed-in.png" width="440"> | <img src="after/dark-03-idle-signed-in.png" width="440"> |

### The GitHub menu

| Before | After |
| --- | --- |
| <img src="before/light-04-menu-open.png" width="440"><br>Opens downward from the command bar. | <img src="after/light-04-menu-open.png" width="440"><br>The same items (**Open from GitHub…**, **Send 1 drawing**, **History**, **@octo-test**, **Add repositories… ↗**, **Sign out**), opening upward from the bottom-left corner. |
| <img src="before/dark-04-menu-open.png" width="440"> | <img src="after/dark-04-menu-open.png" width="440"> |

### Signed out

| Before | After |
| --- | --- |
| <img src="before/light-01-signed-out.png" width="440"> | <img src="after/light-01-signed-out.png" width="440"><br>The cloud stays at the bottom left, without badge or dot (tooltip **GitHub · Not signed in**). |
| <img src="before/light-02-signed-out-menu.png" width="440"> | <img src="after/light-02-signed-out-menu.png" width="440"><br>**Open from GitHub…**, **Send to GitHub…**, **Sign in…**, upward. |
| <img src="before/dark-02-signed-out-menu.png" width="440"> | <img src="after/dark-02-signed-out-menu.png" width="440"> |

### 1040 pt window, three tabs

| Before | After |
| --- | --- |
| <img src="before/light-07-narrow-three-tabs.png" width="440"><br>The GitHub tab is cut to **ring.…** beside two Untitled tabs. | <img src="after/light-07-narrow-three-tabs.png" width="440"><br>With the cloud gone and 4 px gaps, **ring.rsk**, **Untitled** and **Untitled** show in full. |
| <img src="before/dark-07-narrow-three-tabs.png" width="440"> | <img src="after/dark-07-narrow-three-tabs.png" width="440"> |

### Repository rows in Open from GitHub…

<img src="after/rows-closeup-light-dark-before.png" width="640">

Close-up of the repository list, from the captures below: after, light and dark (pointer on reaction-notes; right-click), then before. lab-notes is selected and shows its ↗; reaction-notes shows it under the pointer; spectra shows none, and its lock stays where the other rows' locks are. Right-click shows **Open on GitHub ↗** (reaction-notes is not shared, so there is no **Remove from list**). Before, the rows had no ↗ and right-click did nothing.

| Before | After |
| --- | --- |
| <img src="before/light-05-picker-row-hover.png" width="440"> | <img src="after/light-05-picker-row-hover.png" width="440"> |
| <img src="before/light-06-row-context-menu.png" width="440"> | <img src="after/light-06-row-context-menu.png" width="440"> |
| <img src="before/dark-06-row-context-menu.png" width="440"> | <img src="after/dark-06-row-context-menu.png" width="440"> |

Not clicked in these runs: the ↗ and **Open on GitHub ↗** open a browser. The renderer test below checks the message they send and the URL.

## Verification

<!-- VERIFICATION_TABLE -->

Commands, on `05c1de1b` (the head's tree):

- `cargo fmt --all --check`
- `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`
- `cargo clippy -p reshiki-web -p reshiki -p reshiki-web-worker --lib --bin reshiki --target wasm32-unknown-unknown --locked -- -D warnings`
- `cargo test --locked --no-default-features -p reshiki --lib --bins`: 490 + 1805 passed
- `cargo test --locked --no-default-features -p reshiki --bin reshiki -- --include-ignored --test-threads=1 --skip manual_`: 1962 passed (the renderer tests, including the four new ones and `tab_strip_clicks_switch_and_close_tabs`)
- `python3 scripts/module_index.py --check`, `python3 scripts/copy_lint.py`, `bun scripts/check_docs_tree.mjs`, `uv run --locked python scripts/assemble_changelog.py --check`

Linux and Windows run in this PR's CI.

## Review

An independent adversarial review (Codex, read-only) of the whole diff found no P0–P2 problems and two P3s, both fixed in the last commit (a second read-only review of that commit found nothing further):

- The ↗ showed only inside the row's padding: a pointer on the row's outer 4–6 px highlighted the row without showing it. The padding now sits inside the hover area.
- The long-name assertion could pass with the selected row's own ↗ removed, because the hidden ↗ button also reports an 18 pt "↗" text. The test now counts: two ↗ texts on the selected row, one on each other row.

An earlier review on the first commit found that the button could be squeezed out by a very long theme name in the status bar, and that a long repository name could take the ↗'s room; the second commit fixed both, with tests.

## Risk

Low. Layout of one button and the picker's repository rows; no data or network changes.

- People who learned the cloud's place in the command bar have to find it at the bottom left. The docs and release note say where it went.
- In the theme editor the button is not shown; GitHub is in the command palette there.

## Release-note material

One-sentence user-facing caption: the GitHub button now sits at the left end of the status bar, beside the repository chip, and each repository in **Open from GitHub…** links to its page on GitHub.

Fragment: `docs/changes/unreleased/feat-github-button-status-bar.md`.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

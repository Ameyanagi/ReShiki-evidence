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

Pending: real-window captures before (main) and after, light and dark, are being taken.

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | pending |
| PR CI | pending |

Pending: the full check run on the branch head.

## Review

Pending: an independent adversarial review of the diff.

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

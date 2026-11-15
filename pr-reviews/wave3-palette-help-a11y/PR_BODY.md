## Summary

Wave 3 of the UI audit: command palette, Help and accessibility polish (U8, U9, U10), plus a keyboard fix for the style bar's Font box.

- **U10, palette.** Until a command has run, an empty palette opens on a **Start here** group: **Import structure or name**, **Benzene**, **Open…**, **Clean up structure**, **Molecular formula and properties**, **Predict NMR**, **Export panel** and **Help & shortcuts**. The other commands follow under **More commands**. On main it opened on Cyclopropane and the other ring templates. Once something has run, recent commands lead as before.
- **U10, Help.** Help rows that are also palette commands (**Select all**, **Fit drawing**, …) are marked **Run ↩**. **Enter**, or **Run** in the preview, runs the command and closes Help, after a click on the row too. When the command cannot run now, Help stays open, **Run** is disabled and the reason shows under it. The footer "Reference only: nothing runs" now reads "↩ runs rows marked Run". Help and the palette run commands through the same gate, so a caption you are typing is applied first.
- **U8, interface font.** The interface uses the platform's Latin sans-serif first: Helvetica Neue on macOS, Segoe UI on Windows, Noto Sans (else DejaVu Sans) on Linux. Main used Hiragino Sans everywhere, which draws "…" centered, so **Predict NMR…** read as "Predict NMR···". CJK text in the interface falls back per script; on a Japanese system locale (`ja`, `ja-JP`) kanji keep Japanese forms. Drawing labels keep their own fonts.
- **U9, accessibility (partial).** Keyboard focus is drawn as a 2 px ring 3 px outside the control, with a 1 px gap, instead of a clipped inner border that looked like the selected state. New named controls: document tabs ("aldol.rsk tab, edited, selected") and their Close buttons, the new-tab and overflow buttons, the side-panel tabs, **B** / **I** / **U** / CH₂ / x₂ / x² (with checked state), the font size field, the light/dark canvas button, and the **Font**, **Journal preset** and **Color theme** lists (accessible combo boxes; ↑ ↓ step a focused journal preset or theme list).
- **Font box keyboard fix.** Tab now lands in the Font box's search field, typing searches, ↑ ↓ move the open list's highlight, Enter picks the font and keyboard focus goes back to the drawing. The vendored iced `ComboBox` now forwards widget operations (focus) to its search field and takes an id, and Tab traversal relays the view out.

No issue is filed for these items, so this PR closes none.

## Why it matters

- **Palette (U10).** The palette is the main way to find a command, and a new user opens it with an empty query. On main the first screen was 977 commands starting with Cyclopropane, cyclobutane and other ring templates, none of which is a useful first step.
- **Help (U10).** Help already found the command a user was looking for, then said "Reference only: nothing runs". The user had to close it and run the same thing again from the palette or the menus.
- **Interface font (U8).** Every label ending in "…" (menu items that open a dialog, "Calculating selection…") read as a centered "···", in every locale. The audit measured the ellipsis glyph top at 0.449 em above the baseline in Hiragino Sans; the new model test requires < 0.2 em.
- **Focus and names (U9).** A focused button looked the same as the active or selected one, so keyboard users could not tell where focus was. Screen readers saw the document tabs, side-panel tabs, style buttons and lists as unnamed groups or not at all.
- **Font box.** Tab skipped the Font box entirely on main (iced's combo box did not pass focus operations to its field), so the font could only be chosen with the mouse.

## Approach

- **Palette.** `START_HERE` is a fixed list of command names. With an empty query and no recents it ranks those first under headings; a category chip hides the headings. The row scroll math counts the headings, so a group's heading scrolls into view with its first row.
- **Help → run.** When Help opens, each registry entry is matched once (case-insensitive name) to a non-template palette command; matches get **Run ↩**. Run goes through `App::run_command` and the same gate as the palette (`runs_unavailable_command`), so availability is checked before a caption draft is committed. A clicked row hands focus back to the search field so Enter works. Each Run button has its own id (`help-run-{index}`), so a press can never run a row selected after it started.
- **Font.** `ui_font_family()` checks a per-platform Latin list first and then the old CJK list. Label glyph fallback (`fallback_families`) is unchanged, so drawing measurement and goldens do not move. cosmic-text's Han fallback matches only the exact locale `ja`; `appearance::prepare_han_fallback` maps any `ja-*` system locale to `ja` before the first text is shaped.
- **Focus ring.** `accessibility::Button` draws the ring outside its bounds. It now takes focus on press only when no nested control (a tab's Close button) took it, so a tab and its Close never hold focus together, which used to empty the native accessibility tree.
- **Lists.** New `accessibility::select` wraps an iced pick list or combo box as an accessible `ComboBox`: a name, the shown value, `SetValue` by option name, and ↑ ↓ for pick lists. "Manage styles…" and "Manage themes…" are left out of the options. The Font combo keeps focus in its own search field, which needed the vendored `ComboBox::operate` forwarding and `.id()` (patch recorded in `vendor/patches/iced_widget.diff`).

Alternatives rejected:
- **Tab and Close as sibling controls** (the review's suggestion). With an overlay the top layer takes the press, so the tab below never sees it, and a row sibling cannot share the tab's background and hover. Fixing focus-on-press in the button keeps the layout.
- **A new accessible popup-button widget for every pick list now.** iced's `PickList` and `ComboBox` have no semantic hook; a full widget with options as separate nodes is a separate item. The wrapper covers the three lists in this lane's files.
- **The audit's ↵ for Run.** The app already prints Return as ↩ (`shortcuts::keys`), so Help uses ↩.
- **Keeping Hiragino Sans and substituting the ellipsis glyph.** That fixes one character and keeps Japanese-font Latin text in every locale; the platform's Latin font matches native apps and still reaches Hiragino for Japanese.

## Evidence

Real app on macOS arm64, one build at a time, each launch with a fresh `RESHIKI_DATA_DIR` and the build itself as the InChI and naming helper. **Base** is main `fcd2cde6`; **branch** is the PR head `a4b1b1c2`. Both are debug builds of `cargo build --locked --bin reshiki` (sha256 `882df4f4…` and `e47693db…`). Window 1280 × 852 pt (2560 × 1704 px captures), light appearance, system language en-JP. Input `caffeine.rsk` at Fit zoom **193%**; the second tab is `骨格直鎖.mol` (one benzene ring, a kanji file name on purpose). Codex computer use (gpt-6.1-sol) drove both builds with the same keys, and every screenshot shows only the ReShiki window. Table cells are crops of those windows; the full windows sit next to them in the folder. I checked every image.

The branch is 107 commits behind main (merge base `621e7ab1`). Two differences in these shots come from that, not from this PR: main's Help footer has an **About ReShiki** button and the "Reference only: nothing runs" line wraps; the branch's Help has no About button yet.

### U10: command palette opens on Start here

| Base `fcd2cde6` | Branch `a4b1b1c2` |
| --- | --- |
| <img src="crops/base-03-palette-fresh-palette.png" width="420"> | <img src="crops/branch-03-palette-fresh-palette.png" width="420"> |
| Fresh app, nothing run yet, `:` with an empty search: All 977, first rows Cyclopropane, Cyclobutane … Chair B, Cyclopentadiene. | Same: **Start here** (Import structure or name, Benzene, Open…, Molecular formula and properties, Predict NMR, Export panel, Help & shortcuts, then the greyed Clean up structure), then **More commands** from Cyclopropane. |
| <img src="crops/base-07-palette-after-help-run-palette.png" width="420"> | <img src="crops/branch-07-palette-after-help-run-palette.png" width="420"> |
| After Help → "select all" → Return (nothing ran on base), `:` again: unchanged, Cyclopropane first. | After Select all ran from Help, `:` again: **Select all** leads as a recent command and the headings are gone. |

### U10: Help runs commands

| Base `fcd2cde6` | Branch `a4b1b1c2` |
| --- | --- |
| <img src="crops/base-05-help-select-all-help.png" width="420"> | <img src="crops/branch-05-help-select-all-help.png" width="420"> |
| `?`, type "select all": no Run marks; footer "… · Reference only: nothing runs". | Same: rows that are commands show **Run ↩**, the preview has a **Run ↩** button, and the footer reads "↑ ↓ move · ↩ runs rows marked Run · Esc closes · Uppercase means Shift-letter". |
| <img src="base-06-help-after-enter.png" width="420"> | <img src="branch-06-help-after-enter.png" width="420"> |
| Return: Help stays open and nothing is selected. | Return: Help closes and the molecule and its caption are selected (14 atoms · 1 object · 15 bonds). |

### U9: focus ring outside the control

| Base `fcd2cde6` | Branch `a4b1b1c2` |
| --- | --- |
| <img src="crops/base-08-help-tab-2-footer.png" width="420"> | <img src="crops/branch-08-help-tab-2-footer.png" width="420"> |
| Help open, Tab to **Open shortcut examples** (2× zoom of the footer): focus is a border on the button's edge, the same weight as Done's own border, so the focused and the default button look alike. | Same keys: a 2 px ring 3 px outside the button, with a light gap, clearly different from Done. |

### U8: interface font and the ellipsis

| Base `fcd2cde6` | Branch `a4b1b1c2` |
| --- | --- |
| <img src="crops/base-01-start-panel.png" width="420"> | <img src="crops/branch-01-start-panel.png" width="420"> |
| Properties panel, nothing selected (1:1 crop): Hiragino Sans, **"Predict NMR···"** with centered dots. | Same: Helvetica Neue, **"Predict NMR…"** on the baseline. The narrower font also lets the context row show "3D optimize…" where base folds it into "⋯" ([base](base-01-start.png), [branch](branch-01-start.png)). |
| <img src="crops/base-09-two-tabs-kanji-6x.png" width="420"> | <img src="crops/branch-09-two-tabs-kanji-6x.png" width="420"> |
| Tab title `骨格直鎖.mol`, 6× zoom: Hiragino Sans, Japanese glyph forms (compare 骨 and 直). | Same, on this Mac's **en-JP** system language: PingFang SC, **Simplified Chinese forms** of 骨 and 直. The `ja-*` mapping does not cover `en-JP`; see Risk. |

### Font box with the keyboard

Same keys on both builds: click the empty canvas, Tab × 15, type `Helv`, ↓ ↓, Return, `:`. Crops show the top-left 2000 × 1260 px of each 2560 × 1704 px window.

| Base `fcd2cde6` | Branch `a4b1b1c2` |
| --- | --- |
| <img src="crops/base-font-15-tab-view.png" width="420"> | <img src="crops/branch-font-15-tab-view.png" width="420"> |
| Tab 15 lands on the Lasso tool. The order went from **Show or hide inspector** to the **pt** field (Tab 12), skipping the Font box, B / I / U and the document tab. | Tab 15 lands in the Font box's **search field** ("Search fonts…", caret) and the font list opens. |
| <img src="crops/base-font-16-typed-view.png" width="420"> | <img src="crops/branch-font-16-typed-view.png" width="420"> |
| `Helv`: the letters go to keyboard drawing and add an **HCl** label to the drawing (red status "This atom has no available valence…"). | `Helv`: the list narrows to Helvetica and Helvetica Neue. |
| <img src="crops/base-font-18-enter-view.png" width="420"> | <img src="crops/branch-font-18-enter-view.png" width="420"> |
| ↓ ↓ moved the drawing hotspot to C 6; Return switched to the Lasso tool. Font still Arial. | ↓ ↓ move the list highlight and the field keeps "Helv"; Return picks **Helvetica**, closes the list, no ring left on the Font box. |
| <img src="crops/base-font-19-colon-view.png" width="420"> | <img src="crops/branch-font-19-colon-view.png" width="420"> |
| `:` opens the palette (on the new HCl atom). | `:` opens the palette: keyboard focus went back to the drawing, not into the Font field. |

Each Tab stop is in the folder (`base-font-*`, `branch-font-*`; the Codex runs captured all 15). The branch also stops on the document tab and its × ([tab](branch-font-06-tab.png), [×](branch-font-07-tab.png)); base goes from Save as to Assistant ([base Tab 6](base-font-06-tab.png)).

### U9: journal preset list takes focus; ↑ ↓ choose

| Base `fcd2cde6` | Branch `a4b1b1c2` |
| --- | --- |
| <img src="crops/base-jp-back-05-status.png" width="420"> | <img src="crops/branch-jp-back-07-status.png" width="420"> |
| From the canvas, Shift+Tab: Fit, +, −, View, then the 5th press jumps to the inspector's Drawing style heading. The JACS / ACS and Publication lists are never focused. | Shift+Tab: Fit, +, −, View, **Dark canvas**, **Color theme**, then at the 7th press **JACS / ACS** with the focus ring. |
| | <img src="crops/branch-jp-jp-down-status.png" width="420"> |
| | ↓ chooses the next preset, **Nature** (status "Nature applied", drawing restyled); ↑ goes back to **JACS / ACS** ([↑](crops/branch-jp-jp-up-status.png)). |

### U9: accessibility tree

Dump of the macOS accessibility tree with both tabs open ([base](base-ax-tree.txt), [branch](branch-ax-tree.txt), [diff](ax-tree-diff.txt)). Base has none of these controls; the branch adds:

```text
AXButton  'caffeine.rsk tab'            AXButton  'Close caffeine.rsk'
AXButton  '骨格直鎖.mol tab, edited, selected'   AXButton  'New tab'
AXButton  'Properties tab, selected'    AXButton  'Predict tab' / 'Templates tab' / 'Import tab' / 'Export tab'
AXPopUpButton 'Font' = 'Arial'          AXTextField 'Font size in points' = '10'
AXCheckBox 'Bold' / 'Italic' / 'Underline' / 'Chemical formula formatting' / 'Subscript' / 'Superscript' = False
AXPopUpButton 'Journal preset' = 'JACS / ACS'   AXPopUpButton 'Color theme' = 'Publication'
AXCheckBox 'Dark canvas' = False
```

### Found while capturing: a focus ring behind Help

| Base `fcd2cde6` | Branch `a4b1b1c2` |
| --- | --- |
| <img src="crops/base-08-help-tab-1-help.png" width="420"> | <img src="crops/branch-08-help-tab-1-help.png" width="420"> |
| After Help → "select all" → Return, Escape, `:` and Escape, `?` again and Tab once: focus on Help's **About ReShiki** button, inside the dialog. | Same keys: the toolbar's **ReShiki / About** button *behind* the dialog gets a focus ring. It keeps it on the next two Tabs while Open shortcut examples and then Done also show rings ([Tab 2](branch-08-help-tab-2.png), [Tab 3](branch-08-help-tab-3.png)). |

A fresh launch with only `?` and Tab does not show it: Tab 1 lands on Open shortcut examples and the toolbar has no ring ([branch](branch-10-help-fresh-tab-1.png), [merge base `621e7ab1`](mergebase-10-help-fresh-tab-1.png)). I did not narrow down which earlier step (running Select all from Help, or opening the palette) sets it up. See Risk.

## Verification

VERIFICATION_TABLE

Run by the lane on macOS arm64 (before the two Font box commits):

- `cargo fmt --all --check`, `cargo clippy --workspace --lib --bins --all-features --locked -- -D warnings`, `cargo clippy -p reshiki --all-targets --all-features --locked -- -D warnings`: pass.
- `cargo test --locked --bin reshiki` with `RESHIKI_INCHI_HELPER` / `RESHIKI_NAMING_HELPER` set and `RESHIKI_REQUIRE_INCHI_HELPER=1`: 1584 passed, 0 failed, 188 ignored. `cargo test --locked -p reshiki --lib`: 391 passed. `cargo test --locked -p reshiki-model`: 1437 passed.
- Opt-in renderer tests with the helper env: `app::shortcut_focus_tests::` 37 passed (tab and Close never focused together, tab focus survives bringing a tab to the front, Help runs a clicked row with Enter, Help Run never runs a row selected after the press started, style lists by keyboard and by name, named tabs, style buttons and canvas theme); `app::accessibility::` 24 passed; library `accessibility::` 9 passed (the focus ring reaches outside the control and stays within 3 px).
- New unit tests: `start_here_leads_an_empty_palette_until_a_command_runs`, `rows_that_name_a_palette_command_run_it`, `help_and_the_palette_treat_a_caption_draft_alike`, `interface_font_sets_the_ellipsis_on_the_baseline` (fails on main: Hiragino Sans draws "…" 0.449 em above the baseline), `japanese_locales_set_han_only_interface_text_in_japanese_forms` (macOS only).
- Font box commits `0dec7854`, `a4b1b1c2`: opt-in renderer tests `tab_reaches_the_font_search_field_and_arrows_move_its_list` and `tab_traversal_lays_the_view_out_again`; vendored patch recorded in `vendor/patches/iced_widget.diff`.
- `bun fmt --check` on the changed Markdown, `assemble_changelog.py --check`, `check_docs_tree.mjs`: pass.
- CI on this PR at `a4b1b1c2`: all green, including the Rust jobs on Linux x64 and Windows x64 (lint + goldens and both test shards), Rust geometry on Linux and Windows (x64 and arm64), wasm, Python, the clipboard jobs and Office add-in.
- Real app on macOS arm64: the screenshots above, plus the accessibility tree dump.

Not run: real-app checks on Arch Linux x64, Ubuntu arm64 and Windows x64. There the interface font changes to Noto Sans (else DejaVu Sans) and Segoe UI, which this PR does not show in a screenshot. Not tried: VoiceOver, Narrator or Orca with the new controls, and the focus ring on a dark system appearance.

## Risk

- **Kanji in Chinese forms on an English system with a Japanese region (seen in Evidence).** The Han fix maps only system locales whose first subtag is `ja`. This Mac reports `en-JP` (preferred languages `en-JP`, `ja-JP`), so kanji in tab titles and other interface text switch from Hiragino Sans (main) to PingFang SC, with Simplified Chinese glyph forms. Users with an English UI and Japanese region or Japanese as a second language, which includes the owner's machine, will see this. A fix would also map a `JP` region, or any `ja` in the preferred-language list, to `ja`; it is not in this PR.
- **U9 is partial.** Done: focus ring, named document and panel tabs, Close and new-tab buttons, style buttons with checked state, font size field, canvas theme, and the Font, Journal preset and Color theme lists (keyboard focus and ↑ ↓ for the two pick lists, value set by option name). Not done: about 22 other `appearance::pick_list` call sites (inspector, graphics, pages, generic, typography, theme generator, color popover, numeric transforms) still have no name, role or keyboard focus. The three wrapped lists expose no option nodes: assistive technology can set the value by name but not browse the options, and a native Click does not open the iced menu. Screen readers were not tried. This needs a real accessible popup-button widget as a follow-up item.
- **Focus ring behind Help (seen in Evidence, not explained).** In one sequence (Help ran Select all, the palette opened and closed, Help reopened), the first Tab put a ring on the toolbar's About button behind the modal, and it stayed while focus moved through the dialog. Main in the same sequence and a fresh branch launch do not show it. It may be a Tab escaping the modal or a stale focus flag; it needs a look before merge.
- **Longer Tab order.** Document tabs, their Close buttons, B / I / U, CH₂, x₂, x² and the three lists are new Tab stops. From the canvas the Font box is 15 Tabs away and the status-bar lists are more than 45 (7 with Shift+Tab).
- **Interface font everywhere.** Every interface string changes font, so text widths change and context-row folding moves (at 1280 pt the branch shows "3D optimize…" where main shows "⋯"). View-parity baselines (`RESHIKI_VIEW_PARITY`) will differ for every view and need recapturing after the waves merge.
- **Merge.** The branch is 107 commits behind main. GitHub reports it mergeable, but main's Help footer gained an About ReShiki button (`c09e7a4b`), so the merged footer has three buttons and the new "↩ runs rows marked Run" hint; check that it still fits at 1040 pt. Start here and the Help ↔ palette links match command names exactly (Start here) or case-insensitively (Help); if another PR renames one of the eight Start here commands, `start_here_leads_an_empty_palette_until_a_command_runs` fails and the list needs updating.
- **Vendored iced change.** `ComboBox::operate` now forwards to its text input and `ComboBox::id` is new. Any other combo box in the app becomes reachable by Tab as well.

## Changelog

`docs/changes/unreleased/wave3-palette-help-a11y.md` (section Changes):

- The interface uses the platform's own sans-serif: Helvetica Neue on macOS, Segoe UI on Windows and Noto Sans on Linux. A label ending in "…", such as **Predict NMR…**, no longer reads as "Predict NMR···". Japanese and other CJK text in the interface comes from the system's CJK font; on a Japanese system, kanji keep their Japanese forms. Drawing labels keep their own fonts.
- Before any command has run, the command palette opens on a **Start here** group: **Import structure or name**, **Benzene**, **Open…**, **Clean up structure**, **Molecular formula and properties**, **Predict NMR**, **Export panel** and **Help & shortcuts**. It used to open on Cyclopropane and the other ring templates.
- Help rows that are also commands, such as **Select all** or **Fit drawing**, are marked **Run ↩**. **Enter** or **Run** runs the command and closes Help, after a click on the row too; when it cannot run now, Help says why. A caption you are typing is applied first, as from the command palette.
- Keyboard focus is drawn as a ring around the control, with a gap, so a focused button no longer looks like the selected one.
- Screen readers can reach the document tabs and their close buttons, the side panel's tabs, the font size field, the **B**, **I**, **U**, formula, subscript and superscript buttons, the font, journal preset and color theme lists, and the light/dark canvas button. Tabs say whether they are selected or edited. With a journal preset or color theme list focused, **↑** and **↓** choose the previous or next option.

The fragment does not mention the Font box keyboard fix. Suggested extra line: "**Tab** reaches the **Font** box: type to search, **↑** **↓** move through the list, **Enter** picks the font and returns to the drawing."

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none added. `vendor/iced_widget` (MIT) was already vendored; this PR extends its existing patch, recorded in `vendor/patches/iced_widget.diff` and `vendor/README.md`.

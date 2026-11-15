# ReShiki Settings page — real-app UI verification

Date: 2026-11-15 (Asia/Tokyo). Target: the supplied `feat/settings-page` debug wrapper at `/Users/shiranui/dev/reshiki-targets/apps/settings/ReShiki.app`, using its isolated data directory. Sample: `/Users/shiranui/dev/reshiki-targets/apps/sample/aspirin.mol`.

Core Settings navigation, background selection, saved colors, resolution selection, appearance switching, closing/focus, Export synchronization, and native editable-off paste worked. The exact Preview Cmd+A sequence copied PDF text rather than a picture; a separate rectangular picture-selection test returned a single Picture object to ReShiki as expected. Three UI/accessibility defects and several UX improvements are listed below.

This was a UI verification, using native screenshots, clicks, keys, and clipboard type observations. No source files were edited. ReShiki was launched only with the supplied wrapper commands. No update check, network action, account action, or macOS setting change was initiated. All 65 screenshots are saved as PNG files in this directory. The computer-use screenshot API supplied JPEG-encoded captures; those 63 captures were re-encoded to actual PNG without resizing or altering their content. The two screen-region captures were native PNG. Most show only the relevant app window; screenshots 49 and 64 are screen-region captures used when there was no usable app-window binding or after quitting.

## 1. Launch, sample, Cmd+, — PASS

**Expected:** Launch the wrapped build, open the aspirin sample, and open Settings with Cmd+,.

**Observed:** The sample loaded as aspirin with 13 atoms and 13 bonds, formula C₉H₈O₄. Cmd+, opened Settings with Appearance selected and the Search settings field focused. The wrapper launch and the specified `open -a <wrapper path> <sample>` commands both completed successfully.

**Evidence:** [00-sample-loaded.png](00-sample-loaded.png), [01-settings-open.png](01-settings-open.png).

## 2. Visit every section — PASS

**Expected:** Each of the six sections should be reachable and render its controls.

**Observed:** All six opened without visible errors:

| Section | Visible content | Screenshot |
|---|---|---|
| Appearance | Interface: Match canvas / Light / Dark; Canvas for new drawings: Light / Dark | [01-settings-open.png](01-settings-open.png) |
| Drawing | Smart guides, Arrange controls, Drawing Style units pt / mm / cm | [02-drawing.png](02-drawing.png) |
| Copy & export | Background controls for copies and exports, Your colors, with PNG resolution below the initial viewport | [03-copy-export.png](03-copy-export.png) |
| Names & checks | Chemical name typography, molecular-weight decimals, IUPAC notes, unknown-configuration notation | [04-names-checks.png](04-names-checks.png) |
| Assistant | Model, disconnected reasoning explanation, Accept all edits | [05-assistant.png](05-assistant.png) |
| Updates | Automatic-update preference and Stable / Nightly channel | [06-updates.png](06-updates.png) |

No update-check action was clicked. Assistant and update functionality were only viewed.

## 3. Search resolution, background, nonsense; clear — PASS with labeling defect B1

**Expected:** Matching settings across sections, then an empty state for nonsense, then normal browsing after clearing.

**Observed:**

- `resolution` showed Copy & export with both PNG resolution selectors and all four close-ups. Defaults were Copy 300 dpi and Export 1200 dpi. Other categories were disabled and a result count appeared beside Copy & export.
- `background` showed the background selectors and Your colors. However, the first selector lost its **Copied pictures** heading while **Exported files** remained above the second selector (B1).
- `zzznomatchxyz` showed “No setting matches. Try background, units or channel.”
- Clearing with Cmd+A, Backspace restored normal category browsing and the previously selected Updates section. Search was cleared again after subsequent search-based navigation.

**Evidence:** [07-search-resolution.png](07-search-resolution.png), [08-search-background.png](08-search-background.png), [09-search-empty.png](09-search-empty.png). The later unfiltered background states in screenshots 10–21 also demonstrate the cleared search.

## 4. Background choices and saved colors — PASS

**Expected:** Each copy background is selectable; hex and palette colors become saved Custom colors; selecting a saved color updates Custom; Esc dismisses only the picker; export Custom uses the same color.

**Observed:**

1. Selected Copied pictures backgrounds in order: Transparent, Canvas, White, Black, Custom. Each selected state changed correctly. Initial Custom was `#F4EFE6`.
2. The Your colors `+` opened a picker with Strong and Tint palettes and a field showing hexadecimal, RGB, and OKLCH input examples.
3. Entered `#1F4E79` and clicked Add. The picker closed, a blue saved swatch appeared, and Copied pictures became Custom `#1F4E79`.
4. Opened `+` again and clicked the green Strong palette swatch. This immediately saved `#27762F`, closed the picker, and made it the copy Custom color. A separate Add click was not needed for palette selection.
5. Clicked the saved blue swatch. Copy Custom returned to `#1F4E79`.
6. Selected Exported files → Custom. Both Custom selectors showed the same blue swatch; their accessibility labels agreed on `#1F4E79`.
7. Reopened the picker and pressed Esc. Only the picker closed; Settings remained visible with its controls intact.

**Evidence:** [10-copy-transparent.png](10-copy-transparent.png), [11-copy-canvas.png](11-copy-canvas.png), [12-copy-white.png](12-copy-white.png), [13-copy-black.png](13-copy-black.png), [14-copy-custom-default.png](14-copy-custom-default.png), [15-color-picker.png](15-color-picker.png), [16-color-hex-entered.png](16-color-hex-entered.png), [17-color-hex-added.png](17-color-hex-added.png), [18-color-picker-second.png](18-color-picker-second.png), [19-palette-color-added.png](19-palette-color-added.png), [20-saved-blue-copy-export-custom.png](20-saved-blue-copy-export-custom.png), [21-picker-escape-settings-stays.png](21-picker-escape-settings-stays.png).

The actual blue output is visible later in Preview and TextEdit (screenshots 50 and 51).

## 5. PNG resolution choices and close-ups — PASS

**Expected:** All four copy resolutions select correctly, Copy/Export tags move to their associated close-ups, pixel dimensions scale with resolution, Export accepts 600 dpi, and final values return to Copy 300 / Export 1200.

**Observed:** Each selector updated its selected state and the associated green outline/tag. At 1200/1200, the final close-up displayed both Copy and Export tags. The displayed whole-drawing dimensions were consistent across Settings and Export:

| Resolution | Whole-drawing pixels | Copy evidence |
|---|---:|---|
| 150 dpi | 171 × 134 px | [24-copy-150-closeups.png](24-copy-150-closeups.png) |
| 300 dpi | 341 × 268 px | [25-copy-300-closeups.png](25-copy-300-closeups.png) |
| 600 dpi | 681 × 536 px | [26-copy-600-closeups.png](26-copy-600-closeups.png) |
| 1200 dpi | 1361 × 1071 px | [27-copy-1200-closeups.png](27-copy-1200-closeups.png) |

Rounding aside, doubling dpi approximately doubled each dimension. Close-ups became visibly smoother at higher resolutions. Export was changed to 600 and its tag moved to the 600 card: [28-export-600-closeups.png](28-export-600-closeups.png). Final values were restored to Copy 300 and Export 1200: [29-resolution-restored-300-1200.png](29-resolution-restored-300-1200.png).

The full section required scrolling. Search `resolution` was used to bring both selector rows and the complete strip into one screenshot. Supplemental scroll-position evidence: [22-resolution-controls.png](22-resolution-controls.png), [23-resolution-visible.png](23-resolution-visible.png).

## 6. Interface Dark, Light, Match canvas — PASS with contrast/hierarchy suggestions

**Expected:** Copy & export remains usable in both interface themes, then Interface returns to Match canvas.

**Observed:** Interface Dark changed Settings, toolbar, and inspector chrome while preserving the white drawing canvas. Copy & export labels and selected states remained legible. Light restored light chrome. Match canvas was selected again at the end.

Dark mode has very subtle card borders/separators, and the resolution close-ups stay white even when Custom blue is selected. These are UX observations, not evidence of incorrect exported output. No quantitative accessibility contrast measurement was performed.

**Evidence:** [30-dark-copy-export.png](30-dark-copy-export.png), [31-dark-resolution.png](31-dark-resolution.png), [32-light-copy-export.png](32-light-copy-export.png), [33-interface-restored-match-canvas.png](33-interface-restored-match-canvas.png).

## 7. Closing Settings and drawing keyboard focus — PASS

**Expected:** Esc, Done, and Cmd+, close Settings; immediate drawing shortcuts reach the drawing.

**Observed:**

- Pressed Esc with no picker open, then immediately Cmd+A. The drawing showed a selection bounding box, atom handles, and “13 atoms · 13 bonds.” [34-escape-focus-select-all.png](34-escape-focus-select-all.png).
- Reopened with Cmd+,, clicked Done, then immediately Cmd+A. Selection again appeared on the drawing. [35-done-focus-select-all.png](35-done-focus-select-all.png).
- Reopened with Cmd+, and pressed Cmd+, again. Settings closed. [36-command-comma-toggle-closed.png](36-command-comma-toggle-closed.png).

Cmd+A was used instead of modifying an atom, so no chemical edit needed undoing for this step. Later paste operations were undone with Cmd+Z.

## 8. Export Background hover, Resolution menu, Settings agreement — PASS; accessibility defect B2

**Expected:** Export has background swatches with names on hover and a resolution menu showing physical and pixel size, agreeing with Settings.

**Observed:** Export initially opened in PDF format, where resolution was not shown. Choosing PNG exposed Resolution. Custom blue was selected, matching Settings. Moving within that swatch revealed the tooltip “Custom, #1F4E79.” Resolution was 1200 dpi, 2.9 × 2.3 cm, 1361 × 1071 px. The menu offered all four expected dpi values and the pixel sizes listed in step 5.

Include editable drawing was visibly checked at this stage. The checkbox itself was missing from the native accessibility snapshot although neighboring controls were exposed (B2).

**Evidence:** [37-export-tab.png](37-export-tab.png), [38-export-background-tooltip.png](38-export-background-tooltip.png) (pointer on swatch; tooltip had not appeared yet), [39-export-format-menu.png](39-export-format-menu.png), [40-export-png.png](40-export-png.png), [41-export-custom-hover.png](41-export-custom-hover.png) (successful tooltip capture), [42-export-resolution-menu.png](42-export-resolution-menu.png), [ax-export-final.txt](ax-export-final.txt).

## 9. Right-click → Copy image on → White; clipboard types — PASS

**Expected:** Hover opens the submenu; choosing White copies a one-off image on White.

**Observed:** Right-clicking blank canvas opened a context menu. Hovering Copy image on opened a submenu with Transparent, Canvas, White, Black, both saved colors, the default marker, and Change the default…. Choosing White closed the menu and showed “Image copied.” The saved Custom default stayed blue; the one-off choice did not replace it.

**Evidence:** [43-canvas-context-menu.png](43-canvas-context-menu.png), [44-copy-image-on-submenu.png](44-copy-image-on-submenu.png), [45-copied-image-on-white.png](45-copied-image-on-white.png).

`osascript -e 'clipboard info'` immediately after the White copy returned the following (editable embedding was still ON):

```text
«class PDF », 11275, «class CDIF», 24898, «class CHMS», 24898, «class PNGf», 24806, «class svg », 8645, «class AVIF», 5208, «class 8BPS», 59546, GIF picture, 3561, «class jp2 », 17009, JPEG picture, 11703, TIFF picture, 368982, «class BMP », 365690, «class TPIC», 22224
```

Raw record: [clipboard-09-white-editable-on.txt](clipboard-09-white-editable-on.txt). The White selection and successful copy were verified in UI; the copied White image was not separately opened because step 10 replaced the clipboard with a Custom copy.

## 10. Editable OFF, external paste, round trips, cleanup — FAIL for the literal Preview Cmd+A route; remaining subchecks PASS

**Expected:** Settings and Export stay synchronized; external apps receive a picture; a picture copied back from Preview does not recover chemistry when embedding is off; direct ReShiki paste still preserves editable chemistry; test documents close without saving; embedding returns to ON.

**Observed subchecks:**

| Subcheck | Result | Evidence |
|---|---|---|
| Turn OFF in Settings | PASS. Switch changed from on to off. | [46-editable-settings-before.png](46-editable-settings-before.png), [47-editable-off-settings.png](47-editable-off-settings.png) |
| Export sync | PASS. Include editable drawing was visibly unchecked after closing Settings. | [48-editable-off-export-sync-copy.png](48-editable-off-export-sync-copy.png) |
| Select all, Cmd+C | PASS. Selected all atoms/bonds and copied; public picture formats were advertised. Status wording still said “Editable drawing and images copied” (B3). | Screenshot 48 and raw clipboard record below |
| Preview New from Clipboard | PASS. Cmd+N created an Untitled one-page PDF displaying white chemistry on the chosen blue Custom background. | [50-preview-new-from-clipboard.png](50-preview-new-from-clipboard.png) |
| TextEdit new rich-text document, paste | PASS. Received an attached picture on blue, not SMILES or ordinary text. | [51-textedit-paste-editable-off.png](51-textedit-paste-editable-off.png) |
| Literal Preview Cmd+A, Copy, ReShiki Paste | FAIL to produce a picture round trip. Preview selected PDF label text `H O O O O`; the clipboard contained text formats. ReShiki reported “Could not paste: Invalid SMILES at byte 0.” No picture or editable molecule was inserted. This is a test-path/Preview selection-mode issue, not proof that embedding-off failed. | [52-preview-select-all-copy.png](52-preview-select-all-copy.png), [53-preview-text-copy-back-to-reshiki.png](53-preview-text-copy-back-to-reshiki.png) |
| Explicit Preview picture selection, Copy, ReShiki Paste | PASS. Chose Tools → Rectangular Selection and dragged a region. The clipboard then contained PDF/image formats. ReShiki inserted one **PICTURE**, 40 × 31 pixels, with picture resize controls and “No atoms selected.” It did not recover editable chemistry. The selected region was cropped, rather than the whole page. | [54-preview-rectangular-copy.png](54-preview-rectangular-copy.png) (Cmd+A alone still showed text), [55-preview-region-selected.png](55-preview-region-selected.png), [56-preview-picture-paste-back.png](56-preview-picture-paste-back.png) |
| ReShiki copy again, direct ReShiki paste while OFF | PASS. After undoing the Picture, copied the original drawing. A completed paste inserted another molecule with editable atom handles, selected 13 atoms/13 bonds, and whole-drawing formula C₁₈H₁₆O₈. | [57-direct-reshiki-paste-editable-off.png](57-direct-reshiki-paste-editable-off.png), [58-direct-reshiki-paste-confirmed.png](58-direct-reshiki-paste-confirmed.png) |
| Undo test insertions | PASS. Both the Picture and duplicated molecule were undone. Final screenshot shows one aspirin drawing. | [63-final-restored-before-quit.png](63-final-restored-before-quit.png) |
| Restore ON and reverse sync | PASS. Checked Include editable drawing in Export, then reopened Settings; Put the editable drawing in pictures was ON. | [59-editable-on-restored-export.png](59-editable-on-restored-export.png), [60-editable-on-restored-settings.png](60-editable-on-restored-settings.png) |
| Close created documents without saving | PASS. Closed the TextEdit test and Preview clipboard PDF using Delete (this macOS version’s discard button). Closed the evidence-image reference window opened for Preview binding, and the remaining blank TextEdit window. | [61-textedit-discard-dialog.png](61-textedit-discard-dialog.png), [62-preview-discard-dialog.png](62-preview-discard-dialog.png) |

Preview initially had no usable document window and its computer-use binding timed out repeatedly. Opening the existing evidence image `12-copy-white.png` in Preview supplied a window binding, after which New from Clipboard worked. That reference window was closed without editing. [49-preview-launch-timeout-screen.png](49-preview-launch-timeout-screen.png) records the diagnostic screen region. Unrelated preexisting crash dialogs visible there were left untouched and are not attributed to this build.

One immediate copy/paste batch produced no visible insertion (57); a separate paste after clipboard completion succeeded (58). This single timing observation was not isolated or reproduced, so it is not listed as a confirmed regression.

Clipboard after ReShiki Cmd+C with embedding OFF:

```text
«class CDIF», 1855, «class CHMS», 1855, «class PDF », 10091, «class PNGf», 24906, «class svg », 7795, «class AVIF», 6342, «class 8BPS», 59546, GIF picture, 3290, «class jp2 », 21589, JPEG picture, 12943, TIFF picture, 368982, «class BMP », 365690, «class TPIC», 22224
```

Clipboard after Preview’s default Cmd+A, Copy:

```text
«class rtfd», 485, «class HTML», 582, «class RTF », 394, «class utf8», 9, «class ut16», 20, string, 9, Unicode text, 18
```

Clipboard after Preview’s explicit rectangular picture selection, Copy:

```text
«class PDF », 9878, TIFF picture, 5192, «class AVIF», 4829, «class 8BPS», 6964, GIF picture, 945, «class jp2 », 4501, JPEG picture, 5310, «class PNGf», 4674, «class BMP », 5098, «class TPIC», 1007
```

Raw records: [clipboard-10-copy-editable-off.txt](clipboard-10-copy-editable-off.txt), [clipboard-10-preview-command-a-copy.txt](clipboard-10-preview-command-a-copy.txt), [clipboard-10-preview-region-copy.txt](clipboard-10-preview-region-copy.txt).

The four-character clipboard labels do not establish full pasteboard identifiers or prove that every public representation lacks embedded chemistry. The UI evidence establishes external picture appearance, one public-picture return as a Picture object, and editable native paste. CDIF/CHMS remained advertised while embedding was OFF; their contents were not inspected.

## 11. Quit ReShiki — PASS

**Expected:** Cmd+Q quits the wrapped app; discard if requested; do not query it after quitting.

**Observed:** Sent Cmd+Q after restoration and undo. The ReShiki window disappeared. No target-build save/discard prompt was visible afterward. A screen-region capture shows the underlying windows; the same unrelated crash dialogs already visible in screenshot 49 remained. No ReShiki API, accessibility, process, or application query was made after Cmd+Q.

**Evidence:** [63-final-restored-before-quit.png](63-final-restored-before-quit.png), [64-after-command-q.png](64-after-command-q.png).

Final requested preferences before quitting: Interface Match canvas; Copy 300 dpi; Export 1200 dpi; editable embedding ON. Both background defaults remain Custom `#1F4E79`; saved colors are `#27762F` and `#1F4E79`. PNG was selected in the Export format control during verification. No sample or drawing file was saved.

## Bugs

1. **B1 — Background search removes the copy destination heading.** Reproduce: open Settings and search `background`. The first background selector remains, but its “Copied pictures” heading disappears while “Exported files” stays above the second selector. Users can change the wrong destination because the two controls look identical. Smallest fix: retain each destination heading whenever a child setting matches. Evidence: [08-search-background.png](08-search-background.png), compared with [03-copy-export.png](03-copy-export.png). Severity: low UI labeling defect.
2. **B2 — Export’s Include editable drawing checkbox is absent from native accessibility output.** The checkbox is visible and mouse-operable, and its preference syncs, but the full saved AX snapshot lists the background controls, Settings link, Export button, and Copy image without exposing this checkbox or its checked state. The control was not discoverable or addressable through the captured accessibility interface, although that interface exposes the Settings switch. Smallest fix: expose a named checkbox/toggle with its current value in Export. Evidence: [63-final-restored-before-quit.png](63-final-restored-before-quit.png), [ax-export-final.txt](ax-export-final.txt). Severity: accessibility defect; VoiceOver itself was not tested.
3. **B3 — Copy success text conflicts with embedding OFF.** With both preference controls off, Cmd+C reports “Editable drawing and images copied.” The private native copy behavior may be intentional, but this status makes it look as if the user’s picture-embedding choice was ignored. Smallest fix: say “Copied” or “Drawing copied” and leave embedding scope in the preference help. Evidence: [48-editable-off-export-sync-copy.png](48-editable-off-export-sync-copy.png). Severity: low wording defect; not a demonstrated data-leak or clipboard-payload defect.

No confirmed crash, broken Settings close path, loss of focus, resolution-sync failure, or saved-color failure was observed in the target build.

## UX friction

| Evidence | What happens | Why it matters | Smallest improvement |
|---|---|---|---|
| [01-settings-open.png](01-settings-open.png) | Footer says changes “apply to every drawing,” while Canvas for new drawings says existing drawings keep their own canvas. | Scope sounds contradictory when changing a default. | Use “Changes save automatically. Esc closes.” Keep scope beside each setting. |
| [03-copy-export.png](03-copy-export.png), [08-search-background.png](08-search-background.png) | Your colors uses a five-line explanation followed by an isolated `+`. | The primary add-color action is less discoverable than its supporting prose; resolution is pushed below the initial viewport. | Label the action “Add color,” shorten the shared-Custom explanation, and move ink-conversion details to secondary help. |
| [07-search-resolution.png](07-search-resolution.png), [09-search-empty.png](09-search-empty.png) | A populated search has no visible clear button. Nonsense disables all section links. | Returning to category browsing takes text selection/deletion. | Add an accessible Clear search `×` in the field or a clear action in the empty state. |
| [05-assistant.png](05-assistant.png) | Model and Reasoning say to connect the assistant but provide no visible connection action on this page. | The prerequisite is described without a route to complete it. | Add one “Connect assistant” button or direct link to the connection UI. |
| [15-color-picker.png](15-color-picker.png), [18-color-picker-second.png](18-color-picker-second.png) | The color picker opens downward beyond the Settings modal and covers the footer/status area. It stays inside the app window. | The nested layer feels detached and conceals the Settings close guidance. | Flip it above the `+` when opening below would cross the modal boundary. |
| [30-dark-copy-export.png](30-dark-copy-export.png), [31-dark-resolution.png](31-dark-resolution.png) | Card borders and separators are much harder to distinguish in dark mode than light. | The long section loses some visual grouping. This is a subjective hierarchy concern, not a measured contrast failure. | Slightly lighten dark borders/separators. |
| [20-saved-blue-copy-export-custom.png](20-saved-blue-copy-export-custom.png), [31-dark-resolution.png](31-dark-resolution.png) | Blue Custom is selected for both destinations, but close-ups remain black on white and carry Copy/Export tags. | Users may assume these are final-output previews, although Preview later shows white ink on blue. | Label them “Resolution preview on white,” or apply each destination’s selected background. |
| [22-resolution-controls.png](22-resolution-controls.png), [46-editable-settings-before.png](46-editable-settings-before.png) | “Keep text editable in SVG files” has exceptions for copied SVG and SVG for Office in its helper. | The label is broader than the actual scope. | Rename it “Keep text editable in exported SVG” and retain the Office exception. |
| [37-export-tab.png](37-export-tab.png), [40-export-png.png](40-export-png.png) | Resolution is only revealed after changing the export format from PDF to PNG. | A user following instructions to find “Resolution” may initially believe it is missing. The conditional control is reasonable, but discovery takes an extra step. | Add brief format-aware guidance near the format selector, such as “Choose PNG to set pixel resolution.” |
| [52-preview-select-all-copy.png](52-preview-select-all-copy.png), [53-preview-text-copy-back-to-reshiki.png](53-preview-text-copy-back-to-reshiki.png) | Preview defaults to PDF text selection, and Cmd+A copies atom-label text. ReShiki tries it as SMILES and shows a parser error. | The documented/manual picture round-trip sequence fails unless the tester knows Preview’s selection modes. | Amend the verification instructions to use rectangular picture selection. In product, consider a clearer paste message for non-chemical text, e.g. “Clipboard text is not a recognized drawing or SMILES.” |

Alignment and spacing were generally consistent in the simpler sections. No persistent input lag was apparent during normal Settings navigation; the only uncertain timing issue was the single immediate copy/paste batch described in step 10.

## Not verified / limits

- No separate `-o` output path was present in the supplied task text or invocation context. This report is saved at the explicitly provided fallback path, `real-app/report.md`; no second destination was guessed.
- The literal Preview Cmd+A sequence did not copy a picture. The corrected rectangular-selection test used a cropped region, so a whole-page picture round trip was not established by that test.
- Full pasteboard identifiers, embedded payloads, and the absence of chemistry from every public PDF/PNG/SVG representation were not inspected. Clipboard info lists types and byte sizes, not semantic contents. Copy image with embedding OFF was not separately exercised; the editable-off external tests used Cmd+C.
- Native copy/paste was tested back into the same ReShiki document, as requested in step 10. A second ReShiki window/process was not opened, so cross-window transfer was not independently verified.
- The White context-menu copy was selected and reported successful, and its clipboard types were recorded. Its visual White background was not opened separately before the next copy replaced it.
- RGB and OKLCH parsing, invalid-color validation, saved-color removal, file exports, SVG text-editability output, new-canvas behavior, and persistence across an app restart were outside the executed steps. The hex input and palette path were verified.
- The one immediate copy/paste no-op was not reproduced or diagnosed; it may involve asynchronous clipboard completion or automation timing.
- No update check or assistant connection was attempted, per constraints. No quantitative contrast audit, VoiceOver session, or performance benchmark was run.
- The unrelated `ReShiki-w1b-base quit unexpectedly` dialog visible in desktop-region captures predated the target app’s quit and was left untouched. It is not evidence of a target-build crash.

## Claude review of this evidence (2026-11-15)

Checked against the screenshots and the branch source at 82f356933d1f:

- B1 is **not reproduced by the evidence**: [08-search-background.png](08-search-background.png) shows the "Copied pictures" heading above the first selector. Rejected.
- B2 is real but **pre-existing**: the Export tab's "Include editable drawing" is a plain iced checkbox on main too (src/app/inspector.rs:2258 on the branch). Recorded as an accessibility observation, not a branch regression.
- B3 is **by design, reclassified as UX**: with the switch off, Copy still writes the ChemDraw exchange data (src/clipboard.rs:510-513 sets `external_editable`), so src/app/clipboard.rs:506-507 reports "Editable drawing and images copied". Only the pictures lose the drawing, which matches docs/clipboard.md. The wording is recorded as a UX observation.
- Step 10's Preview Cmd+A failure is a test-path issue (Preview selected PDF text), not a product failure; the rectangular-selection round trip ([56-preview-picture-paste-back.png](56-preview-picture-paste-back.png)) pastes back as a Picture as documented.
- Privacy redaction: 49-preview-launch-timeout-screen.png was a desktop capture; everything except the menu-bar app name is blacked out. 64-after-command-q.png (desktop capture with unrelated windows) was removed from this folder. Hashes in evidence-manifest.json no longer match those two files.

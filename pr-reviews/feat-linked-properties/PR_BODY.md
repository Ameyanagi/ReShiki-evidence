## Summary

ReShiki can now show a molecule's properties as text under it that stays up to date: Formula, Mol. Wt., Exact Mass, cLogP, TPSA and elemental analysis. Right-click a molecule and choose **Show properties ›**, or click the pin beside a row in **Molecular properties**. Every structure edit recalculates the caption in the same Undo step. Editing the caption text makes it ordinary text, and deleting the molecule deletes the caption. CDXML and CDX keep the link as ChemDraw linked property text, so ChemDraw keeps updating it, and ChemDraw files with linked property text open in ReShiki with the link.

## Why it matters

Issue #1175 asks for ChemDraw's "paste chemical properties" feature (ChemDraw Analysis window › Paste; ChemSketch had the same thing). On main, the only related action is **Copy analysis** in the Properties panel.

A synthetic chemist writing up an experimental puts the molecular weight (and often the formula and exact mass for HRMS) under every compound in a scheme. When the structure changes (another protecting group, a different ester, a typo in the drawing), every number has to be found and retyped, and a stale MW under a corrected structure is an easy mistake to miss in an SI. ChemDraw users expect the numbers to follow the drawing. They also share CDXML files, so a ReShiki file opened in ChemDraw, or a ChemDraw file opened in ReShiki, has to keep the link and not turn into dead text. Before this change, ReShiki refused ChemDraw files containing this text altogether ("CDXML contains unsupported drawing objects or multiple pages").

## Approach

- **Reuse of the name-caption link.** ReShiki already links a chemical-name caption to its molecule (`molecule_names`): the caption is an ordinary annotation plus a list of atom ids, kept through copy/paste, templates, joining, generic expansion and deletion. Property captions use the same pattern (`crates/model/src/linked_properties.rs`, `PropertyCaption { annotation, atoms, properties, two_decimal_weight, text }`), and `molecule_names::is_caption` / `include_annotations` now cover both kinds. Because the caption is a normal annotation, every export (SVG, PNG, PDF, EMF, Office) prints it with no extra code, and styling it (font, size, color) keeps the link.
- **Recalculated inside the edit's transaction.** `linked_properties::reconcile` runs in `transaction::reconcile`, so the new text lands in the same Undo frame as the structure edit, and Undo restores the structure and the text together. Values come from the same code as the Properties panel, so the caption and the panel never disagree. The caption keeps its offset from the molecule's bottom center.
- **Unlink by editing, delete with the molecule.** The link stores the text it last wrote. When the annotation's text no longer matches, the user typed into it, so the link is dropped and the text stays as written (ChemDraw does the same). `Document::delete` prunes the caption with its structure.
- **ChemDraw object.** CDXML/CDX export writes ChemDraw's own `<chemicalproperty ChemicalPropertyDisplayID ChemicalPropertyIsActive="yes" ChemicalPropertyType="…" BasisObjects="fragment atoms bonds">` next to the caption. Import reads active links back from CDXML and CDX. The type codes (2 formula, 3 exact mass, 4 molecular weight, 6 elemental analysis) were taken from reference files made in ChemDraw 26.1 and checked by opening ReShiki's output in ChemDraw. The CDX schema gained object 0x8020 and its two properties, in the Rust schema and in the Python reference.
- **Document version 38** is written only when a drawing has a property caption; other drawings keep their older version.

Alternatives rejected:
- *A new "property text" drawing object* with its own rendering and export paths. The annotation-plus-link model already works for names, and a separate object would need its own handling in every exporter, selection and Undo path.
- *Recalculating at draw time* (a computed label). Exports and CDXML would not carry the text, and Undo would not cover it.
- *Static text from Copy analysis.* That is what main offers today, and the issue is precisely that it does not follow edits.
- *Writing cLogP/TPSA links to ChemDraw* with guessed type codes. ChemDraw's codes for them are not confirmed, so a caption that contains cLogP or TPSA is saved to CDXML/CDX as plain text instead of risking a link ChemDraw misreads.

## Evidence

All app captures: macOS arm64, debug builds, ReShiki window only (1280 x 852 pt at 2x). Before: `main` fcd2cde6 (binary `shasum` 1da9b92a…). After: `feat/linked-properties` 184416e5 (binary 97c63a38…). Input: `phenol.smi` (`Oc1ccccc1`) opened at launch. Driven by Codex computer use; every image checked by Claude. Light theme unless marked dark.

### Before: the Properties panel only offers Copy analysis

| Light | Dark |
| --- | --- |
| <img src="before-properties-panel.png" width="420"><br>main: phenol selected. **Molecular properties** lists the values and **Copy analysis**; nothing can be placed on the canvas. | <img src="before-properties-panel-dark.png" width="420"><br>main, dark: the same panel. |
| <img src="before-context-menu.png" width="420"><br>main: right-click on a bond. No **Show properties** item. | <img src="before-open-chemdraw-file.png" width="420"><br>main: opening a ChemDraw 26.1 file with linked property text is refused: "CDXML contains unsupported drawing objects or multiple pages." |

### After: pin Mol. Wt. and Exact Mass, then edit the structure

| | |
| --- | --- |
| <img src="after-01-panel-pins.png" width="420"><br>Phenol selected: a pin at the right of Formula, Weight, Exact mass, cLogP, TPSA and Elemental analysis. | <img src="after-02-pinned-phenol.png" width="420"><br>Weight and Exact mass pinned: the caption reads `Mol. Wt.: 94.113` / `Exact Mass: 94.0419`, centered under phenol. |
| <img src="after-03-methyl-added.png" width="420"><br>A methyl added para to OH (bond tool). The caption updates by itself to `Mol. Wt.: 108.140` / `Exact Mass: 108.0575` (p-cresol, C7H8O). | <img src="after-04-show-properties-menu.png" width="420"><br>Right-click › **Show properties ›**: ✓ on Mol. Wt. and Exact Mass. |
| <img src="after-05-formula-added.png" width="420"><br>Choosing **Formula** in that list adds `Formula: C7H8O` as the first line (panel order). | <img src="after-09-fourth-undo-phenol.png" width="420"><br>Undo: Formula is removed; one more Undo removes the methyl and puts the phenol values back in the same step. |

Dark theme:

| | |
| --- | --- |
| <img src="after-06-dark-caption.png" width="420"><br>Dark: three-line caption, white on the dark canvas; Formula, Weight and Exact mass pins inked. | <img src="after-07-dark-menu.png" width="420"><br>Dark: **Show properties ›** with ✓ on Formula, Mol. Wt. and Exact Mass. |

The theme button takes an Undo step of its own (that code is not changed here), so in the capture run the first two Undos after the dark shots only switched the theme back.

### After: editing the text makes it plain text; deleting the structure deletes the caption

| | |
| --- | --- |
| <img src="unlink-01-caption.png" width="420"><br>Linked caption on phenol. | <img src="unlink-02-text-edited.png" width="420"><br>Caption text edited: `Mol. Wt.` changed to `MW`. |
| <img src="unlink-03-plain-text-after-edit.png" width="420"><br>Methyl added: the panel shows C7H8O / 108.140, but the edited caption keeps `MW: 94.113` / `Exact Mass: 94.0419`. It is ordinary text now. | <img src="unlink-03-properties-submenu.png" width="420"><br>Show properties on the same molecule: no ✓ on any row. |
| <img src="unlink-04-back-to-linked.png" width="420"><br>Two Undos: methyl and text edit undone, caption linked again. | <img src="unlink-05-selection-before-delete.png" width="420"><br>A box around the ring and OH only: the selection takes the caption along (`7 atoms · 1 object · 7 bonds`), as it does for linked name captions. |
| <img src="unlink-05-structure-deleted.png" width="420"><br>Delete: the molecule and its caption are both gone. | <img src="unlink-06-undo-restores.png" width="420"><br>One Undo: phenol and the caption come back together. |
| <img src="unlink-07-restored-still-live.png" width="420"><br>The restored caption is still live: a methyl updates it to 108.140 / 108.0575. | <img src="unlink-08-dark.png" width="420"><br>Same state, dark theme. |

### ChemDraw round trip

**ChemDraw-made file opened in ReShiki.** `tests/fixtures/chemdraw-properties/phenol-props.cdxml` was made in ChemDraw 26.1 with Analysis window › Paste (Formula, Exact Mass, Molecular Weight, Elemental analysis).

| In ChemDraw 26.1 | Opened in ReShiki (after) |
| --- | --- |
| <img src="chemdraw-made-phenol-props.png" width="360"><br>The pasted linked text in ChemDraw (crop of the document window). | <img src="import-01-opened-chemdraw-file.png" width="420"><br>Opens with the link; ReShiki rewrites the lines in its own labels. On main this file is refused (above). |
| <img src="import-02-menu-ticks.png" width="420"><br>Show properties: ✓ on Formula, Mol. Wt., Exact Mass and Elemental analysis. | <img src="import-03-after-methyl.png" width="420"><br>A methyl added in ReShiki: all four lines update to C7H8O / 108.140 / 108.0575 / C, 77.75; H, 7.46. |
| | <img src="import-04-after-methyl-dark.png" width="420"><br>Same, dark theme. |

The strip at the bottom left ("2 drafts · Restore…") is the recovery offer from the earlier capture runs in the same throwaway data folder.

**ReShiki file edited in ChemDraw 26.1.** The CDXML exported above opens in ChemDraw without an alert, with the caption in place. A methyl added in ChemDraw makes ChemDraw recalculate the text itself, in its own words. The edit was captured on an earlier commit of this branch (7aee8e1c, a four-line caption); the CDXML writer for the caption has not changed since. A rerun on 184416e5 opened the file correctly, but the computer-use agent could not reach ChemDraw's bond tool, so that edit is not shown.

| ChemDraw: 184416e5 export opened | ChemDraw: 7aee8e1c export opened | ChemDraw: after adding a methyl in ChemDraw |
| --- | --- | --- |
| <img src="chemdraw-01-opened-reshiki-file.png" width="300"><br>`Mol. Wt.: 94.113` / `Exact Mass: 94.0419` as written by ReShiki. | <img src="chemdraw-earlier-01-opened.png" width="300"><br>Four lines as written by ReShiki. | <img src="chemdraw-earlier-02-after-methyl.png" width="300"><br>ChemDraw rewrote them: `Chemical formula: C7H8O`, `Exact mass: 108.06`, `Molecular weight: 108.14`, `Elemental analysis: C, 77.75; H, 7.46; O, 14.79`. |

**Headless round trip.** The same ChemDraw file through `reshiki --cli convert … -o roundtrip.cdxml` ([`base-roundtrip.txt`](base-roundtrip.txt), [`head-roundtrip.txt`](head-roundtrip.txt)):

```text
main fcd2cde6:  reshiki: error[failed]: CDXML contains unsupported drawing objects or multiple pages.   (exit 1)

branch:         exit 0
<chemicalproperty id="19" ChemicalPropertyDisplayID="18" ChemicalPropertyIsActive="yes"
  ChemicalPropertyType="2 4 3 6" BasisObjects="2 3 4 5 6 7 8 9 10 11 12 13 14 15 16" />
Formula: C6H6O
Mol. Wt.: 94.11
Exact Mass: 94.0419
Anal. Calcd for C6H6O: C, 76.57; H, 6.43
```

The CDXML the app wrote for the pinned phenol ([`reshiki-phenol-props.cdxml`](reshiki-phenol-props.cdxml), Export › Structure & exchange › CDXML) holds `<chemicalproperty … ChemicalPropertyIsActive="yes" ChemicalPropertyType="4 3" …>`.

## Verification

VERIFICATION_TABLE

## Risk

- **Document version 38.** A drawing with a property caption is saved as version 38, so older ReShiki builds refuse to open it. Drawings without one keep their old version.
- **Wide reach in the model.** The link has to follow atoms through copy/paste, templates, joining, atom merge, share-atom, generic certify/expansion and deletion (67 files, about 3,000 lines including tests and fixtures). An independent adversarial review found five places where a caption went stale or failed validation (atom merge, share-atom, CDXML import before generic labels were restored, component expansion, whole-drawing expansion); each was fixed, most with a test. Another path that rebuilds atoms could still miss the link; the failure mode is a stale or dropped caption, not lost structure.
- **ChemDraw labels.** ReShiki writes its own short labels (`Mol. Wt.:`); after an edit in ChemDraw, ChemDraw rewrites the lines in its words (`Molecular weight:`). On import ReShiki rewrites ChemDraw's lines in its labels, and its elemental analysis lists C, H, N and S as the Properties panel does, so ChemDraw's `O, 17.00` is not kept.
- **What stays plain text.** A caption containing cLogP or TPSA is saved to CDXML/CDX as plain text, because ChemDraw's codes for them are unconfirmed. ChemDraw text linked to more than one molecule (both ions of a salt) opens as plain text. SVG, PNG, PDF, EMF and Office exports always carry plain text.
- **Behaviour choices to review.** Clicking the **Show properties** row itself shows Mol. Wt. when nothing is shown (the reading of "default Mol. Wt."). A box around the molecule also selects its caption, as with name captions, so moving or deleting the molecule takes the caption along. Mol. Wt. follows **View › 2-decimal MW**; switching it rewrites every caption in one Undo step.

## Changelog

`docs/changes/unreleased/linked-property-captions.md` (section Changes):

- **Properties under a molecule.** Right-click a molecule and choose **Show properties**, or click the pin beside a row in **Molecular properties**. The caption shows Formula, Mol. Wt., Exact Mass, cLogP, TPSA or elemental analysis, one line each, and updates with every edit in the same Undo step. Editing its text makes it ordinary text; deleting the molecule deletes it.
- CDXML and CDX save the caption as ChemDraw linked property text, and ChemDraw files with linked property text open with the link. A caption with cLogP or TPSA is saved as plain text, and so is ChemDraw text over more than one molecule when it opens. ChemDraw files that contain linked property text used to be refused. `.rsk` files with these captions use document version 38.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

Fixes #1175

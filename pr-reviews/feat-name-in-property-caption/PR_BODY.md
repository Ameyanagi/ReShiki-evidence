## Summary

A molecule's name can now be the first line of its property caption, in bold, with Mol. Wt., Exact Mass or the other properties below it in the same caption. **Show properties ›** has a **Name** row at the top, followed by a separator, and **Show chemical name** shows the same row. The name is the automatic (IUPAC) name, or a custom name such as `Compound 3a`, typed in the new **Name** field at the top of **Molecular properties** or by double-clicking the name on the canvas. Both edit one stored name, and the caption stays linked. ↺, or clearing the field, returns to the automatic name.

When the structure changes, an automatic name follows it in the same Undo step as the edit, like the properties. A custom name stays, and the panel notes "Structure changed since you named it."

## Why it matters

The owner approved this design on 2026-11-18 ([mock](https://claude.ai/artifact/VrtntECjiBxDb4Sdn9Bnuh)). On main, the name (**Show chemical name**) and the properties (#1197) are two separate captions under the molecule. They are placed independently, so they overlap (below), and they cannot be laid out as one compound heading for an SI. The name caption is also removed whenever the structure changes, and there is no way to give a molecule your own label (`Compound 3a`, `Aspirin`) that moves with it.

## Approach

- **One more caption row.** `Property::Name` is the first row of `linked_properties::PropertyCaption`, so the name uses the property caption's link: it moves with the molecule, follows copy/paste, templates and deletion, and every export prints it as ordinary text. `PropertyCaption` gains `smiles` (the molecule's identity), `name` (the automatic name), `custom_name` and `custom_smiles` (the identity when the custom name was typed, for the note). A new name line starts bold; editing keeps whatever style the user gives it.
- **Automatic names are generated outside the transaction.** The local name generator runs in a worker process (or the browser worker), so it cannot run inside `transaction::reconcile`. Instead, reconcile re-identifies a named molecule whenever its chemistry changes, or its shape changes (stereo read from 2D coordinates), and clears the automatic name; the line shows `–` meanwhile. After every update, the app asks the generator for one caption still waiting (`start_caption_names`), and writes the answer into the drawing as it stands with `linked_properties::named`, **without an Undo step of its own** and without a new revision. Undo therefore goes straight back to the drawing before the edit, with its old name. Answers are matched by identity, so a name never lands on a structure that changed meanwhile; names are cached per tab, so Undo and Redo do not ask again. A structure the generator refuses shows `–`, the status bar says why, and showing the name again retries.
- **One stored name, two ways to type it.** The panel's **Name** field and the canvas both set `custom_name`. Double-clicking a caption whose first row is the name opens the text editor with the name line selected. When a caption's text changes only in its first line (the property lines below are as written), reconcile reads that line as the new name and keeps the link; changing a property line still makes the caption plain text, as before. Typing the automatic name, or clearing it, returns to automatic. Typing a name for a molecule without a caption adds one with the name row.
- **Show chemical name.** For one molecule it now toggles the **Name** row (the same as **Show properties › Name**), so a name is shown one way and the old overlap cannot happen. A salt's ions are separate molecules, so for a charge-balanced salt it still places the separate name caption, and name captions in older drawings still hide on their own.
- **ChemDraw: the name line is plain text, the properties stay linked.** ChemDraw's CDX documentation in the repository lists a chemical-name type (`reference/engine/cdx_schema.py`, generated from the CDX SDK's property table: `ChemicalPropertyType … {"Unspecified": 0, "ChemicalName": 1}`), so the first build linked it as type 1. Checked in ChemDraw 26 (below), that does not work: with types `1 4 3`, deleting a methyl left every line stale, while the same file with `4 3` had its lines rewritten. A name type stops ChemDraw from updating the whole linked text. So CDXML/CDX export writes the name line as its own plain text object, bold, just above the property lines, and links only the property lines (types 2, 3, 4, 6 as in #1197). This matches the owner's pick ("Properties stay linked; the name line is saved as plain text"). Reading the file back gives the name as ordinary text above a linked property caption; `.rsk` keeps the whole caption linked.
- **Document version 39** is written only when a caption has a name row or a custom name; other drawings keep their version.

Alternatives rejected:
- *Keep the name as a separate caption stacked above the properties* (the mock's second option): two objects to keep aligned, and the overlap seen on main.
- *Wait for the name before committing the edit*, to get a true single transaction: every structure edit would block on a worker process, and naming can be unavailable.
- *Generate the name while drawing* (a computed label): exports, CDXML and Undo would not carry it.

## Evidence

All captures: macOS arm64, debug builds, ReShiki window only (2560 x 1704 px). Input: `aspirin.smi` (`CC(=O)Oc1ccccc1C(=O)O`) opened at launch, fresh data folder, naming helper pointed at the build. Before: `main` 0d97885c (binary `shasum` c0071e45…). After: this branch at 09dc6c52 (binary 5303c665…), which is 316f024e after the rebase onto main b9bdcaf7. Driven by Codex computer use; every image checked by Claude against the mock.

### Before (main)

| Light | Dark |
| --- | --- |
| <img src="before/before-01-show-properties-menu.png" width="420"><br>**Show properties ›** has no Name row. | <img src="before/before-04-menu-dark.png" width="420"><br>The same, dark. |
| <img src="before/before-02-molecular-properties.png" width="420"><br>Molecular properties starts with Formula; there is no Name field. | <img src="before/before-05-molecular-properties-dark.png" width="420"><br>The same, dark. |
| <img src="before/before-03-name-and-weight-separate.png" width="420"><br>**Show chemical name**, then **Show properties › Mol. Wt.**: two separate captions, placed on top of each other. | |

### After (this branch)

| | |
| --- | --- |
| <img src="after/after-01-show-properties-menu.png" width="420"><br>**Show properties ›**: **Name** at the top, a separator, then the values. | <img src="after/after-02-caption-name-weight-mass.png" width="420"><br>Name, Mol. Wt. and Exact Mass chosen: one caption, the IUPAC name `2-(acetyloxy)benzoic acid` in bold, the values in regular text. |
| <img src="after/after-03-panel-name-automatic.png" width="420"><br>Molecular properties: the **Name** field at the top shows the automatic name as its placeholder; ↺ is disabled, the pin is on. | <img src="after/after-04-panel-name-custom.png" width="420"><br>`Aspirin (3a)` typed in the field, then Return: the caption's first line follows; "Custom name · automatic: …". |
| <img src="after/after-05-inline-edit-open.png" width="420"><br>Double-click on the name: the text editor opens with the name line selected. | <img src="after/after-06-inline-edit-applied.png" width="420"><br>`Compound 3a` typed and applied: still linked, still bold; the panel field shows the same name. |
| <img src="after/after-07-structure-edited-custom-kept.png" width="420"><br>A methyl added: the values update (194.186 / 194.0579), the custom name stays, and the panel says "Structure changed since you named it." | <img src="after/after-08-automatic-after-edit.png" width="420"><br>↺: back to the automatic name, now `2-(acetyloxy)-4-methylbenzoic acid`; the note is gone. |
| <img src="after/after-09-undo.png" width="420"><br>One Undo: `Compound 3a` again, with the note. | <img src="after/after-10-caption-panel-dark.png" width="420"><br>Dark theme. |
| <img src="after/after-11-menu-dark.png" width="420"><br>Dark: **Hide chemical name** (no tick) and ✓ on Name, Mol. Wt. and Exact Mass. The submenu separator is a gap, as the other menu separators are in dark. | |

The GUI captures are from 09dc6c52, now 316f024e (binary 5303c665…); the commits after it change only CDXML/CDX export, test goldens and docs.

### ChemDraw 26

The drawings saved in the run above: [`name-caption-auto.rsk`](name-caption-auto.rsk) (automatic name) and [`name-caption-custom.rsk`](name-caption-custom.rsk) (`Compound 3a`, version 39). Converted with the head build ([`cdxml-output.txt`](cdxml-output.txt); the file opened in ChemDraw below is byte-identical to the head's output): the name is a text object of its own, and the property lines are linked with `ChemicalPropertyType="4 3"`. The main build refuses the version 39 file ([`base-open-v39.txt`](base-open-v39.txt)).

| Head export opened in ChemDraw | After deleting the ring methyl in ChemDraw |
| --- | --- |
| <img src="chemdraw/chemdraw-01-opened.png" width="300"><br>[`name-caption-auto.cdxml`](name-caption-auto.cdxml) opens without an alert. | <img src="chemdraw/chemdraw-02-after-edit.png" width="300"><br>ChemDraw rewrites the linked lines for aspirin in its own words (`Exact mass: 180.04`, `Molecular weight: 180.16`) and moves them; the name stays as written, since it is plain text. |

Why the name is not linked. The same file with the documented name type included ([`ab-B-types-1-4-3.cdxml`](chemdraw/ab-B-types-1-4-3.cdxml)) and without it ([`ab-A-types-4-3.cdxml`](chemdraw/ab-A-types-4-3.cdxml)), after the same edit:

| `ChemicalPropertyType="4 3"` | `ChemicalPropertyType="1 4 3"` |
| --- | --- |
| <img src="chemdraw/ab-A-after-edit.png" width="300"><br>Rewritten. | <img src="chemdraw/ab-B-after-edit.png" width="300"><br>Nothing is updated: the methylated name, 194.186 and 194.0579 stay. |


### Tests

- `crates/model/src/linked_properties/tests.rs`: name first and bold; a custom name from the API and from typing over the name line is one value; line breaks and clearing; ↺ and typing the automatic name; a property-line edit still unlinks; a structure edit clears an automatic name and keeps a custom one with the note, and Undo restores both; a move keeps the name; dragging a double bond's end (E to Z) renames it and clears the caption line at once; a generated name fills only waiting captions; hiding the row forgets the name; typing over a bold name keeps it bold (failing first, from the GUI run); `.rsk` round trip and version 38/39.
- `src/app/linked_properties/tests.rs`: the generated name arrives with no extra Undo step and no new revision; Undo/Redo reuse it; a refused structure is not asked again until the row is shown again; the Name field (draft until Return) and the canvas double-click set one name, with bold kept; ↺; a custom name survives a structure edit with the note.
- `src/app/context_menu/tests.rs`: **Show properties ›** lists Name, a separator, then the values, with ticks; **Show chemical name** toggles the Name row and Undo restores; only Show properties rows carry ticks; old name captions still hide.
- `crates/io/src/chemistry/cdxml/properties_tests.rs`: with an automatic or a custom name, CDXML and CDX link only the property line (`ChemicalPropertyType="4"`), and the name comes back as bold text of its own above it; a name alone is plain text.
- `src/app/atom_text/presentation_tests.rs`: this real-renderer test compares the label dialog's area before and after a click, and the click also changed the Properties panel, which now reaches into that area. It keeps the panel closed.

## Verification

VERIFICATION_TABLE

## Risk

- **Asynchronous name.** The automatic name is written into the current drawing without an Undo step, after the edit. Between the edit and the answer (typically well under a second) the line shows `–`; exporting in that moment exports `–`. Undo snapshots taken in that window also hold `–`, and are named again (from the cache) when restored.
- **Name typography.** The name line is bold, with no italic locants or stereodescriptors (the **Chemical name typography** setting applies to the separate name captions only). **Format as chemical name** on the selected caption still works, and keeps the link.
- **ChemDraw round trip.** A CDXML/CDX file keeps the name as plain text, so after a structure edit in ChemDraw the name does not change there, and reopening the file in ReShiki gives a plain name text and a linked property caption (no Name row). The text positions in a CDXML written by the command line use estimated text widths, as before; the name and the property lines share one center.
- **Clearing a name-only caption on the canvas** deletes the caption, as deleting all of any text box does; the panel field's ↺ (or an empty field) returns to the automatic name instead.
- **Document version 39.** A drawing that uses names cannot be opened by older builds; other drawings are unaffected.

## Changelog

`docs/changes/unreleased/feat-name-in-property-caption.md` (section Changes):

- **The name above the properties.** **Show properties** has a **Name** row, and **Show chemical name** now shows the same row: the molecule's name in bold, with Mol. Wt., Exact Mass or the other properties below it in one caption. The automatic name follows structure edits in the same Undo step.
- **Your own name.** Type a name such as `Compound 3a` in the new **Name** field of **Molecular properties**, or double-click the name on the canvas. ↺ returns to the automatic name. A custom name stays when the structure changes, and the panel notes that it changed.
- CDXML and CDX save an automatic name as ChemDraw chemical-name text, linked like the properties; a caption with a custom name is saved as plain text. `.rsk` files with a name line use document version 39.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

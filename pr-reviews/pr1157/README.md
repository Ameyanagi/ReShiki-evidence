# Text flavors for Copy and Copy Image (PR 1157), 2026-11-12

Question: can ReShiki's Copy (and Copy Image) carry a plain-text SMILES flavor, so text-only
targets stop getting nothing, without changing what rich apps paste? Answer: no, on macOS and
Windows; on Linux the tested apps were unchanged. Input: the caffeine drawing with a caption.
SMILES used: `Cn1c(=O)c2c(ncn2C)n(C)c1=O`, byte-identical to ReShiki's own Copy SMILES output
(`macos/copy-smiles-notes/pasteboard.txt`).

Method: the real Copy / Copy Image clipboard contents were captured and re-published with and
without the text flavor, then pasted into each app.

- `macos/`: macOS 27.0.1 arm64. Pasteboard bytes from a ReShiki 0.14.0 Copy and Copy Image
  (main 11df00d5; the macOS clipboard code is unchanged on fb508e23), re-published by
  `tools/pbwrite.swift`: C0 = Copy, C1 = Copy + `public.utf8-plain-text` in the same item,
  C2 = Copy + the text as a second item, I0 = Copy Image. Pasted by hand (computer use) into
  Word, PowerPoint, Excel 16.115, TextEdit (rich and plain), Notes (Google account; no iCloud
  account on the machine), ChemDraw 26.1 and ReShiki: `paste-matrix/report.md` and screenshots.
  Chrome 157 paste events: `chrome/` (DevTools paste into a contenteditable page).
  `copy-smiles-notes/`: ReShiki's own Copy SMILES (Cmd+Option+C) pasted into a Google-account note.
- `windows/`: Windows 11 x64 25H2, Microsoft 365, Edge 157, Paint 11.2609. The Copy came from
  ReShiki's real `clipboard::copy` (main with #1148), re-published with `CF_UNICODETEXT`
  (`tools/republish.ps1`, from issue 1146's tools, plus a `CF_UNICODETEXT` case). Word and Excel
  pastes through COM, Edge through DevTools (contenteditable and `tools/probe-textarea.html`).
  PowerPoint was not driven: the test machine's PowerPoint was in use by another session.
  `desktop-copy-text-matrix.txt` (its Paint lines failed on a script bug; see the Paint files).
  `browser-copy-image-text-matrix.txt`: Edge wrote the browser editor's `ClipboardItem`
  (`tools/browser_write.mjs`) for Copy, Copy Image, and Copy Image + `text/plain`; then Word,
  Excel, Edge and desktop ReShiki's real paste path (`clip_paste`, 14 atoms = the SMILES molecule,
  0 atoms = the picture). `paint-*.txt` / `paint-*-copied-back.png`: Paint pasted through its
  Edit menu with UI Automation (the desktop is locked), then Edit > Copy; the bitmap Paint copied
  back is 1303 x 1390, the Copy bitmap. OneNote 16 opened only a sign-in dialog; classic Outlook
  has no mail profile.
- `linux/`: Arch Linux x64, X11 under Xvfb, LibreOffice 25.8.7, Chromium 149. The portable Copy
  and Copy Image representations, with and without `public.utf8-plain-text` (offered as
  `text/plain;charset=utf-8`, `text/plain`, `UTF8_STRING`), published through ReShiki's own X11
  clipboard worker (`tools/run.sh`, `tools/run-lo.sh`). LibreOffice under Xvfb crashed on some
  runs regardless of the payload (also without text); `libreoffice-run*.txt` hold the completed
  runs: Writer and Impress pasted the PDF picture for every payload.

Result summary (bold = the pick changed):

| App | Without text | With text (same item / second item) |
| --- | --- | --- |
| macOS Word | picture | picture / picture |
| macOS PowerPoint | picture | **text box** / **nothing** |
| macOS Excel | picture | **text in B2** / **text in B2** |
| macOS TextEdit rich | picture | picture / picture |
| macOS TextEdit plain | nothing | SMILES / SMILES |
| macOS Notes (Google) | nothing (Copy and Copy Image) | nothing / nothing |
| macOS ChemDraw, ReShiki | editable | editable / editable |
| macOS Chrome page | picture | picture |
| Windows Word, Copy / Copy Image | object / SVG graphic | object / SVG graphic |
| Windows Excel, Copy / Copy Image | object / SVG graphic | **text in B2** / **text in B2** |
| Windows Edge page | bitmap | bitmap |
| Windows Edge text box | nothing | SMILES |
| Linux Writer, Impress | PDF | PDF |
| Linux Chromium page / text box | picture / nothing | picture / SMILES |
| Browser Copy Image to Word, Excel, Edge page | picture | picture |
| Browser Copy Image to desktop ReShiki | picture | **molecule from SMILES** |

Copy SMILES into Notes (Google): the SMILES text.

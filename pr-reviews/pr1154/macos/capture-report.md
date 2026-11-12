ReShiki #462 evidence capture — 2026-11-12, macOS arm64, Retina

All six requested Part A screenshots were captured. The BEFORE build pasted a picture from Word and refused PDF/SVG import. The AFTER build restored editable caffeine through all three routes. In Part B, Word, PowerPoint, and Excel round trips restored the editable drawing; TextEdit returned rich text that ReShiki rejected as invalid SMILES. Preview could not be operated through the available computer-use binding, and Chrome's local probe remained empty before further tab access was blocked. Those two routes are incomplete, not evidence of payload loss.

All paths below are relative to this artifact directory. Clipboard evidence was collected with the supplied `survival/pbdump.swift`, restored with the supplied `survival/pbwrite.swift`, and checked with `python3 -I survival/haspayload.py`. A successful payload check throughout this report means `payload=v1 json=4859B env=628B hash=ok atoms=14 bonds=15`. `payload=none` means the supplied detector found no supported payload in that file; it is not an exhaustive decoding of every possible nested container.

The actual wrapper/build provenance was:

| Run | Wrapper launched with `open -n` | Executable referenced by wrapper | PID / captured window ID |
|---|---|---|---|
| Part A BEFORE | `../../apps/ReShiki-462png-d670ed7a.app` | `../../bin462/reshiki-png-d670ed7a` | 77707 / 66877 |
| Part A AFTER, final evidence | `../../apps/ReShiki-462vector-7d45486c.app` | `../../bin462/reshiki-vector-7d45486c` | 96093 / 67102 |
| Part B AFTER | `../../apps/ReShiki-462vector-7d45486c.app` | `../../bin462/reshiki-vector-7d45486c` | 7953 / 67250 |

An earlier AFTER attempt (PID 85693) was quit after a computer-use connection/window-targeting problem. Part A was repeated in a fresh AFTER wrapper instance; the final `after-*` captures come from PID 96093. The current task's specified AFTER build and the wrapper executable both identify **7d45486c**. The pre-existing `prompt-tail.md` mentions a different commit and was not used as build provenance.

ReShiki was launched only through the supplied wrapper paths. Each wrapper supplied its own temporary `RESHIKI_DATA_DIR`. Windows were identified from the wrapper PID and Quartz window list, and positioned/resized using the native Accessibility API from that PID. No ReShiki app-name or bundle-ID launch was used. Each instance received Cmd+Q before the next was launched, and no instance was queried after quitting. No repository files were edited and the supplied `caffeine.rsk` was not saved over.

All ReShiki evidence windows measured **1400 × 900 points at (0, 30)** on the main display. macOS constrained the top edge to y=30 beneath the menu bar. Captures used `screencapture -x -o -l <window-id>` and are **2800 × 1800 pixels**, including title bar and status bar, with no rescaling or image edits. Both builds used the same input, 250% zoom, JACS / ACS style, Publication mode, and Arial 10 pt. The final images have different canvas centering/object placement between builds; no manual repositioning was applied to force pixel alignment. The selected pasted object also differs by design: a picture in BEFORE, atoms and bonds in AFTER.

Part A was performed in this order for each build:

1. Launch the wrapper. Because its file argument left an Untitled document, open `caffeine.rsk` through Cmd+O → Cmd+Shift+G → full input path → Open.
2. Cmd+A, Cmd+Shift+C; create a new blank Word document, Cmd+V; select the pasted picture and Cmd+C. Return to ReShiki, click the same empty canvas location, and Cmd+V. Capture the status, dump Word's returned clipboard, and check PNG/PDF/SVG/TIFF representations. Close the temporary Word document without saving. Undo the ReShiki paste before exporting the original drawing.
3. Export SVG through the Export inspector. In AFTER, enable **Include editable drawing**; this choice remained enabled when switching to PDF. Save both files in this directory.
4. Import → Choose file… → the exported PDF; capture. Undo the inserted drawing. Repeat for SVG and capture. The BEFORE refusals did not insert anything.
5. Check drawing focus after closing the inspector, undo any inserted test drawing, and quit with Cmd+Q.

| Step / build | Expected | Observed status and object | Screenshot / supporting evidence |
|---|---|---|---|
| Word copyback, BEFORE d670ed7a; Word 16.115 | Picture pasted | `Picture pasted · Drag the corner handles to resize`. Properties identifies a 160 × 134 pixel picture. | [before-01-word-roundtrip.png](before-01-word-roundtrip.png); [before-word-copyback.txt](before-word-copyback.txt) |
| Word copyback, AFTER 7d45486c; Word 16.115 | Editable drawing restored | `Editable drawing pasted · Restored the editable drawing from the picture · Paste picture inserts the image instead`. Selection is 14 atoms / 15 bonds. | [after-01-word-roundtrip.png](after-01-word-roundtrip.png); [after-word-copyback.txt](after-word-copyback.txt) |
| PDF insertion, BEFORE d670ed7a | Refusal | `Can't import .pdf`; original caffeine remains. | [before-02-insert-pdf.png](before-02-insert-pdf.png) |
| PDF insertion, AFTER 7d45486c | Editable drawing restored | `Inserted after-caffeine.pdf · Drag to position · Delete or Undo to remove · Restored the editable drawing from after-caffeine.pdf`. | [after-02-insert-pdf.png](after-02-insert-pdf.png) |
| SVG insertion, BEFORE d670ed7a | Refusal | `Can't import .svg`; original caffeine remains. | [before-03-insert-svg.png](before-03-insert-svg.png) |
| SVG insertion, AFTER 7d45486c | Editable drawing restored | `Inserted after-caffeine.svg · Drag to position · Delete or Undo to remove · Restored the editable drawing from after-caffeine.svg`. | [after-03-insert-svg.png](after-03-insert-svg.png) |

Word's Part A returned flavor set is the Word set listed below. BEFORE's PNG, PDF, TIFF, and Microsoft SVG representations all checked as `payload=none`; the Microsoft SVG entry was empty. AFTER's PDF contained a valid drawing; PNG, TIFF, and Microsoft SVG did not. The PDF returned by AFTER Word is byte-identical to the canonical Part B source PDF.

| ReShiki file route | Build | Saved file | Detector result | Import outcome |
|---|---|---|---|---|
| Export SVG → Import | d670ed7a | [before-caffeine.svg](before-caffeine.svg), 4,857 B | None | Refused `.svg` |
| Export PDF → Import | d670ed7a | [before-caffeine.pdf](before-caffeine.pdf), 10,141 B | None | Refused `.pdf` |
| Export SVG with editable drawing → Import | 7d45486c | [after-caffeine.svg](after-caffeine.svg), 5,803 B | Valid, 14 atoms / 15 bonds | Restored |
| Export PDF with editable drawing → Import | 7d45486c | [after-caffeine.pdf](after-caffeine.pdf), 11,641 B | Valid, 14 atoms / 15 bonds | Restored |

File detector output is in [export-payloads.txt](export-payloads.txt).

The focus checks produced a useful distinction. In BEFORE, closing the focused Import inspector and pressing Right reached the drawing and reported `No drawing hotspot in that direction`. In AFTER, Cmd+Z while the Import text field still had focus did not undo the PDF insertion. After closing the inspector, Cmd+Z removed the inserted drawing: the modified marker disappeared and Undo became disabled. The inspector was reopened for the SVG test; closing it and pressing Cmd+Z again removed that insertion. Thus keyboard focus returned to the drawing after inspector closure. These checks were observed through the live UI; there are no separate focus-check image files.

For Part B, a fresh AFTER instance opened the same caffeine input, then Cmd+A / Cmd+Shift+C produced the canonical clipboard. Its seven representations were dumped to `00-reshiki-copy-image/`, and copied without byte changes into `00-reshiki-copy-image-ordered/` with `00-` through `06-` prefixes in the printed order. Each tested app received this exact clipboard restored with `pbwrite.swift` before paste. The canonical source checks are in [00-reshiki-copy-image.txt](00-reshiki-copy-image.txt).

| Canonical flavor, in original order | Bytes | Payload check |
|---|---:|---|
| `com.adobe.pdf` | 11,605 | Valid, 14 atoms / 15 bonds |
| `com.revvity.chemdraw.cdx-clipboard` | 73,321 | Not part of the requested source payload check |
| `com.perkinelmer.chemdraw.cdx-clipboard` | 73,321 | Not part of the requested source payload check |
| `com.cambridgesoft.cdx` | 73,321 | Not part of the requested source payload check |
| `public.png` | 73,225 | Valid, 14 atoms / 15 bonds |
| `public.svg-image` | 5,702 | Valid, 14 atoms / 15 bonds |
| `dev.reshiki.drawing` | 4,859 | Native drawing JSON; not a picture payload check |

For each completed clipboard route, a new app document received Cmd+V. Its picture/attachment was selected and copied, every returned clipboard representation was dumped and checked, then ReShiki received Cmd+V after an empty-canvas click. The ReShiki result was captured and undone. Temporary app documents were closed without saving. PowerPoint was usable; no activation or read-only blocker appeared. Its slide layout was changed to Blank to remove the initial title placeholders; Design Suggestions opened automatically but no suggested design was applied.

The exact successful ReShiki clipboard status below, abbreviated **restored status**, is: `Editable drawing pasted · Restored the editable drawing from the picture · Paste picture inserts the image instead`.

| App / version | Route and visible paste | Returned clipboard types | Payload found | ReShiki outcome | Images / log |
|---|---|---|---|---|---|
| Microsoft Word 16.115 (16.115.26110837) | New blank document; inline caffeine picture, identified as Picture 1. UI does not identify its encoded source type. | Word flavor set below | `com.adobe.pdf` only; all other files checked as none | Restored status; editable 14 atoms / 15 bonds | [word-pasted.png](word-pasted.png), [reshiki-from-word.png](reshiki-from-word.png), [word-copyback.txt](word-copyback.txt) |
| Microsoft PowerPoint 16.115 (16.115.26110837) | New presentation, blank slide; selected caffeine picture / Picture Format UI | PowerPoint flavor set below | `com.adobe.pdf` only; all other files checked as none | Restored status; editable 14 atoms / 15 bonds | [powerpoint-pasted.png](powerpoint-pasted.png), [reshiki-from-powerpoint.png](reshiki-from-powerpoint.png), [powerpoint-copyback.txt](powerpoint-copyback.txt) |
| Microsoft Excel 16.115 (16.115.26110837) | New workbook; floating Picture 1 at A1 | Excel flavor set below | `com.adobe.pdf` only; all other files checked as none | Restored status; editable 14 atoms / 15 bonds | [excel-pasted.png](excel-pasted.png), [reshiki-from-excel.png](reshiki-from-excel.png), [excel-copyback.txt](excel-copyback.txt) |
| Preview 11.0 (1147) | New from Clipboard route could not be started; binding timed out without a window | Not collected | Untested | Not attempted | No image or clipboard dump; blocker described below |
| TextEdit 1.21 (419) | New rich-text document; caffeine image attachment. Cmd+A / Cmd+C | `com.apple.flat-rtfd`, `public.rtf`, `public.utf8-plain-text`, `public.utf16-external-plain-text` | None detected in any of the four returned files | `Could not paste: Invalid SMILES at byte 3`. No new picture or drawing was inserted. | [textedit-pasted.png](textedit-pasted.png), [reshiki-from-textedit.png](reshiki-from-textedit.png), [textedit-copyback.txt](textedit-copyback.txt) |
| Google Chrome 156.0.8078.80 (loaded test process) | New window at the requested local `probe.html`; attempted paste left contenteditable box empty | No valid copyback collected | Untested | Not attempted | [chrome-pasted.png](chrome-pasted.png) shows the empty box after a paste attempt, **not** a successful pasted picture |

The Word, PowerPoint, and Excel returned PDFs are each **byte-for-byte identical** to the 11,605 B canonical source PDF. This was checked directly; see [byte-verification.txt](byte-verification.txt). All seven ordered restore files also match their original bytes. Rich-text clipboard containers were checked with the supplied detector as requested; no separate recursive RTFD extraction was performed.

Clipboard flavor sets are listed in the order printed by `pbdump.swift`. All dumps in this run had one item (item 0); the raw `.bin` files are retained in each corresponding `*-copyback/` directory.

- **Word** (Part A BEFORE/AFTER and Part B): `com.microsoft.Art--GVML-ClipFormat`; `com.adobe.pdf`; `public.tiff`; `public.png`; `public.jpeg`; `com.microsoft.Object-Descriptor`; `com.microsoft.image-svg-xml`; `com.microsoft.ole.source.78550.0x105569a30`; `com.microsoft.DataObject`; `com.microsoft.appbundleid`.
- **PowerPoint**: `com.microsoft.PowerPoint-12.0-Internal-Shapes`; `com.microsoft.Object-Descriptor`; `com.microsoft.PowerPoint-12.0-Internal-Theme`; `com.microsoft.PowerPoint-12.0-Internal-Color-Scheme`; `com.microsoft.Art--GVML-ClipFormat`; `com.adobe.pdf`; `public.tiff`; `com.microsoft.ole.source.11937.0x7509b99500`; `com.microsoft.DataObject`; `com.microsoft.appbundleid`.
- **Excel**: `com.microsoft.Excel-2007-Internal-Shape`; `com.microsoft.Art--GVML-ClipFormat`; `com.adobe.pdf`; `public.tiff`; `com.microsoft.ole.source.14804.0x749bf5c370`; `com.microsoft.DataObject`; `com.microsoft.appbundleid`.
- **TextEdit**: `com.apple.flat-rtfd` (89,609 B); `public.rtf` (311 B); `public.utf8-plain-text` (3 B); `public.utf16-external-plain-text` (2 B).

Saved-file routes used fresh Word and PowerPoint documents, each pasted from the restored canonical AFTER clipboard. Each document was saved locally through its Save dialog. Right-click → Save as Picture… was available in both apps and offered **PNG** by default; that default was accepted. The DOCX and PPTX were extracted with `unzip -q` to the matching artifact directories, then every file under `word/media/` or `ppt/media/` was passed to the supplied detector.

| App / version | Saved-file route | File/media type | Payload result | ReShiki paste/status for this route | Evidence |
|---|---|---|---|---|---|
| Word 16.115 | Save new pasted document as DOCX | `word-saved.docx` contains `word/media/image1.emf` (33,456 B) | Valid, 14 atoms / 15 bonds in EMF bytes | Not reopened/copied back; this route checks saved media only | [word-saved.docx](word-saved.docx), [word-saved-payloads.txt](word-saved-payloads.txt) |
| Word 16.115 | Save as Picture…, default PNG | `word-picture.png`, 80 × 67 pixels, 1,942 B | None | Not pasted back; detector-only saved-picture check | [word-picture.png](word-picture.png), [word-saved-payloads.txt](word-saved-payloads.txt) |
| PowerPoint 16.115 | Save new pasted presentation as PPTX | `powerpoint-saved.pptx` contains `ppt/media/image1.emf` (33,456 B) | Valid, 14 atoms / 15 bonds in EMF bytes | Not reopened/copied back; this route checks saved media only | [powerpoint-saved.pptx](powerpoint-saved.pptx), [powerpoint-saved-payloads.txt](powerpoint-saved-payloads.txt) |
| PowerPoint 16.115 | Save as Picture…, default PNG | `powerpoint-picture.png`, 80 × 67 pixels, 1,942 B | None | Not pasted back; detector-only saved-picture check | [powerpoint-picture.png](powerpoint-picture.png), [powerpoint-saved-payloads.txt](powerpoint-saved-payloads.txt) |
| Preview 11.0 | New from Clipboard → Export PDF | No file created | Untested | Not attempted | Blocked before document creation |
| Preview 11.0 | New from Clipboard → Export PNG | No file created | Untested | Not attempted | Blocked before document creation |

The Word and PowerPoint package media each consist of one `image1.emf`. The detector validates a drawing payload present in those EMF bytes. This establishes retention in saved package media; it does not establish how ReShiki would handle a directly imported EMF or a copy after reopening the Office file. The two small PNG picture exports were viewed at their native size and were not enlarged or edited.

Every saved top-level PNG was opened and visually reviewed before this report. The review confirmed the six Part A status results, the Office and TextEdit pasted pictures, each completed ReShiki copyback result, and the empty Chrome probe. The filename `chrome-pasted.png` follows the requested naming convention but records an unsuccessful paste attempt. There are 15 window screenshots and two application-exported picture PNGs; no close-up crops were requested or produced.

| Image files | ReShiki source build | Window size in points | PNG size in pixels |
|---|---|---:|---:|
| `before-01-word-roundtrip.png`, `before-02-insert-pdf.png`, `before-03-insert-svg.png` | d670ed7a | 1400 × 900 | 2800 × 1800 each |
| `after-01-word-roundtrip.png`, `after-02-insert-pdf.png`, `after-03-insert-svg.png` | 7d45486c | 1400 × 900 | 2800 × 1800 each |
| `reshiki-from-word.png`, `reshiki-from-powerpoint.png`, `reshiki-from-excel.png`, `reshiki-from-textedit.png` | 7d45486c | 1400 × 900 | 2800 × 1800 each |
| `word-pasted.png` | 7d45486c | 1120 × 720 | 2240 × 1440 |
| `powerpoint-pasted.png` | 7d45486c | 1600 × 900 | 3200 × 1800 |
| `excel-pasted.png` | 7d45486c | 1402 × 859 | 2804 × 1718 |
| `textedit-pasted.png` | 7d45486c | 586 × 488 | 1172 × 976 |
| `chrome-pasted.png` | 7d45486c clipboard supplied; no image appeared | 1400 × 900 | 2800 × 1800 |
| `word-picture.png`, `powerpoint-picture.png` | 7d45486c | Application exports, not screenshots | 80 × 67 each |

Application versions were read from their installed Info.plist files. Chrome's initially observed version was 156.0.8078.80, and the test process (PID 20510) was confirmed to have that version's framework files loaded. Its installed plist had changed to 157.0.8103.78 by the final audit; no update was initiated by this run. Runtime framework evidence and final installed versions are recorded in [app-versions.txt](app-versions.txt).

The incomplete steps and cleanup limits are explicit:

- **Preview:** `cua.getApp` timed out when addressed by name, full app path, and bundle identifier (`Computer Use server error -10005: timeoutReached`). The process was running but had no on-screen window, so no controllable app handle was returned. No New-from-Clipboard document, copyback, or export was made. A request to permit launching its ordinary Open dialog with `open -a /System/Applications/Preview.app` remained unanswered; that fallback was not run. The computer-use tool requires explicit authorization before using another UI-control mechanism. Preview may remain running without a window because the same binding problem prevented UI cleanup.
- **Chrome:** the exact requested local page loaded in a new window, but clicking the contenteditable box and pressing Cmd+V left it empty. A subsequent attempt to bind the exact `file://` tab was explicitly rejected by the browser tool's URL security policy. No workaround was attempted after that rejection. No valid selection/copyback or ReShiki paste was performed. Only the created probe window was closed; Chrome's startup “What's New” window was left alone.
- Consequently, `preview-pasted.png`, `preview-copyback/`, `preview-copyback.txt`, `reshiki-from-preview.png`, `preview-export.pdf`, `preview-export.png`, `chrome-copyback/`, `chrome-copyback.txt`, and `reshiki-from-chrome.png` do not exist. No synthetic screenshots or clipboard results were substituted.
- The initial AFTER targeting failure required a fresh wrapper retry. A possible Swift mouse fallback was discussed and a helper file prepared, but the fallback was never executed; the retry used the normal computer-use API.
- Word, PowerPoint, Excel, TextEdit, Preview, and Chrome were not running at the initial inventory. All created unsaved Office/TextEdit documents were discarded; the requested saved Word and PowerPoint artifacts were closed after saving. Word, PowerPoint, Excel, and TextEdit were quit. The final ReShiki source drawing was clean with Undo disabled before Cmd+Q. No query was made against that ReShiki instance afterward.

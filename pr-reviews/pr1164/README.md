# Outlined SVG on the clipboard on every platform (PR 1164), 2026-11-13

Question: after this PR, does the SVG that ReShiki puts on the clipboard draw its text as
outlines on macOS and Linux (only Windows Copy Image did before), keep its physical size and
the editable drawing inside it, and paste the same picture into Word as before?

Base (before): main `fb116736`. Head (after): `fb116736` plus PR 1164 (`78721de8`). Debug
builds, each in a fresh detached worktree with its own target directory; the before and after
binaries have different SHA-256 (macOS `675839c8…` / `be54dc35…`, Linux `19405060…` /
`067d5c87…`). Every ReShiki run used a fresh `RESHIKI_DATA_DIR`. Input:
`fixtures/caffeine.rsk` (caffeine with a "Caffeine" caption: 7 text runs).

## macos/ (macOS 27.0.1 arm64)

A throwaway `.app` wrapper (`tools/make-app.sh`) launched with `open -n`, driven by computer
use (`tools/macos-computer-use-prompt.md`): Cmd+A, then **Copy Image** (Cmd+Shift+C), **Copy**
(Cmd+C) and right-click **Copy as → SVG**. After each, `tools/pbdump.swift` saved the
pasteboard item and `tools/svgsum.py` summarised its `public.svg-image`. Copy Image was pasted
into a new Word 16.115 document (`03-word-paste.png`). Then the Copy Image SVG alone was put on
the pasteboard (`tools/pbwrite.swift`) and pasted into a new ReShiki drawing (`06-*`), and into a
Chrome 157 page that reads and draws the `image/svg+xml` flavor (`chrome/`, `tools/probe-svg.html`
with `tools/cdp_paste.mjs`). `report.md` in each folder is the run log with every status message.

## linux/ (Arch Linux x64, X11 under Xvfb)

`tools/linux-run.sh`: real Ctrl+A, Ctrl+C and Ctrl+Shift+C in the ReShiki window (`xdotool`),
`image/svg+xml` read with `xclip`, pasted into a Chromium 149 page that draws that flavor, then
the SVG alone published with `xclip` and pasted (Ctrl+V, Ctrl+S) into a second ReShiki.

## Results

| Check | Before | After |
| --- | --- | --- |
| macOS Copy Image `public.svg-image` | 7 `<text>`, 1 `<path>` | 0 `<text>`, 10 `<path>` |
| macOS Copy `public.svg-image` | 7 `<text>` | 0 `<text>`, 10 `<path>` |
| macOS Copy as → SVG (`public.svg-image` and its text) | 7 `<text>` | 0 `<text>`, 10 `<path>` |
| Linux Copy and Copy Image `image/svg+xml` | 7 `<text>` | 0 `<text>`, 10 `<path>` |
| Size | 80.08 × 91.50 pt (Linux 91.64 pt) | same |
| `viewBox` | drawing coordinates | `0 0` + CSS-pixel size, same aspect |
| Drawing inside the SVG | yes | yes |
| SVG alone pasted into ReShiki | editable, 14 atoms, 15 bonds, caption | same |
| Chrome / Chromium page drawing the SVG flavor | picture, live text | same picture, outlined |
| Word (Copy Image) | caffeine picture with caption | same picture |
| Other pasteboard types and sizes (macOS) | PDF 14098, CDX 99137, PNG 99041, drawing 5142 bytes | unchanged |

Word's context menu does not name the format it took; the pasted picture is the same before and
after. The other Copy Image types are byte-for-byte the same size, so only the SVG changed.

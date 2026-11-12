# Linux Copy puts SMILES text on the clipboard (PR 1161), 2026-11-13

Base: ReShiki main `fb116736` (0.14.0). Head: the PR branch. Debug builds on Arch Linux x64.

## linux-x11/

A real desktop Copy in the ReShiki window (Ctrl+A, Ctrl+C sent with `xdotool`) on X11 under
Xvfb, then pastes, with `tools/run.sh`. Every ReShiki run used a fresh `RESHIKI_DATA_DIR`
and its own `XDG_SESSION_ID`, so the second ReShiki is a separate process, not a new tab.

- `caffeine/` (`fixtures/caffeine.rsk`, caffeine with a caption): `targets.txt` (xclip TARGETS),
  `text.txt` (each text target), `libreoffice.txt` and `libreoffice-*.png` (LibreOffice 25.8
  Writer and Impress, `tools/lo_paste.py`), `chromium-probe*.json/png` (Chromium 149 paste
  event on a contenteditable page and in a textarea, `tools/cdp_paste.mjs`), and
  `reshiki-paste.png/txt` plus `target.rsk` (Ctrl+V in a second ReShiki, then Ctrl+S).
- `reaction/` (`fixtures/reaction.cdxml`, composed from `fixtures/esterification.json`):
  TARGETS and text only.
- `shapes/` (`fixtures/shapes.rsk`, one caption, no molecules): TARGETS and text only.

| Case | Before | After |
| --- | --- | --- |
| Caffeine TARGETS | no text targets | adds `text/plain;charset=utf-8`, `text/plain`, `UTF8_STRING` |
| Caffeine text | not available | `Cn1c(=O)c2c(ncn2C)n(C)c1=O` (same as Copy SMILES) |
| LibreOffice Writer, Impress | PDF picture | PDF picture |
| Chromium page | picture (1 img) | picture (1 img) |
| Chromium textarea | nothing | the SMILES |
| Second ReShiki | editable drawing, caption kept | editable drawing, caption kept |
| Reaction | no text targets | no text targets |
| Caption only | no text targets | no text targets |

LibreOffice under Xvfb sometimes crashes whatever the payload; `run.sh` retries it with a
fresh profile, and the kept result is the completed run.

## Wayland

`tools/wayland.sh` runs the repository's own `scripts/wayland_clipboard_qa.sh` in the CI image
(`reshiki-ci-noble-desktop:main`) on the same machine. With this PR the harness also checks that
ordinary Copy offers the three text aliases with `CCO`, and that Paste of a published drawing
next to different text (`C`) inserts the drawing. Results: `wayland/`.

GNOME's clipboard manager (mutter `meta-clipboard-manager.c`) reads one MIME type on every
owner change, ranking `text/plain;charset=utf-8` above every image type, and keeps it after the
owner exits only if that read has finished. So at exit the GUI owner re-offers an ordinary Copy
without its text aliases and waits (bounded at 1.5 s) until a reader has read it, plus 250 ms.

Results (head with that exit handoff): `wayland/gnome` and `wayland/sway`, 13 real compositor
checks each (`manifest.json`). While ReShiki runs, Copy offers the SMILES text. After exit, GNOME's
fresh reader gets only `image/svg+xml`, byte-identical to the final copy's SVG
(`wayland/gnome/fresh-receiver`); Sway keeps nothing, as before. The GNOME QA passed in 5 of 5
runs on the handoff code, and Sway in 2 of 2. Without the handoff, GNOME kept only the SMILES text.

`linux-x11/after-quit-handoff/` repeats the X11 real-app run on that head: identical to `after/`.

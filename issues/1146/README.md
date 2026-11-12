# Clipboard compatibility evidence (issue 1146), 2026-11-12

ReShiki origin/main 11df00d5 (0.14.0). Input: a caffeine drawing with a caption.

- `windows/`: Windows 11 x64 25H2, Microsoft 365 16.0.20625.20076, Edge 157. The copy ran through ReShiki's
  real `clipboard::copy` from `tools/clip_harness.rs` (the test desktop is locked). Formats come from
  `EnumClipboardFormats`. Word/PowerPoint/Excel pastes ran through COM, and the Edge paste through DevTools
  (`tools/cdp_paste.mjs`, `tools/probe.html`). The experiments re-publish the Copy formats plus one
  extra format (`tools/republish.ps1`).
- `macos/`: macOS 27.0.1 arm64, Office 16.115, ChemDraw 26.1, Chrome 156. A real app Copy and Copy Image,
  dumped with `tools/pbdump.swift`, then pasted by hand into each app.
- `linux/`: Arch Linux x64, X11 under Xvfb. The macOS payload bytes (the same code path on Linux) were
  published through ReShiki's Linux clipboard worker. Then come `xclip` TARGETS, a LibreOffice 25.8 Writer/Impress paste
  (`tools/lo_paste.py`) and a Chromium 149 paste.

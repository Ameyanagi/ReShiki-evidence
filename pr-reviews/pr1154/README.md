# PR 1154 evidence: editable drawing inside ReShiki SVG and PDF pictures, and where it survives

Captured 2026-11-12 on macOS arm64 and Windows x64.

## Before/after (macOS arm64, 1400 × 900 pt window, caffeine fixture)

- BEFORE: the PNG-only PR #1153 (d670ed7a). AFTER: this PR at 7d45486c (the head only adds the Copy Image size cap from #1153 and a rebase).
- `*-01-word-roundtrip.png`: Copy Image → Word 16.115 → copy the picture → Paste in ReShiki.
- `*-02-insert-pdf.png`, `*-03-insert-svg.png`: Export PDF/SVG (AFTER with Include editable drawing) → Import → Choose file….

## Survival matrix

- `macos/`: pasteboard dumps checked with `haspayload.py` after Word, PowerPoint, Excel, TextEdit and Chrome; ReShiki screenshots after each copy back; saved .docx/.pptx media and Save as Picture checks; `capture-report.md` is the full run log.
- `windows/`: the same through the real copy and paste code (`clip_harness.rs`) driven by `survival.ps1` in an interactive session: Word and Excel by COM, Edge by DevTools. `survival-final.txt` is the PR head; `survival-pr1.txt` the PNG-only build; `sizes-main-with-1148.txt` main 11df00d5 with #1148's CF_DIB for size comparison.
- `macos/sizes-*.txt`: pasteboard sizes from `measure_sizes_test.rs` (main vs the PNG PR).

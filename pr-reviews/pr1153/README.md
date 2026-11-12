# PR 1153 evidence: editable drawing inside ReShiki PNG pictures

macOS arm64, window 1400 × 900 pt, 128% zoom, caffeine fixture opened in both builds.

- BEFORE: origin/main 131b5a6f. AFTER: PR head d670ed7a (the later head adds only the Copy Image size cap and a rebase on main).
- 01/02: Select all → Copy Image → Paste, then click one atom of the pasted copy.
- 03/04: Export → Figure → PNG; the AFTER build shows "Include editable drawing".
- 05/06: Export PNG, then Import → Choose file… of that PNG.
- exported-*.png: the two exported files; payload-check.txt shows the AFTER file carries the drawing (628-byte envelope) while the pixels are identical.

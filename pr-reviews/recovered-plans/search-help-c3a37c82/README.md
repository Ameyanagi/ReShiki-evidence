# Search and Help at the editor header

The native macOS screenshots use the checked app from commit `c3a37c82f09e183c47a6fd92aa762913a4a0dba8`. The app binary SHA-256 is `df2b4136229eb8841e0298cdce1cb9614b198cb449b86804f92696cc7a038095`. The native window is 1280 × 852 points including the title bar, and the Fischer esterification drawing is fitted at 81%.

1. Open the Fischer esterification example in three tabs with different filenames. The Search keycap and header controls stay visible.
2. Click Search and type `benzene`. The palette opens with its search field focused.
3. In Help, type `cmd+k` and `cmd+shift+p`. The top result identifies Command palette for each. Pressing either shortcut while Help is open preserves Help’s keyboard focus.
4. Run Import from Search. Type `ethanol:` into the chemical-name field. Command–K and Command–Shift–P each move focus into the palette. Closing it preserves the typed name. Run Export panel from Search to open Export.
5. Repeat the header and palette checks with the dark interface.

The separate 1040 × 680 PNG is the exact source’s Iced renderer test snapshot. Its example uses benzene and three tabs. It shows the compact header at the minimum client size.

# Reopen a dipole arrow in ChemDraw

This original single-arrow specimen was reduced from the project's generated arrow probe. `before.cdx` was exported by the ReShiki drawing build at `e4feeb21`. `after.cdx` was exported by the exact fixed Rust executable at `d7aabca81`, using the same arrow and export options. The only change in the files is the length and payload of the binary Dipole property.

The old binary fails in the ChemDraw SDK with error 536. The fixed binary opens in ChemDraw 26.1. The native screenshot shows its full arrowhead and the cross at the tail at Actual Size. ChemDraw SDK 26.8 also opened and resaved it with `Dipole="yes"`; its enlarged render matches its rendering of the source dipole.

# Native drawing tables in ReShiki and ChemDraw

These captures use Apple Silicon macOS and ReShiki `d38970f32f7f159c4c7e3f6adaf74f00042f4770`. Both inputs are original project drawings saved in ChemDraw.

- Open [the reaction table](reaction-table-native.cdx) to see the three columns, two rows, editable molecule and cell captions at 105%. Choose the single bond tool and click the top-right benzene vertex to add a bond within the structure cell. One Undo restores benzene.
- Open [the overflow fixture](overflow-probe-native.cdx) at 83%. Green text and the ring extend past their cell boundaries in the underlying data. The window shows the clipped result and the separate coincident colored borders.
- Run `reshiki --cli convert reaction-table-native.cdx -o round-trip.cdx` and open the result in ChemDraw 26.1. The six cells, molecule and captions are visible at ChemDraw's native view scale.

The final test binary exercised 15 supported CLI routes and ChemDraw SDK 26.8 reopened and resaved 12 native outputs. Each sample retained its six cells or, for the aromatic probe, its two cells and the aromatic circle in the molecule's cell.

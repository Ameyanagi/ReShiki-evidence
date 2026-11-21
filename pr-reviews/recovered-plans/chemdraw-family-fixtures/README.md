# Native ChemDraw references for tables and TLC plates

These two original review drawings were saved from ChemDraw 26.1.0.6801 as both CDX and CDXML. The window captures show the native editor. The tighter PNGs are separate reference renders from the installed ChemDraw engine.

| Drawing | Editable source | Native editor | Reference render |
| --- | --- | --- | --- |
| Three-lane TLC plate | [CDX](tlc-plate.cdx) · [CDXML](tlc-plate.cdxml) | [ChemDraw window](tlc-plate-in-chemdraw.jpg) | [Plate and spots](tlc-plate-render.png) |
| Two-row chemistry table | [CDX](reaction-table.cdx) · [CDXML](reaction-table.cdxml) | [ChemDraw window](reaction-table-in-chemdraw.jpg) | [Cells and structure](reaction-table-render.png) |

The plate was created with ChemDraw’s TLC tool. The three lanes have retention factors 0.28, 0.51, and 0.77. The first spot shows its Rf value and the last is hollow. Both files use the same plate and spots.

The table started as an original CDXML seed with six cells and a benzene ring in the middle cell. I opened it in ChemDraw, selected the last cell’s text and changed Example to Reference, then saved both formats. Cell content uses coordinates relative to each cell, while the border and cell bounds place the grid on the document page.

At ReShiki commit `e4feeb21`, both TLC files returned “No supported drawing objects found”. The table opens from both formats and retains its six atoms, six bonds, and five labels. It loses the table, all 24 border records, and the position of the contents within their cells. These files are references for the upcoming family implementation.

# ChemDraw table borders and clipped contents

The original six-cell probe is based on the ReShiki review reaction table. Open `source.cdxml` in ChemDraw 26.1 at Actual Size to reproduce the native desktop capture. An independent open and resave in ChemDraw SDK 26.8 produced the `reopened` files and the detail image.

- The broad red border between Entry and Structure is drawn first in the header. The second cell draws a narrow blue stroke over its centre. The opposite order in the bottom row leaves only the broad red stroke visible.
- The green and purple horizontal strokes under Yield show the same ordered painting on a horizontal edge.
- The benzene ring is clipped at the edge of its owning cell. Text wraps to the available width and clips below the cell or table. The full strings and original ring remain in the saved document. The CDXML records the calculated text wraps in `LineStarts`.

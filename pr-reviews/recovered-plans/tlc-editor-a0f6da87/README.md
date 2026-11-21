# Create and edit a TLC plate in ReShiki

The ReShiki captures use Apple Silicon macOS and editor commit `a0f6da878043876982eb116251df0a8984a98454`.

1. Open the [native three-lane reaction plate](../tlc-reaction-reference/). Select the plate, then choose Lane 3 and Spot 1 in Properties. At 66% zoom, the original shows Rf 0.32 and a 7 pt spot.
2. Enter 0.48 and press Return. The spot moves up its lane, and the visible Rf label retains its format. One Undo restores 0.32.
3. On a fresh drawing, choose TLC plate in the toolbar and drag a frame. The tool creates three lanes. Add a fourth lane and one spot, then remove both using Properties.

The final screenshot shows ChemDraw 26.1 reopening the CDX exported from the edited plate. The edited drawing was saved and reopened as RSK, then exported to CDX and CDXML with the earlier `3f93384c` editor build. Both exported formats reopened in ChemDraw with the four spots and Rf 0.48. The updated `a0f6da87` build exposes Lane, Spot, Filled and Show Rf through macOS accessibility.

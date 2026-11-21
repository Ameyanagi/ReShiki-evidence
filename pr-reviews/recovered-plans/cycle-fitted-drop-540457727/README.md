# Fitted drop on a bowed cycle step

These native macOS screenshots use the build at `540457727`. The three-member rectangular Suzuki–Miyaura example includes a loose eight-atom aryl–Pd–Br fragment. The drawing and the camera stay at 29% through the before, drop, Undo and reopening captures.

I selected the fragment and dragged it onto the visible bowed Transmetalation arrow. ReShiki created Intermediate 3 under the drop position. The neighboring reversible shafts follow the same bow, with a gap around the inserted structure. Undo restores the loose fragment and the original three-member cycle. Redo and Save As produce the included [four-member drawing](fitted-suzuki.rsk), which reopened with the fitted route.

The final branch at `f495f3db` adds selection bounds for the chosen cycle shape and keeps fitted sources through numeric and drag Tilt. Rust tests exercise the held preview and release against the same fitted drawing, and verify transforms, persistence and Undo/Redo.

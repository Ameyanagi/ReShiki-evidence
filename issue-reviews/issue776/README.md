# Issue 776: label-to-bond spacing

Rendered with `reshiki --cli render` on macOS arm64 from origin/main b0dae4ad
plus the #1070 branch (label-margin code unchanged; default output identical).

- `cyclophosphamide-margin-1.6.png` / `-0.8.png`: SMILES
  `ClCCN(CCCl)P1(=O)NCCCO1` converted to CDXML, root `MarginWidth` set to 1.6
  (JACS / ACS default) and 0.8 pt. The label-to-bond gap follows Label margin.
- `vertical-labels-*.png`: N and O labels with bonds straight above and below,
  drawn at 4x size (40 pt labels, 6.4 pt margin). Measured gaps above and below
  are equal (1.56 pt at 10 pt scale) in Arial and with a missing font family
  (fallback font measured and drawn).

# Export by destination

Captured in the native macOS editor at ReShiki commit `2ef1f07dc5e2826024c702b48afcb632c61b94d2`. The app’s executable SHA-256 was `2d95aba9d6f28afa0bc4facd332eb44a82d0bf8a60286f6238f751e194f2fa04`. The captures use the Publication theme at 250%.

1. Open [Lactic acid.rsk](fixtures/Lactic%20acid.rsk), choose Export, and use Copy for Word & PowerPoint. The status line confirms the editable drawing and images were copied.
2. Export a white PNG at 300 dpi. Change the current options to black at 600 dpi, then use Export again. The action wrote the same 283 × 246 PNG to the same path without reopening the save dialog. The PNGs were byte-identical and had SHA-256 `e547ba9c6c19f8a0d44f89cfa1f945c94896d3d511337ee5eca0461372117825`. The same drawing was used for the byte comparison.
3. Choose SMILES in Structure and click Copy. Open Pages & printing, then close it to return to Export with the current panel options.
4. Open [Undefined lactic acid.rsk](fixtures/Undefined%20lactic%20acid.rsk) and run Check drawing. Export shows one undefined stereocenter with Review. Review opens the prior C2 finding. This second drawing has no Export again row. Return to the first drawing and reopen Export to see the remembered figure and the restored background defaults.

The second fixture shares the first drawing’s geometry and omits its stereochemical annotation and name. The walkthrough checked actual clipboard feedback, panel controls, and saved files. Print and paste inside Office were outside this walkthrough.

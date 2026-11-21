# ChemDraw CDX with unknown atom stereochemistry

The ReShiki macOS window shows the original ChemDraw CDX opened by the build at `58a218ac`. Properties reports five atoms, four bonds, and the canonical SMILES `CN=C=NC`.

I used Save As to write a new CDX from that window and reopened the saved file in ChemDraw 26.1. The two ChemDraw screenshots show the source and the re-export at the same zoom, including the warning marker ChemDraw shows for the central atom in both drawings. The captures are cropped to the document title and the occupied canvas.

ChemDraw SDK 26.8 reopened the original CDX, paired CDXML, authored CDXML, and all six corresponding CLI outputs. All nine SDK renders matched byte for byte. The SDK reported the central state as unknown in each and reported zero assigned atom stereocentres.

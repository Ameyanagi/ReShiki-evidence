"""E2 evidence: open pictures with and without an embedded ReShiki drawing."""
import sys
from pathlib import Path

import reshiki

here = Path(__file__).parent
print(f"reshiki {reshiki.version() if hasattr(reshiki, 'version') else reshiki.__version__}")
plain = reshiki.Molecule.from_smiles("CCO")
for extension in ("png", "svg", "pdf"):
    cases = {
        f"ethanol.{extension} (exported by the app with the editable drawing)": here / f"ethanol.{extension}",
        f"plain.{extension} (written by this package, no drawing inside)": plain.save(
            Path(sys.argv[1]) / f"plain.{extension}"
        ),
    }
    for label, path in cases.items():
        try:
            drawing = reshiki.Drawing.open(path)
            print(f"{label}: {type(drawing).__name__} {drawing.smiles()}")
        except Exception as error:
            print(f"{label}: {type(error).__name__}: {error}")

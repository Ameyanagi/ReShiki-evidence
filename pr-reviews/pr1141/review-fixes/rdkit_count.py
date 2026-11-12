"""Count the configurations RDKit enumerates for each enhanced-stereo input.

Usage: count.py FILE...   (.smi/.cxsmi: one CXSMILES per line; .mol; .cdxml)
"""
import sys
from rdkit import Chem
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers


def count(mol):
    return len({Chem.MolToSmiles(m) for m in EnumerateStereoisomers(mol)})


def groups(mol):
    names = {Chem.StereoGroupType.STEREO_ABSOLUTE: "abs", Chem.StereoGroupType.STEREO_AND: "&", Chem.StereoGroupType.STEREO_OR: "o"}
    return " ".join(
        names[g.GetGroupType()] + ":" + ",".join(str(a.GetIdx()) for a in g.GetAtoms())
        for g in mol.GetStereoGroups()
    )


for path in sys.argv[1:]:
    if path.endswith((".smi", ".cxsmi", ".txt", ".smiles")):
        for line in open(path):
            line = line.strip()
            if line:
                mol = Chem.MolFromSmiles(line)
                print(f"{path}\t{line}\t{count(mol)}\t{groups(mol)}")
    elif path.endswith(".mol"):
        mol = Chem.MolFromMolFile(path)
        print(f"{path}\t{count(mol)}\t{groups(mol)}")
    elif path.endswith(".cdxml"):
        mols = Chem.MolsFromCDXMLFile(path)
        mol = mols[0]
        for other in mols[1:]:
            mol = Chem.CombineMols(mol, other)
        print(f"{path}\t{len(mols)} fragment(s)\t{count(mol)}\t{groups(mol)}")

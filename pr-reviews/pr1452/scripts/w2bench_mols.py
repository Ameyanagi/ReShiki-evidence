"""Build the benchmark molecule set: one fixed 3D geometry per molecule (ETKDGv3 seed 42 + MMFF94s)."""
import math, sys, pathlib
from rdkit import Chem
from rdkit.Chem import AllChem

OUT = pathlib.Path(sys.argv[1])
SMILES = {
    "water": "O",
    "benzene": "c1ccccc1",
    "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "ala-phe": "C[C@H](N)C(=O)N[C@@H](Cc1ccccc1)C(=O)O",
    "propranolol": "CC(C)NCC(O)COc1cccc2ccccc12",
    "tyr-gly-gly-phe": "N[C@@H](Cc1ccc(O)cc1)C(=O)NCC(=O)NCC(=O)N[C@@H](Cc1ccccc1)C(=O)O",
    "cholesterol": "C[C@H](CCCC(C)C)[C@H]1CC[C@@H]2[C@@]1(CC[C@H]3[C@H]2CC=C4[C@@]3(CC[C@@H](C4)O)C)C",
    "atorvastatin": "CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O",
    "ritonavir": "CC(C)c1nc(CN(C)C(=O)N[C@@H](C(C)C)C(=O)N[C@@H](Cc2ccccc2)C[C@H](O)[C@H](Cc2ccccc2)NC(=O)OCc2cncs2)cs1",
    "sirolimus": "C[C@@H]1CC[C@H]2C[C@@H](/C(=C/C=C/C=C/[C@H](C[C@H](C(=O)[C@@H]([C@@H](/C(=C/[C@H](C(=O)C[C@H](OC(=O)[C@@H]3CCCCN3C(=O)C(=O)[C@@]1(O2)O)[C@H](C)C[C@@H]4CC[C@H]([C@@H](C4)OC)O)C)/C)O)OC)C)C)/C)OC",
    "cyclosporin-a": "CC[C@H]1C(=O)N(CC(=O)N([C@H](C(=O)N[C@H](C(=O)N([C@H](C(=O)N[C@H](C(=O)N[C@@H](C(=O)N([C@H](C(=O)N([C@H](C(=O)N([C@H](C(=O)N([C@H](C(=O)N1)[C@@H]([C@H](C)C/C=C/C)O)C)C(C)C)C)CC(C)C)C)CC(C)C)C)C)C)CC(C)C)C)C(C)C)CC(C)C)C)C",
}

def write_xyz(path, symbols, coords, comment):
    lines = [str(len(symbols)), comment]
    lines += [f"{s:2s} {x:14.8f} {y:14.8f} {z:14.8f}" for s, (x, y, z) in zip(symbols, coords)]
    path.write_text("\n".join(lines) + "\n")

for name, smi in SMILES.items():
    mol = Chem.AddHs(Chem.MolFromSmiles(smi))
    params = AllChem.ETKDGv3(); params.randomSeed = 42
    assert AllChem.EmbedMolecule(mol, params) == 0, name
    props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94s")
    ff = AllChem.MMFFGetMoleculeForceField(mol, props)
    assert ff.Minimize(maxIts=5000) == 0, f"{name}: MMFF did not converge"
    conf = mol.GetConformer()
    write_xyz(OUT / f"{name}.xyz", [a.GetSymbol() for a in mol.GetAtoms()],
              [tuple(conf.GetAtomPosition(i)) for i in range(mol.GetNumAtoms())],
              f"{name} {smi} ETKDGv3 seed 42 + MMFF94s")
    (OUT / f"{name}.smi").write_text(smi + "\n")
    print(name, mol.GetNumAtoms())

# Ferrocene, eclipsed D5h: Fe-ring centroid 1.66 A, C-C 1.43 A, C-H 1.08 A.
r = 1.43 / (2 * math.sin(math.pi / 5)); sym, xyz = ["Fe"], [(0.0, 0.0, 0.0)]
for z in (1.66, -1.66):
    for k in range(5):
        a = 2 * math.pi * k / 5
        sym.append("C"); xyz.append((r * math.cos(a), r * math.sin(a), z))
        sym.append("H"); xyz.append(((r + 1.08) * math.cos(a), (r + 1.08) * math.sin(a), z * 1.03))
write_xyz(OUT / "ferrocene.xyz", sym, xyz, "ferrocene eclipsed D5h, idealized")
print("ferrocene", len(sym))
# Uranium hexafluoride, Oh, U-F 1.996 A.
d = 1.996; uf6 = [(d,0,0),(-d,0,0),(0,d,0),(0,-d,0),(0,0,d),(0,0,-d)]
write_xyz(OUT / "uf6.xyz", ["U"] + ["F"] * 6, [(0.0, 0.0, 0.0)] + uf6, "UF6 Oh, U-F 1.996 A")
print("uf6", 7)

import reshiki
print("reshiki", reshiki.__version__)
m = reshiki.Molecule.from_smiles("C[C@H](O)C(=O)O |r|")
print(m.smiles())
c = reshiki.parse("C/C=C=C=C/C")
print(c.smiles())
r = reshiki.render_many(["C[C@H](O)C(=O)O |r|", "CCO"], "svg")
print("errors:", r.errors, "warnings:", getattr(r, "warnings", "(no attribute)"))

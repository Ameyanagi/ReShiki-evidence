# PR 1167: reshiki --cli name before and after

`reshiki --cli name --smiles <SMILES>` with the base (95bcf628) and head (d7d0d218) debug builds on Arch Linux x64, RESHIKI_NAMING_HELPER/RESHIKI_INCHI_HELPER set to each build, RESHIKI_DATA_DIR a fresh temp dir.

### salt-order
SMILES: `[Cl-].[Cl-].C[C@]12CC[C@H]3[C@@H](CCC4CC(CC[C@]34C)[NH3+])[C@@H]1CCC2.CCCC[NH3+]`
before:
```
(8S,9S,10S,13S,14S)-10,13-dimethylgonan-3-aminium butan-1-aminium dichloride
(exit 0)
```
after:
```
butan-1-aminium (8S,9S,10S,13S,14S)-10,13-dimethylgonan-3-aminium dichloride
(exit 0)
```
### diazonium
SMILES: `[O-]C(=O)c1ccc(cc1)[N+]#N`
before:
```
4-(diazonio)benzoate
(exit 0)
```
after:
```
4-(diazyn-1-ium-1-yl)benzoate
(exit 0)
```
### diazonium-acetate
SMILES: `N#[N+]CC(=O)[O-]`
before:
```
diazonioacetate
(exit 0)
```
after:
```
(diazyn-1-ium-1-yl)acetate
(exit 0)
```
### enclosure
SMILES: `O=C(O)Cc1cccc2cc3ccccc3cc12`
before:
```
anthracen-1-ylacetic acid
(exit 0)
```
after:
```
(anthracen-1-yl)acetic acid
(exit 0)
```
### multiplicative-ether
SMILES: `c1ccccc1Oc2ccc(Oc3ccccc3)cc2`
before:
```
1,4-diphenoxybenzene
(exit 0)
```
after:
```
1,1'-[1,4-phenylenebis(oxy)]dibenzene
(exit 0)
```
### multiplicative-glycol
SMILES: `OC(=O)COCCOCC(=O)O`
before:
```
[2-(carboxymethoxy)ethoxy]acetic acid
(exit 0)
```
after:
```
2,2'-[ethane-1,2-diylbis(oxy)]diacetic acid
(exit 0)
```
### multiplicative-bisphenolA
SMILES: `CC(C)(c1ccc(O)cc1)c1ccc(O)cc1`
before:
```
4-[2-(4-hydroxyphenyl)propan-2-yl]phenol
(exit 0)
```
after:
```
4,4'-(propane-2,2-diyl)diphenol
(exit 0)
```
### multiplicative-bromo
SMILES: `Brc1ccc(Oc2ccc(Br)cc2)cc1`
before:
```
1-bromo-4-(4-bromophenoxy)benzene
(exit 0)
```
after:
```
1,1'-oxybis(4-bromobenzene)
(exit 0)
```
### trityl
SMILES: `c1ccccc1C(c1ccccc1)c1ccccc1`
before:
```
(diphenylmethyl)benzene
(exit 0)
```
after:
```
1,1',1''-methanetriyltribenzene
(exit 0)
```
### isotope-methoxy
SMILES: `[2H]C([2H])([2H])Oc1ccccc1`
before:
```
reshiki: error: This structure can't be named locally yet: openclatura: isotope equivalent-numbering proof failed
(exit 1)
```
after:
```
(2H3)methoxybenzene
(exit 0)
```
### isotope-dimethyl
SMILES: `[13CH3]c1ccccc1[13CH3]`
before:
```
reshiki: error: This structure can't be named locally yet: openclatura: isotope equivalent-numbering proof failed
(exit 1)
```
after:
```
1,2-di[(13C)methyl]benzene
(exit 0)
```
### isotope-thiolanyl
SMILES: `c1cnccc1C1SCC[14CH2]1`
before:
```
reshiki: error: This structure can't be named locally yet: openclatura: isotope equivalent-numbering proof failed
(exit 1)
```
after:
```
4-[(3-14C)thiolan-2-yl]pyridine
(exit 0)
```
### isotope-acid
SMILES: `OC(=O)CC(C)(C)[13CH3]`
before:
```
3,3-dimethyl(4-13C)butanoic acid
(exit 0)
```
after:
```
3,3-dimethyl(4-13C)butanoic acid
(exit 0)
```
### hydrogencarbonate
SMILES: `[Na+].OC([O-])=O`
before:
```
reshiki: error: Name reconstruction failed: The source structure differs in connectivity, charge, isotope, tautomer or stereochemistry. No name was assigned
(exit 1)
```
after:
```
sodium hydrogen carbonate
(exit 0)
```
### adduct-hcl
SMILES: `CCN.Cl`
before:
```
reshiki: error: Select one complete molecule or a charge-balanced salt; neutral components, mixtures, net-charged sets and zwitterions mixed with ions are unsupported
(exit 1)
```
after:
```
reshiki: error: Select one complete molecule or a charge-balanced salt; neutral components, mixtures, net-charged sets and zwitterions mixed with ions are unsupported
(exit 1)
```
### cyano
SMILES: `N#CCCC(=O)O`
before:
```
3-cyanopropanoic acid
(exit 0)
```
after:
```
3-cyanopropanoic acid
(exit 0)
```
### cation-parent
SMILES: `OCc1cc[n+](C)cc1`
before:
```
(1-methylpyridin-1-ium-4-yl)methanol
(exit 0)
```
after:
```
4-(hydroxymethyl)-1-methylpyridin-1-ium
(exit 0)
```
### betaine
SMILES: `C[N+](C)(C)CC(=O)[O-]`
before:
```
(trimethylammonio)acetate
(exit 0)
```
after:
```
(N,N-dimethylmethanaminiumyl)acetate
(exit 0)
```
### diamine-locants
SMILES: `CN(C)CCCNC`
before:
```
N,N,N'-trimethylpropane-1,3-diamine
(exit 0)
```
after:
```
N^1,N^1,N^3-trimethylpropane-1,3-diamine
(exit 0)
```
### benzodiazepinone
SMILES: `CN1C(=O)CN=C(C2=C1C=CC(=C2)Cl)C3=CC=CC=C3`
before:
```
7-chloro-1-methyl-5-phenyl-1H-1,4-benzodiazepin-2(3H)-one
(exit 0)
```
after:
```
7-chloro-1-methyl-5-phenyl-1,3-dihydro-2H-1,4-benzodiazepin-2-one
(exit 0)
```
### thioperoxol
SMILES: `CSO`
before:
```
(hydroxysulfanyl)methane
(exit 0)
```
after:
```
methane-SO-thioperoxol
(exit 0)
```
### mandelic
SMILES: `OC(C(=O)O)c1ccccc1`
before:
```
(hydroxy)(phenyl)acetic acid
(exit 0)
```
after:
```
hydroxy(phenyl)acetic acid
(exit 0)
```
### paracyclophane
SMILES: `C1Cc2ccc(cc2)CCc2ccc1cc2`
before:
```
1,4(1,4)-dibenzenacyclohexaphane
(exit 0)
```
after:
```
tricyclo[8.2.2.2^{4,7}]hexadeca-1(12),4,6,10,13,15-hexaene
(exit 0)
```
### benzocarbazoledione
SMILES: `CCc1cccc2c1[nH]c1c3c(c(C(C)=O)cc12)C(=O)C=CC3=O`
before:
```
5-acetyl-10-ethyl-11H-benzo[a]carbazole-1,4-dione
(exit 0)
```
after:
```
5-acetyl-10-ethyl-1H-benzo[a]carbazole-1,4(11H)-dione
(exit 0)
```
### salt-order-alkoxide
SMILES: `[Na+].CC(C)(C)[O-].[Na+].C[O-]`
before:
```
disodium methoxide tert-butoxide
(exit 0)
```
after:
```
disodium tert-butoxide methoxide
(exit 0)
```

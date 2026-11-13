| Input | Before: formula, mass, InChI, unpaired | Before warning | After: formula, mass, InChI, unpaired |
| --- | --- | --- | --- |
| `[C]` | CH2, 14.027, `InChI=1S/CH2/h1H2`, 2 | Atom C1 had 4 radical electrons; ReShiki keeps at most 2 and drew it as a triplet; its hydrogen count changed from 0 to 2 | C, 12.011, `InChI=1S/C`, 4 |
| `[CH]` | CH2, 14.027, `InChI=1S/CH2/h1H2`, 2 | Atom C1 had 3 radical electrons; ReShiki keeps at most 2 and drew it as a triplet; its hydrogen count changed from 1 to 2 | CH, 13.019, `InChI=1S/CH/h1H`, 3 |
| `[N]` | HN, 15.015, `InChI=1S/HN/h1H`, 2 | Atom N1 had 3 radical electrons; ReShiki keeps at most 2 and drew it as a triplet; its hydrogen count changed from 0 to 1 | N, 14.007, `InChI=1S/N`, 3 |
| `[B]` | HB, 11.82, `InChI=1S/BH/h1H`, 2 | Atom B1 had 3 radical electrons; ReShiki keeps at most 2 and drew it as a triplet; its hydrogen count changed from 0 to 1 | B, 10.812, `InChI=1S/B`, 3 |
| `[Si]` | H2Si, 30.102, `InChI=1S/H2Si/h1H2`, 2 | Atom Si1 had 4 radical electrons; ReShiki keeps at most 2 and drew it as a triplet; its hydrogen count changed from 0 to 2 | Si, 28.086, `InChI=1S/Si`, 4 |
| `[Al]` | HAl, 27.99, `InChI=1S/Al.H`, 2 | Atom Al1 had 3 radical electrons; ReShiki keeps at most 2 and drew it as a triplet; its hydrogen count changed from 0 to 1 | Al, 26.982, `InChI=1S/Al`, 3 |
| `[C+]` | CH+, 13.019, `InChI=1S/CH/h1H/q+1`, 2 | Atom C1 had 3 radical electrons; ReShiki keeps at most 2 and drew it as a triplet; its hydrogen count changed from 0 to 1 | C+, 12.011, `InChI=1S/C/q+1`, 3 |

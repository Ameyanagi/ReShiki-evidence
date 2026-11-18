## Why

Compare C2b, the third Compare follow-up after the polish PR (#1235) and C2a (#1236). Compare matched molecules by ReShiki's ids, then by SMILES. A molecule that was both edited and given new ids, as after importing a scheme again, showed as **Molecule removed** plus **Molecule added**, with every atom painted. Adding a nitro group to a re-imported ester should be one chemical change, painted where it changed.

## Approach

Plan section 3, with the critic's corrections and decisions 2, 3 and 9.

**Order of matching.** By id, then by SMILES (unchanged), then the scheme's common move is fitted again from all pairs so far, then:

1. **By constitution** (`MatchedBy::Constitution`): the same canonical SMILES written without stereo or isotopes (`Signature.constitution`), paired nearest first like SMILES. This catches a stereo flip drawn anew.
2. **By structure** (`MatchedBy::Structure`), in the new `compare/structure.rs`.

**Mapper** (`reaction_mapping/search.rs`). `correspond(left, right, budget, cost)` reuses the bounded search under Compare's own policy, and leaves `propose` untouched:

- `Graph::compared` ignores atom maps and isotopes, and marks ring bonds (a bond is in a ring when its ends stay joined without it). A bond is kept only as one of the same order and ring membership.
- Compare ranks a pairing by bonds kept, then by the lowest total integer cost, then by the first found. The cost is the distance in hundredths of a bond length once the two centroids meet. The mapper's finer preferences, fewest changed atoms first, don't count for Compare. If they did, its optimistic bound would never equal the best, and a 97-atom pair would take 177M work. `propose` keeps its tie pruning (it stops at an equal score once two bests were seen), its isotope rule, its map anchors and its pre-charged work. The shared core (`domains`, `run`) is extracted unchanged.
- `correspond` returns the work it used, so Compare can enforce one budget across all its searches.

**Acceptance** (`compare/structure.rs`):

- Candidates are molecules left unmatched with readable chemistry on both sides. A per-class bound filters them before any search: heavy bonds by (elements, order, ring). The two molecules must also have the same number of ring systems.
- Similarity is kept heavy-atom bonds over the bonds of either, kept / (L + R − kept). Accept only if it is **≥ 0.5** with **≥ 3** bonds kept, and every ring system pairs with exactly one on the other side **through ring bonds kept between them**.
- A pair must be **each molecule's clear best**. Similarities are compared in 0.05 steps. An equally similar rival must be both strictly farther and at least twice as far. A rival of unknown worth leaves both unmatched if its bound could reach the winner. That covers a rival the budget skipped or cut short, one over 128 atoms, and one whose best pairing splits ring systems. Distance never matters otherwise, so far-apart molecules match when the match is unambiguous.
- **Budget** (work units, not time): 20,000 states and 10,000,000 work per pair, and 40,000,000 per comparison, constitution pairings included. One pass through two 128-atom molecules costs about 7M in the mapper's accounting. With more than 32 such molecules on a side, none are matched.

**Under a pairing.** Constitution and structure correspondences feed C2a's `edit_mapped`, so paint is local and the wording is the same as for id matches. A constitution pairing is used only if it keeps every bond; otherwise the molecule is painted whole, as before. The fit uses only matched atoms whose neighbours are matched too. The chemical line's detail reads **Different chemistry · matched by structure (ids changed)**.

**ID guard.** A shared-id pair counts a kept bond only when both endpoints keep their elements, and needs kept bonds ≥ ½ × the bonds of the smaller molecule. A pair keeping less than half the bonds of the *larger* molecule is weak evidence. It is used only when SMILES, constitution and structure matched neither molecule. In a fresh re-import, the ethanol took three of the ester's old ids and kept one of its bonds. That pair now yields to the real matches, while a molecule cut to under half its size, with its ids kept, is still one chemical change.

### Thresholds, and why

| Rule | Value | Why |
|---|---|---|
| Similarity | ≥ 0.5 | Pyridine ↔ benzene sits exactly here (4 of 6 aromatic bonds kept); anything less is mostly a different molecule. |
| Bonds kept | ≥ 3 | Rejects water → methanol and ethanol → propanol, where any pairing looks similar. |
| Same order and ring membership | always | Biphenyl ↔ hexylbenzene would otherwise keep 12 of 13 bonds (0.92); n-butane ↔ cyclobutane 0.75. Now 0.39 and 0. |
| Ring systems one to one | always | Biphenyl (two) never pairs with hexylbenzene (one), nor a fused system with separate rings. |
| Similarity steps | 0.05 | Near-equal candidates count as equal, so distance decides, or nothing does. |
| Distance tie-break | strictly nearer and ≤ ½ the next | `0 ≤ 0/2` would accept two candidates at the same place. |
| Per pair / per comparison | 20k states, 10M / 40M work | Deterministic bounds, the same on every machine; 10M covers one pass through two 128-atom molecules. |

## Evidence

_Pending._

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | pending: checks running |
| PR CI | pending |

## Risk

- **False structure matches**, the highest risk. Mitigated by the thresholds, strict mutual best candidates, excluding small and unverifiable molecules, and saying **matched by structure** on the row. Two adversarial review rounds focused on this.
- **Mapper refactor**: `propose` moved into shared helpers. All `reaction_mapping` tests pass unchanged.
- An element change near the threshold, such as pyridine for benzene, matches; larger rewrites stay removed plus added.
- Small molecules with sequential ids from a fresh import can still pair by id when they keep half the larger molecule's bonds between atoms of the same elements. Butane and propan-1-ol is an example; it reads as a chemical change.
- Water and other molecules with fewer than three heavy bonds never match by structure. A hydrogen-isotope edit to one of them, such as `O` → `[2H]O` re-imported, stays removed plus added.

## Changelog

`docs/changes/unreleased/feat-compare-c2b.md`

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

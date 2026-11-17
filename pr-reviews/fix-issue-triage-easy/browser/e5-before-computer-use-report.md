# ReShiki before-build UI verification

Tested `http://localhost:8191/examples/evidence.html?auto=150&build=before&residues=100` in a new Google Chrome window. The PNGs show the full 3320 × 2000 pixel window. The eight during captures span 19.9 seconds, measured from the first frame showing `FILE DROPPED`.

| Screenshot | Time from first drop frame | Banner text | Bottom-left status-line text |
| --- | ---: | --- | --- |
| [01-before-drop.png](01-before-drop.png) | Before drop | `before: dropping a large drawing in 11 s` | `Document opened` |
| [02-during-1.png](02-during-1.png) | 0.0 s | `before: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held)` | `Document opened` |
| [02-during-2.png](02-during-2.png) | 1.1 s | `before: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held)` | `Document opened` |
| [02-during-3.png](02-during-3.png) | 4.0 s | `before: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held)` | `Document opened` |
| [02-during-4.png](02-during-4.png) | 8.1 s | `before: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held)` | `Document opened` |
| [02-during-5.png](02-during-5.png) | 8.8 s | `before: FILE DROPPED. Page clock since the drop: 0.5 s (it stands still while the page is held)` | `Document opened` |
| [02-during-6.png](02-during-6.png) | 12.1 s | `before: FILE DROPPED. Page clock since the drop: 0.5 s (it stands still while the page is held)` | `Document opened` |
| [02-during-7.png](02-during-7.png) | 16.1 s | `before: FILE DROPPED. Page clock since the drop: 0.5 s (it stands still while the page is held)` | `Document opened` |
| [02-during-8.png](02-during-8.png) | 19.9 s | `before: FILE DROPPED. Page clock since the drop: 0.5 s (it stands still while the page is held)` | `Document opened` |
| [03-after-open.png](03-after-open.png) | 23.3 s | `before: FILE DROPPED. Page clock since the drop: 23.4 s (it stands still while the page is held)` | `Document opened` |

The original chain was visible in all eight during captures. The first recovered frame showed the large drawing in the `evidence-big.rsk` tab. The banner advanced to `23.5 s` in the following frame.

## Anything I could not do

None.

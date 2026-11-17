# ReShiki UI verification

Verified the `after` build at `http://localhost:8192/examples/evidence.html?auto=150&build=after&residues=100`. The PNGs show the full Chrome window at 3360 × 2040 pixels.

Capture times are relative to the first screenshot that showed `FILE DROPPED`. The banner and status columns transcribe the text visible in each screenshot.

| Screenshot | Capture time (s) | Banner text | Bottom-left status line |
| --- | ---: | --- | --- |
| [01-before-drop.png](01-before-drop.png) | −11.75 | after: dropping a large drawing in 11 s | Document opened |
| [02-during-1.png](02-during-1.png) | 0.00 | after: FILE DROPPED. Page clock since the drop: 0.0 s (it stands still while the page is held) | Document opened |
| [02-during-2.png](02-during-2.png) | 0.11 | after: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held) | Opening… |
| [02-during-3.png](02-during-3.png) | 3.00 | after: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held) | Opening… |
| [02-during-4.png](02-during-4.png) | 5.88 | after: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held) | Opening… |
| [02-during-5.png](02-during-5.png) | 8.88 | after: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held) | Opening… |
| [02-during-6.png](02-during-6.png) | 11.89 | after: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held) | Opening… |
| [02-during-7.png](02-during-7.png) | 13.68 | after: FILE DROPPED. Page clock since the drop: 0.1 s (it stands still while the page is held) | Opening… |
| [02-during-8.png](02-during-8.png) | 13.87 | after: FILE DROPPED. Page clock since the drop: 9.8 s (it stands still while the page is held) | Document opened |
| [02-during-9.png](02-during-9.png) | 19.84 | after: FILE DROPPED. Page clock since the drop: 9.8 s (it stands still while the page is held) | Document opened |
| [03-after-open.png](03-after-open.png) | 24.08 | after: FILE DROPPED. Page clock since the drop: 24.1 s (it stands still while the page is held) | Document opened |

The page clock displayed `0.1 s` across six captures while the editor showed `Opening…`. The large drawing was visible by the 13.87 s capture, with the banner at `9.8 s`. The banner still showed `9.8 s` at the 19.84 s capture. After the final PNG was captured at `24.1 s`, the next check showed `24.4 s`, confirming that the clock was advancing.

## Incomplete items

None.

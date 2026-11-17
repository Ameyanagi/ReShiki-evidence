# ReShiki Probe Before timing run

Completed Part A and Part B against the local mock GitHub. `marks.txt` contains all 16 requested marks in order, one per label. The probe window and menu-bar name were verified on both launches, and the probe exited after both quit commands.

| Mark | Result | Exact path and observations |
| --- | --- | --- |
| `A0-launch` | Succeeded | Launched the specified bundle with `open -n`. In the probe window, used bottom-left **GitHub → Sign in…**. The mock completed device approval, the dialog closed, and the status showed **Signed in as @octo-test**. Waited another 5 seconds. |
| `A1-picker-open` | Succeeded | Bottom-left **GitHub → Open from GitHub…**. The picker and repository sidebar were available after 6 seconds. |
| `A2-choose-repo` | Succeeded | Clicked **group-drawings** in the picker’s left sidebar and waited 6 seconds. The pane was in Tree view. Clicked the left **Tiles** button at the end of the folder path line without a mark and waited 4 seconds. |
| `A3-open-routes` | Succeeded | Double-clicked the **routes** folder tile. After 8 seconds, confirmed six drawing tiles and their previews. |
| `A4-bigfolder-open` | Succeeded | Focused **Search or paste a GitHub link**, selected all with Command+A, and pasted the supplied local screening URL. Pressed Return after the mark and waited 10 seconds. The folder displayed `hit-NNN.mol` tiles. |
| `A5-open-drawing` | Succeeded with a tab difference | Before the mark, clicked **group-drawings** in the left sidebar, double-clicked **routes**, and waited 6 seconds. After the mark, double-clicked **drawing-01** and waited 6 seconds. The picker closed and `drawing-01.rsk` opened with the **GD** repository badge. The app reused the blank **Untitled** tab. |
| `A6-history` | Succeeded | Clicked the **History** clock immediately to the right of the inspector tabs. After 10 seconds, **This computer** showed “No saves since the last send,” and **GitHub** showed 12 versions. |
| `A9-quit` | Succeeded | Ran the specified path-scoped `pkill -f`, waited 5 seconds, and verified the probe had exited. |
| `B0-launch` | Succeeded | Relaunched the same bundle with `open -n`. Verified the probe window, waited 5 seconds, and used bottom-left **GitHub → Sign in…**. The mock completed device approval, the dialog closed, and the status showed **Signed in as @octo-test**. Waited another 5 seconds. |
| `B1-picker-open` | Succeeded | Bottom-left **GitHub → Open from GitHub…**. The picker and repository sidebar were available after 6 seconds. |
| `B2-choose-repo` | Succeeded | Clicked **group-drawings** in the picker’s left sidebar and waited 6 seconds. **Tiles** was already selected. |
| `B3-open-routes` | Succeeded | Double-clicked the **routes** folder tile. After 8 seconds, confirmed the six drawing tiles. |
| `B4-bigfolder-open` | Succeeded | Focused **Search or paste a GitHub link**, selected all with Command+A, and pasted the same URL. Pressed Return after the mark and waited 10 seconds. The folder displayed `hit-NNN.mol` tiles. |
| `B5-open-drawing` | Succeeded | Before the mark, clicked **group-drawings** in the left sidebar, double-clicked **routes**, and waited 6 seconds. After the mark, double-clicked **drawing-01** and waited 6 seconds. The picker closed and `drawing-01.rsk` again opened in the former **Untitled** tab with the **GD** badge. |
| `B6-history` | Succeeded | Clicked the **History** clock immediately to the right of the inspector tabs. After 10 seconds, **This computer** showed “No saves since the last send,” and **GitHub** showed 12 versions. |
| `99-end` | Succeeded | Ran the specified path-scoped `pkill -f` and verified the probe had exited. |

All requested actions were performed. Both sign-ins completed inside the probe, and no browser was opened. No screenshots were saved to the artifact directory.

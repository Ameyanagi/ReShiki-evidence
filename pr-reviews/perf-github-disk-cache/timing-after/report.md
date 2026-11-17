# ReShiki Probe After timing run

Both passes completed. All 16 labels appear once and in order in `marks.txt`. The probe exited after each pass.

| Mark | Result and UI path | Mark to app event |
| --- | --- | ---: |
| `A0-launch` | Succeeded. Launched the specified bundle with `open -n` and verified the **ReShiki Probe After** window. Used status-bar **GitHub → Sign in…** and waited for the mock to sign in as `@octo-test`. The device dialog closed on its own. | |
| `A1-picker-open` | Succeeded. Status-bar **GitHub → Open from GitHub…** opened the picker. | 2.71 s |
| `A2-choose-repo` | Succeeded. Clicked **group-drawings** in the left sidebar. The files pane was in Tree view. After six seconds, clicked **Tiles** at the right end of the folder path and waited four more seconds. | 2.99 s |
| `A3-open-routes` | Succeeded. Double-clicked the **routes** tile. The folder showed six drawing tiles, and the probe logged six thumbnail results. | 3.65 s |
| `A4-bigfolder-open` | Succeeded. Pressed Return in **Search or paste a GitHub link** after entering the supplied link. The picker opened **ligands / screening** and showed `hit-NNN.mol` tiles. | 2.66 s |
| `A5-open-drawing` | Opened the drawing with a UI difference. Double-clicked **drawing-01**. The picker closed and the app showed `drawing-01.rsk` with the **GD** repository badge in the original Untitled tab slot. A separate tab did not appear. | 3.10 s |
| `A6-history` | Succeeded. Clicked the **History** clock immediately after the inspector tabs. The inspector showed **This computer**, with “No saves since the last send,” and **GitHub** with 12 revisions. | 3.01 s |
| `A9-quit` | Succeeded. Ran the specified path-scoped `pkill`. After at least five seconds, confirmed the process and probe window were gone. | |
| `B0-launch` | Succeeded. Relaunched the specified bundle with `open -n`, verified the signed-out probe window, and waited five more seconds. Used status-bar **GitHub → Sign in…** and verified mock sign-in as `@octo-test`. The device dialog closed on its own. | |
| `B1-picker-open` | Succeeded. Status-bar **GitHub → Open from GitHub…** opened the picker. The app loaded the previous repository on open. | 3.39 s |
| `B2-choose-repo` | Succeeded. Clicked **group-drawings** in the left sidebar. **Tiles** was already selected. | 4.04 s |
| `B3-open-routes` | Succeeded. Double-clicked the **routes** tile. The folder showed six drawing tiles, and the probe logged six thumbnail results. | 3.42 s |
| `B4-bigfolder-open` | Succeeded. Pressed Return in **Search or paste a GitHub link** after entering the same link. The `hit-NNN.mol` tiles appeared. | 3.05 s |
| `B5-open-drawing` | Succeeded. Double-clicked **drawing-01**. The picker closed and the drawing appeared in the original Untitled tab slot with the repository badge. | 3.22 s |
| `B6-history` | Succeeded. Clicked the **History** clock immediately after the inspector tabs. The inspector showed 12 GitHub revisions, and the probe log confirmed zero local versions. | 2.70 s |
| `99-end` | Succeeded. Ran the specified path-scoped `pkill` and confirmed the probe process was gone. | |

For both unmarked returns from **screening**, I clicked **group-drawings** in the left sidebar, double-clicked **routes**, and waited six seconds before marking the drawing open. Both sign-ins used the mock’s automatic approval, followed by the five-second wait. No browser was opened.

For each marked UI step, I ran the shell mark and issued the input in the next computer-use call. The offsets above compare `marks.txt` with the corresponding action events in `probe.log` and include the tool handoff. For double-clicks, the offset uses the second selection event. The display-name lookup after the first launch failed, so I checked the running-app list and attached using the running probe’s unique identifier.

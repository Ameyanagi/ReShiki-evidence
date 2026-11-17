# ReShiki Probe Before timing run

All 17 marks completed in order. Each marked UI action followed its shell mark, and the specified settling waits elapsed before the next interaction.

| Mark | Result | UI action and observation |
| --- | --- | --- |
| `00-launch` | Succeeded | Launched the exact probe bundle with `open -n` and verified the window belonged to ReShiki Probe Before. Clicked status-bar GitHub → Sign in…. The mock approved the device code and closed the dialog. The status button showed `@octo-test`. |
| `04a-open-drawing` | Succeeded | Double-clicked the `drawing-01` tile. The picker closed and `drawing-01.rsk` was selected with the `group-drawings` badge. |
| `04b-open-drawing` | Succeeded | Double-clicked the `drawing-06` tile. The picker closed and `drawing-06.rsk` opened in the second GitHub tab. |
| `04c-open-drawing` | Succeeded | Double-clicked the `drawing-11` tile. The picker closed and all three GitHub tabs were open with `drawing-11.rsk` selected. |
| `05a-cmd-s` | Succeeded | Pressed Cmd+S after the first canvas edit. The edited indicator cleared and the GitHub badge showed `1 unsent`. No dialog appeared. |
| `05b-cmd-s` | Succeeded | Pressed Cmd+S after the second canvas edit. The edited indicator cleared and the GitHub badge showed `1 unsent`. No dialog appeared. |
| `05c-cmd-s` | Succeeded | Pressed Cmd+S after the third canvas edit. The edited indicator cleared and the GitHub badge showed `1 unsent`. No dialog appeared. |
| `06a-tab` | Succeeded | Clicked `drawing-01.rsk` in the top tab strip and verified selection. |
| `06b-tab` | Succeeded | Clicked `drawing-06.rsk` in the top tab strip and verified selection. |
| `06c-tab` | Succeeded | Clicked `drawing-11.rsk` in the top tab strip and verified selection. |
| `06d-tab` | Succeeded | Clicked `drawing-01.rsk` in the top tab strip and verified selection. |
| `06e-tab` | Succeeded | Clicked `drawing-11.rsk` in the top tab strip and verified selection. |
| `06f-tab` | Succeeded | Clicked `drawing-06.rsk` in the top tab strip and verified selection. |
| `08a-history` | Succeeded | Clicked the History clock to the right of the inspector tabs on `drawing-01.rsk`. The inspector opened and listed GitHub versions. |
| `08b-history-other` | Succeeded | Clicked `drawing-06.rsk` in the top tab strip. History stayed open and showed `Remote change to routes/drawing-06.rsk`. |
| `08c-history-back` | Succeeded | Clicked `drawing-01.rsk` in the top tab strip. History showed **This computer** with “No saves since the last send” and **GitHub** with drawing-01 versions and previews. |
| `98-codex-done` | Succeeded | Wrote the handoff mark after the last wait. Left the probe running in front with `drawing-01.rsk` selected and History open. |

The initial picker path was status-bar GitHub → Open from GitHub… → `group-drawings` in the left sidebar → Tiles → double-click `routes`. All six drawing tiles were listed after the eight-second wait. Both later opens returned to the repository root. Each time I clicked `group-drawings` in the left sidebar, double-clicked `routes`, and waited four seconds before marking the drawing open.

Before the saves, I selected **Single bond** in the left drawing toolbar because **Select / move** was active. Each of the three single clicks on an empty canvas spot made `drawing-11.rsk` show as edited. I waited two seconds before each save mark and four seconds after each Cmd+S.

Every requested action was completed. No screenshots were saved to the artifact directory.

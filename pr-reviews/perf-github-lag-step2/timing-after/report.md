# ReShiki Probe After timing run

All 17 requested marks appear once in `marks.txt`, in order. I left ReShiki Probe After running in front with `drawing-01.rsk` selected, the History inspector open, and all three GitHub drawing tabs open.

The shell marks and computer-use actions ran as consecutive tool calls. The probe logged the corresponding UI events about 2.1–5.1 seconds after the marks, excluding launch and the completion marker. The table gives approximate offsets from `marks.txt` to the relevant event in `probe.log`. Open offsets use the picker’s working-copy read, save offsets use the keypress, and tab and History offsets use the accessibility action dispatch.

| Mark | Result | Action and observation | Logged offset |
| --- | --- | --- | ---: |
| `00-launch` | Succeeded | Ran the specified `open -n` command after the mark and verified the window and menu-bar name were ReShiki Probe After. Used the bottom-left GitHub button → **Sign in…**. The mock approved the device code, the sign-in panel closed on its own, and the status showed `@octo-test`. No browser or Escape was needed. | — |
| `04a-open-drawing` | Succeeded with a tab difference | Used GitHub → **Open from GitHub…** → **group-drawings** in the left sidebar → **Tiles**, then double-clicked **routes**. Waited 8 seconds and verified all six drawing tiles were listed. The probe logged six loaded thumbnails before the mark. Double-clicked **drawing-01** and waited 6 seconds. The picker closed, and the tab strip showed the repository badge. The drawing replaced the initial empty Untitled tab. | 4.2 s |
| `04b-open-drawing` | Succeeded | GitHub → **Open from GitHub…** reopened at the **group-drawings** root. Double-clicked **routes** and waited 4 seconds. After the mark, double-clicked **drawing-06** and waited 6 seconds. The picker closed and the new GitHub tab was selected. | 3.5 s |
| `04c-open-drawing` | Succeeded | Reopened through GitHub → **Open from GitHub…** and returned to **routes** from the **group-drawings** root. Waited 4 seconds. After the mark, double-clicked **drawing-11** and waited 6 seconds. The picker closed, and drawing-11 was selected with three GitHub tabs open. | 3.6 s |
| `05a-cmd-s` | Succeeded | The active tool was **Select / move**, so I selected **Single bond** in the left toolbar. Clicked empty canvas once, waited 2 seconds, pressed Cmd+S after the mark, and waited 4 seconds. The edited indicator cleared, and the probe logged a local working-copy version save. No dialog appeared. | 3.7 s |
| `05b-cmd-s` | Succeeded | Clicked a second empty spot with **Single bond** active, waited 2 seconds, pressed Cmd+S after the mark, and waited 4 seconds. The edited indicator cleared, and the probe logged a second local version save. No dialog appeared. | 2.2 s |
| `05c-cmd-s` | Succeeded | Clicked a third empty spot with **Single bond** active, waited 2 seconds, pressed Cmd+S after the mark, and waited 4 seconds. The edited indicator cleared, and the probe logged a third local version save. No dialog appeared. Drawing-11 still showed `1 unsent`. | 2.1 s |
| `06a-tab` | Succeeded | Clicked **drawing-01** in the top tab strip and waited 2 seconds. | 5.1 s |
| `06b-tab` | Succeeded | Clicked **drawing-06** in the top tab strip and waited 2 seconds. | 2.4 s |
| `06c-tab` | Succeeded | Clicked **drawing-11** in the top tab strip and waited 2 seconds. | 2.4 s |
| `06d-tab` | Succeeded | Clicked **drawing-01** in the top tab strip and waited 2 seconds. | 2.3 s |
| `06e-tab` | Succeeded | Clicked **drawing-11** in the top tab strip and waited 2 seconds. | 3.2 s |
| `06f-tab` | Succeeded | Clicked **drawing-06** in the top tab strip and waited 2 seconds. | 2.9 s |
| `08a-history` | Succeeded | Clicked **drawing-01** without a mark and waited 2 seconds. After the mark, clicked the **History** clock immediately to the right of the inspector tabs and waited 8 seconds. **This computer** showed “No saves since the last send.” **GitHub** showed the version list with previews. | 4.2 s |
| `08b-history-other` | Succeeded | Clicked **drawing-06** and waited 6 seconds. History stayed open and showed the remote version for `routes/drawing-06.rsk`. | 3.3 s |
| `08c-history-back` | Succeeded | Clicked **drawing-01** and waited 6 seconds. History stayed open and showed drawing-01’s revisions again. | 4.3 s |
| `98-codex-done` | Succeeded | Wrote the final mark and stopped interacting with the app. | — |

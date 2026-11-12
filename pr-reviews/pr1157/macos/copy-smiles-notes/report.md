# ReShiki Copy SMILES → Apple Notes (Google)

Observed on 2026-11-12, around 18:24–18:27 JST, on the supplied macOS 27 Retina Mac. The test flow used computer-use screenshots, clicks, and keyboard input. No repository files were edited.

## Result

Copy SMILES pasted this exact single line of visible text into a new note in the Google account’s **Notes** folder:

```text
Cn1c(=O)c2c(ncn2C)n(C)c1=O
```

The paste was not empty. No drawing, image, or attachment appeared. The note list used the same text as the note title.

## 1. Launch, selection, and Copy SMILES

- Before launching, ran `pgrep -fl 'scratchpad/apps/ReShiki-|scratchpad/bin/'`. It returned no matches (exit 1), so there was no evidence instance to wait for.
- Notes was not running before the test: its process check returned no matches, and the computer-use inventory reported `isRunning: false`.
- Issued the exact prescribed launch command once:

```sh
open -n <scratch>/apps/ReShiki-clip-11df00d5.app --args <scratch>/clip/caffeine.rsk
```

- The command succeeded, but the window initially showed an empty **Untitled** drawing. Opened the supplied `caffeine.rsk` through this evidence instance’s Open dialog. The resulting title was **caffeine.rsk — ReShiki**, and the caffeine structure and label were visible.
- In the final recorded pass, clicked an empty canvas location (400, 500 in the screenshot’s coordinate system), pressed Cmd+A, then Cmd+Option+C. Keyboard input used a 150 ms hold after very short key presses proved unreliable in the file dialog.
- Inspected and saved [01-reshiki-copy-smiles.png](01-reshiki-copy-smiles.png). It shows the selected caffeine structure and label, **14 atoms · 1 object · 15 bonds**, and the status message **Selection copied as SMILES · Review details**.
- Immediately ran the supplied `pbdump` executable with stdout redirected to `pasteboard.txt` as requested.

## Pasteboard dump, verbatim

```text
changeCount 2632
item 0
   0 org.opensmiles.smiles         26  436e3163283d4f29
   1 public.utf8-plain-text         26  436e3163283d4f29
```

The dump reports one pasteboard item with two types, each 26 bytes: `org.opensmiles.smiles` and `public.utf8-plain-text`. It does not print the entire string; the full pasted string is recorded above and visible in screenshot 02.

## 2. Paste into Google Notes

- Opened Apple Notes. The sidebar showed **Google** as the only account and **Notes** as its folder. The folder initially contained **0** notes and displayed **No Notes**.
- Selected that folder, pressed Cmd+N, then Cmd+V without replacing or reformatting the ReShiki clipboard.
- Inspected and saved [02-notes-google-copy-smiles.png](02-notes-google-copy-smiles.png). It shows one note in Google → Notes and the complete string `Cn1c(=O)c2c(ncn2C)n(C)c1=O` in its body. The screenshot timestamp is November 12, 2026, 18:26.

## 3. Delete the test note

- Selected only the newly created test note in the note list and pressed Delete/Backspace.
- Notes asked **Are you sure you want to delete the selected note?** Clicked **Delete**.
- Inspected and saved [03-notes-deleted.png](03-notes-deleted.png). Google → Notes again shows **0**, the window says **No notes**, and the list displays **No Notes**.
- Did not inspect or empty Trash. No other notes were selected, edited, or deleted.

## 4. Quit and cleanup

- Clicked the evidence window and pressed Cmd+Q. No save or Don’t Save dialog appeared.
- A subsequent computer-use accessibility-state query unexpectedly returned a fresh **Untitled — ReShiki** window. A process check found the evidence executable running again. This appears to have been an implicit reopen by the UI tool during the post-quit observation; it was not another explicit `open` command. This is a deviation from the intended launch-only flow.
- Clicked that remaining empty evidence window and pressed Cmd+Q again, without another app-state query afterward. The final prescribed-pattern process check showed no running ReShiki evidence executable. One unrelated shell process matched because its command text contained the literal `pgrep` pattern; it was not an app instance.
- Quit Notes with Cmd+Q because it had not been running initially. A final Notes process check returned no matches (exit 1).

## Deviations and limitations

- The exact launch command did not automatically open caffeine; the supplied file was opened through the evidence instance’s UI instead.
- A preliminary copy/paste/delete pass produced the same text, but its initial click was outside the empty canvas. Repeated the copy/paste/delete flow with a clear empty-canvas click. The three final screenshots and `pasteboard.txt` are from that final pass. Both disposable test notes were deleted, with the folder visibly returning to zero notes after each pass.
- The post-quit UI observation appears to have reopened the evidence app as described above; the remaining instance was then quit and its absence verified by process check.
- No save prompt appeared, so there was no Don’t Save button to choose. No unresolved blocker remains for the observed paste result.
- No sign-in, account creation, or settings changes were performed. No repository files or other user documents were modified. ReShiki was bound through the supplied evidence app’s exact filesystem path, never by app name or bundle ID.

All three final screenshot images were visually inspected before this report was written.

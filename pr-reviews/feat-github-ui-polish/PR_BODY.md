## Summary

GitHub UI polish and repository identity, stacked on #1199 (`feat/github-sync`). It follows the owner's decisions of 2026-11-16 (items 1–25, 33, 36, 37, 39, 41–53 of the GitHub UI decisions; items 26–32, 34, 35, 38 and 40 are the next PR, "Open shared GitHub repositories by link").

- **Which repository, at a glance.** Each repository keeps one of six colors, chosen on first sight by repository id and kept in `<data>/github/prefs.json`; right-click a GitHub tab → **Color** to change it. GitHub tabs carry a badge with the repository's initials (**LN** for lab-notes; owner initials when two open repositories would look the same), the tab in front is underlined in that color, the window title reads **ring.rsk — lab-notes — ReShiki**, and its accessible name is "ring.rsk, lab-notes, 1 unsent" (or "this computer").
- **The status chip says what is left.** **● lab-notes / scheme · 1 unsent [Send]**, **✓** when everything is sent, an amber **Review** for a drawing changed on GitHub, **· Sending…**, **· not sent yet** for a drawing GitHub has never had. The name opens the picker in that folder; the state opens History. **Send** opens a small popover above the chip with the message selected: type over it, Enter sends, Esc closes.
- **Sign-in without an account dialog.** **Sign in…** shows the code at once (large; click it to copy it again), the dialog closes by itself after approval with the status **Signed in as @login**, and what started the sign-in goes on (the picker comes back; Send sends). The GitHub menu shows what applies now (**Open from GitHub…**, **Send 1 drawing** / **Send to GitHub…** / greyed **Nothing to send**, **History**), then **@login**, **Add repositories… ↗**, **Sign out**. The cloud button has a dot while anything is unsent and the account's initial while signed in.
- **One picker for Open and Send.** Repositories left (tinted tiles, dot + count for unsent or conflicts, a small lock for private, the last used first, **+ New repository** last), folders and drawings right, newest first with "@author · time", **+ New drawing** and **+ New folder** first. Double-click, Enter or **Open**; Backspace goes up; the breadcrumb's parents go back. Signed out it shows the repositories known here, greyed, and **Sign in…**; with none reachable, **No repositories yet** and **Choose repositories ↗**.
- **A drawing changed on GitHub is a question, not an error.** The status is amber (**Not sent · ring.rsk changed on GitHub**). The dialog shows **GitHub · @alice · 14:02 · message** and **Yours · saved 14:10**, each drawing with what differs painted in ReShiki's own atom and bond highlight (on copies), **Keep GitHub's** under GitHub's and **Keep mine** under yours, then **Later** and **Keep both** (tooltip "Yours becomes ring (2).rsk"); Enter does nothing. **Kept GitHub's · ⌘Z brings yours back**; **Keep both** also opens GitHub's version in a tab next to yours.
- **History** replaces Versions: a clock tab after Export in the inspector, only for GitHub drawings, with **This computer** and **GitHub** groups, day headings, "@author · 14:02" rows and **Compare** · **Open** · **Restore** on one line. Compare shows "Add an ethyl group · @octo-test · 23:02" beside **Now**, with **Restore this** and **Close**.
- **Smaller things.** The command palette lists only the GitHub rows that apply, and a whole word such as `history`, `versions`, `send` or `repo` puts them first. Closing asks **Send** / **Later** with "Sends 3 drawings in lab-notes." when others go too. Opening a drawing takes over an untouched Untitled tab, and a repository's new tab opens after its last tab. Inactive tabs have a faint outline. The lone green autosave dot is gone. Dark-theme mint buttons use dark ink. About's unselected channel is an outline. The star card and About say plainly what Star does: signed in, **★ Star on GitHub** with "Stars ReShiki on GitHub as @login." (status after: "Starred ReShiki on GitHub as @login. Thank you!"); signed out, **★ Star on GitHub ↗** with "Opens GitHub in your browser."; About reads **★ Star on GitHub** (tooltip "Stars ReShiki on GitHub as @login"), **★ Starred on GitHub** or **★ Star on GitHub ↗**. The card never shows under a GitHub dialog.

Desktop only, as before. Docs: `docs/github.md`, release note `docs/changes/unreleased/feat-github-ui-polish.md`.

## Why it matters

The owner tried #1199 on real GitHub and in screenshots: several repositories looked the same, statuses were worded as errors, the sign-in left an account dialog to close, the picker needed extra clicks for the common cases, and there was no way to make a new drawing or folder in a repository. These changes make the repository visible everywhere a drawing appears, put controls in the order they are used and drop words that did not help.

## Approach

- **Identity** is `src/app/github/identity.rs`: six hues per theme (checked by a test: monogram ≥ 4.5:1 on the badge, badge ≥ 3:1 on the tab strip in both themes), FNV-1a of the lowercase `owner/repo` for the first choice, the next hue no other kept repository uses, and writes that carry a sequence number so a late write never rolls a newer choice back.
- **The picker** keeps one component for Open and Send (`src/app/github/picker.rs`). Each drawing's last commit is one `commits?path=…` request (its first page); drawings show once all are known, so nothing moves under the pointer. Listings, downloads and repository creation have separate request numbers, so one never strands another. A new drawing is an empty working copy with no base, so the existing Send makes it a new file; a new folder exists only in the picker until a drawing in it is sent.
- **Send popover**: the draft stays `Dialog::Send`, so the existing modal gate still owns input; it is drawn by the status chip (or as a small dialog in the theme editor, which has no status bar).
- **Keys**: a modal's keys that no widget took (Enter, Backspace) now reach the picker through a second hook in `file_shortcuts.rs`, so the search and name fields keep their own Backspace and Enter.
- **Compare** paints changed atoms and bonds with the persistent highlight on copies made for the compare (a collapsed label's own paint too), and fills changed text and graphics softly; the drawings are untouched.
- No new top-level `Message`; GitHub actions stay under `Message::GitHub`, which `results.rs` already classifies.

Not done here, for the next pass: item 50's avatar **image** (the button shows the account's initial instead; fetching `avatar_url` needs an unauthenticated image download and a cache).

## Evidence

Real app, macOS arm64 debug builds, window 1280 × 852 pt, against the **local mock GitHub** (`src/github/mock.rs`, served with `RESHIKI_GITHUB_CLIENT_ID=mock` and the API/web overrides, a pass-through holding the code approval), each run with a fresh `RESHIKI_DATA_DIR`, driven by Codex computer use, each image a capture of the ReShiki window only. The mock's user is `@octo-test` with private repositories `lab-notes`, `reaction-notes` and `spectra`; `@alice` makes the changes on GitHub.

- **Before**: `feat/github-sync`. Images from #1199's evidence (build `5d96de06d`, and `27dcbb238` for the "fixes" ones), plus `extra-*` captured for this PR from `27dcbb238`, plus `walk-*` from the owner's walkthrough of `feat/github-sync` on real GitHub.
- **After**: this branch. `after/light-01…35` from `92cfe8eb6`; star and About from `3e0bb7b5b`; dark from `3e0bb7b5b` (one tooltip from `b667bef55`). The later commits change only the star card's visibility and wording and wrap the tiles' second line; the clipped tile line visible in `after/light-18` is what that wrap fixes.

### Sign in (items 6, 41, 43)

| Before | After |
| --- | --- |
| <img src="before/light-02-account-signed-out.png" width="420"><br>GitHub account… → a dialog with "Sign in with GitHub". | <img src="after/light-02-picker-signed-out.png" width="420"><br>Open from GitHub while signed out: the picker itself, with **Sign in…** (a fresh data folder knows no repositories, so the list is empty). |
| <img src="before/light-03-sign-in-code.png" width="420"><br>The code dialog: Open GitHub ↗ / Copy code / Cancel, "Waiting for GitHub…", and Close. | <img src="after/light-03-sign-in-code.png" width="420"><br>Sized to its content: the code large (click it to copy again), "Copied. Paste it on GitHub.", **Open GitHub ↗** / **Cancel**. |
| <img src="before/light-04-signed-in.png" width="420"><br>After approval the account dialog stays open ("Signed in as @octo-test", Choose repositories ↗, Sign out, Close). | <img src="after/light-04-picker.png" width="420"><br>After approval the dialog closed by itself, the status says **Signed in as @octo-test**, and the picker came back (lab-notes chosen by a click here: with three repositories and none used yet, nothing is chosen for you). |

### GitHub menu and the cloud button (items 7, 14, 44, 50)

| Before | After |
| --- | --- |
| <img src="before/light-01-github-menu.png" width="420"><br>Signed out: Open from GitHub…, Send to GitHub, Versions (disabled), GitHub account…. | <img src="after/light-01-menu-signed-out.png" width="420"><br>Signed out on an Untitled drawing: **Open from GitHub…**, **Send to GitHub…**, line, **Sign in…**. |
| <img src="before/extra-light-08-menu.png" width="420"><br>Signed in, one save unsent: the same four rows. | <img src="after/light-08-menu.png" width="420"><br>**Open from GitHub…**, **Send 1 drawing**, **History**, line, **@octo-test** (grey), **Add repositories… ↗**, **Sign out**. The cloud has the unsent dot and the account's initial. |
| <img src="before/walk-01-idle.png" width="420"><br>Owner's walkthrough on real GitHub: nothing on the cloud says whether you are signed in. | <img src="after/light-09d-cloud-tooltip.png" width="420"><br>Tooltip and accessible name **GitHub · Signed in as @octo-test · Not everything is sent**. |

### Open from GitHub (items 4, 36, 37, 39, 42, 45, 46, 47)

| Before | After |
| --- | --- |
| <img src="before/light-05-open-picker.png" width="420"><br>owner/repo rows, a filled folder tile, "ring.rsk", Cancel / Open, "New private repository…" under the list. | <img src="after/light-04-picker.png" width="420"><br>Tinted tiles with initials (**LN**, **RN**, **SP**), the lock as a small trailing glyph, **+ New repository** last; **+ New drawing**, **+ New folder**, a neutral folder tile with the Open icon, "ring" with **@octo-test · Yesterday 23:02**; key hints. |
| <img src="before/light-06-open-picker-folder.png" width="420"><br>"‹ lab-notes / scheme". | <img src="after/light-05-picker-folder.png" width="420"><br>Breadcrumb **lab-notes / scheme** (the muted parent goes back), drawings newest first: furan by **@alice · Today 03:23**, then route. |
| | <img src="after/light-22-new-folder.png" width="420"><br>**+ New folder** "drafts": it opens at once and says **Empty** (it reaches GitHub with the first drawing sent from it). lab-notes shows **● 2**: two drawings unsent. |
| | <img src="after/light-21-new-drawing.png" width="420"><br>**+ New drawing** "esterification" in scheme: an empty tab **esterification.rsk** with the LN badge, placed after the repository's other tab; chip **● lab-notes / scheme · 2 unsent** with Send (ring.rsk is also waiting, so the repository count shows). |

### Which repository, at a glance (items 21–25, 15, 17)

| Before | After |
| --- | --- |
| <img src="before/light-07-opened-on-github.png" width="420"><br>ring.rsk opened: title "ring.rsk — ReShiki", an "Untitled" tab left behind, chip "On GitHub". | <img src="after/light-06-opened.png" width="420"><br>Title **ring.rsk — lab-notes — ReShiki**, the Untitled tab taken over, the **LN** badge, chip **● lab-notes ✓**. |
| <img src="before/extra-light-07-unsent.png" width="420"><br>After Cmd+S: "1 not on GitHub" and Send. | <img src="after/light-07-unsent.png" width="420"><br>**● lab-notes · 1 unsent** with **Send**; the dot on the cloud. No green autosave dot. |
| | <img src="after/light-15-two-repos.png" width="420"><br>Two repositories: route.rsk (**LN**) and ring-opening.rsk (**RN**, underlined in its blue as the tab in front); inactive tabs have a faint outline; title **ring-opening.rsk — reaction-notes — ReShiki**. |
| | <img src="after/light-16-color-menu.png" width="420"><br>Right-click a GitHub tab: **Color** with six named swatches; the current one is checked. |
| | <img src="after/light-17-color-changed.png" width="420"><br>After **Olive**: the RN badge and the chip's dot change; kept in `prefs.json` by repository id. |
| | <img src="after/light-15a-chip-folder.png" width="420"><br>The chip names the folder: **● lab-notes / scheme · 1 unsent** (the repository's count: ring.rsk still waits). |
| | <img src="after/light-15b-picker-at-folder.png" width="420"><br>Clicking the chip's name opens the picker in **lab-notes / scheme**. |

### Send (items 10, 11)

| Before | After |
| --- | --- |
| <img src="before/extra-light-10-send-box.png" width="420"><br>A centered "Send to GitHub" dialog: octo-test/lab-notes, "1 drawing: ring.rsk", the message, Cancel / Send. | <img src="after/light-10-send-popover.png" width="420"><br>A popover above the chip: **[LN] ring.rsk → lab-notes**, the message selected (type over it), **Send**; Enter sends, Esc closes. |
| <img src="before/light-10-sent.png" width="420"><br>"On GitHub", "Sent to GitHub". | <img src="after/light-11-sent.png" width="420"><br>**● lab-notes ✓**, "Sent to GitHub"; the cloud's dot is gone. |
| <img src="before/light-14-save-to-github.png" width="420"><br>A drawing not on GitHub: "Save to GitHub", a name with ".rsk" inside the field, "Save here". | <img src="after/light-18-send-to.png" width="420"><br>**Send to GitHub**, the same picker (last used repository first), **Name [Untitled] .rsk**, **Send**. |
| <img src="before/light-15-new-repo.png" width="420"><br>"New private repository…" → Name and Create. | <img src="after/light-19-new-repo.png" width="420"><br>**+ New repository** turns into a field "Repository name" with the lock; Enter creates and selects it. |
| <img src="before/light-17-saved-to-new-repo.png" width="420"><br>Saved as first-route: "On GitHub". | <img src="after/light-20-sent-to-new-repo.png" width="420"><br>Sent as first-route: tab **R2 first-route.rsk**, title **first-route.rsk — routes-2026 — ReShiki**, chip **● routes-2026 ✓**. |

### Command palette (items 33, 52)

| Before | After |
| --- | --- |
| <img src="before/extra-light-09-palette.png" width="420"><br>"github": the four fixed rows, GitHub account… first. | <img src="after/light-09-palette.png" width="420"><br>Only what applies, in the menu's order: Open from GitHub…, **Send 1 drawing**, **History**, **Copy GitHub link**, **Open on GitHub ↗**, **Sign out of GitHub**. |
| <img src="before/walk-19-palette-history.png" width="420"><br>Owner's walkthrough: "history" finds Versions only by its description. | <img src="after/light-09b-palette-history.png" width="420"><br>"history": **History** first. |
| <img src="before/walk-26-palette-send.png" width="420"><br>"send": the GitHub row below unrelated matches. | <img src="after/light-09c-palette-send.png" width="420"><br>"send": **Send 1 drawing** first. |
| <img src="before/walk-28-palette-repo.png" width="420"><br>"repo": Triphenylphosphine among the GitHub rows. | <img src="after/light-09-palette.png" width="420"><br>A whole word such as `repo` or `github` puts every GitHub row first (shown for "github"). |

### History (items 8, 9, 49, 48)

| Before | After |
| --- | --- |
| <img src="before/light-11-versions.png" width="420"><br>Versions in place of the inspector: ON THIS MAC / ON GITHUB, large thumbnails, "Compare with current" / Open / Restore (filled). | <img src="after/light-12-versions.png" width="420"><br>**History**, the clock tab after Export: **This computer** ("Saved 03:28:47", seconds because two saves share the minute) and **GitHub** with **Today** / **Yesterday**; the selected row's **Compare** · **Open** · **Restore** on one line, all outline. |
| <img src="before/walk-16-versions-panel.png" width="420"><br>Owner's walkthrough: the separate Versions panel. | <img src="after/light-12-versions.png" width="420"><br>The same content as an inspector tab, only for GitHub drawings. |
| <img src="before/light-12-versions-compare.png" width="420"><br>Boxes under what changed, "Highlighted: different". | <img src="after/light-13-compare.png" width="420"><br>**Add an ethyl group · @octo-test · 03:28** beside **Now**; the two bonds added since are painted with ReShiki's highlight; **Restore this** / **Close**. |

### Closing with saves not on GitHub (item 12)

| Before | After |
| --- | --- |
| <img src="before/light-13-close-unsent.png" width="420"><br>"Send to GitHub" / "Later". | <img src="after/light-14-close-question.png" width="420"><br>**Send** / **Later**, "Saved on this computer only." (ring.rsk is the only unsent drawing; with others it says "Sends 3 drawings in lab-notes."). |

### A drawing changed on GitHub (items 1, 2, 3, 48)

Light images from `92cfe8eb6` (the star card, still open from launch, shows under the dialog there; `b667bef55` hides it while a GitHub dialog is open).

| Before | After |
| --- | --- |
| <img src="before/light-20-conflict-compare.png" width="420"><br>"GitHub's" / "Yours", boxes, "Highlighted: different", three buttons in a row and the "Keep both: yours becomes…" footnote. | <img src="after/light-30-conflict.png" width="420"><br>**GitHub · @alice · 03:39 · Swap in a pyridine N** and **Yours · saved 03:39**; the N and the new bond painted on both copies; **Keep GitHub's** under GitHub's, **Keep mine** under yours, **Later** and **Keep both**. Enter did nothing. |
| <img src="before/light-41-not-sent.png" width="420"><br>"Not sent · “ring.rsk” changed on GitHub" in red; "1 conflict" / Review. | <img src="after/light-32-review-chip.png" width="420"><br>**Not sent · ring.rsk changed on GitHub** in amber; chip **● lab-notes ·** with an amber **Review**. |
| <img src="before/light-24-kept-github.png" width="420"><br>"Kept GitHub’s". | <img src="after/light-33-kept-github.png" width="420"><br>**Kept GitHub’s · ⌘Z brings yours back** (one ⌘Z did). |
| <img src="before/light-42-kept-mine-sent.png" width="420"><br>"Kept yours · sent". | <img src="after/light-34-kept-mine.png" width="420"><br>**Kept yours · sent**, **● lab-notes ✓**. |
| <img src="before/light-43-kept-both-sent.png" width="420"><br>The tab became ring (2).rsk; GitHub's version only in the picker. | <img src="after/light-35-kept-both.png" width="420"><br>**Kept both · yours is ring (2).rsk · sent**, and GitHub's **ring.rsk** opened in a tab next to yours. |

### Star card and About (items 13, 53, 19)

From `3e0bb7b5b`.

| Before | After |
| --- | --- |
| <img src="before/light-30-star-card.png" width="420"><br>"Enjoying ReShiki?", a long body, Not now / Star on GitHub; nothing says whose star or whether a browser opens. | <img src="after/light-40-star-signed-out.png" width="420"><br>Signed out: **Like ReShiki?**, "A star on GitHub helps other chemists find it.", **Not now** / **★ Star on GitHub ↗**, and **Opens GitHub in your browser.** |
| | <img src="after/light-41-star-signed-in.png" width="420"><br>Signed in (the card stayed open through the sign-in, hidden while its dialog showed): **★ Star on GitHub** and **Stars ReShiki on GitHub as @octo-test.** |
| <img src="before/light-51-about-before-star.png" width="420"><br>About, signed in: "Star ReShiki on GitHub". | <img src="after/light-43-about-signed-in.png" width="420"><br>About, signed in: **★ Star on GitHub** (tooltip "Stars ReShiki on GitHub as @octo-test"); the unselected **Nightly** is an outline. Signed out it reads **★ Star on GitHub ↗** (<a href="after/light-42-about-signed-out.png">screenshot</a>). |
| <img src="before/light-31-starred.png" width="420"><br>"Starred on GitHub. Thank you!". | <img src="after/light-45-starred.png" width="420"><br>One click, no browser: **Starred ReShiki on GitHub as @octo-test. Thank you!** |
| <img src="before/light-32-about-starred.png" width="420"><br>"★ Starred". | <img src="after/light-46-about-starred.png" width="420"><br>**★ Starred on GitHub**. |

### Dark interface (item 18 and the screens above)

From `3e0bb7b5b` (the tooltip image from `b667bef55`).

| Before | After |
| --- | --- |
| <img src="before/dark-03-sign-in-code.png" width="420"><br>Dark code dialog. | <img src="after/dark-03-sign-in-code.png" width="420"><br>The compact code dialog; **Open GitHub ↗** in mint with dark ink. |
| <img src="before/dark-05-open-picker.png" width="420"><br>Dark picker. | <img src="after/dark-04-picker.png" width="420"><br>Tinted repository tiles in the dark palette, the folder icon tile, the disabled **Open** visibly faded. |
| <img src="before/dark-08-saved-not-on-github.png" width="420"><br>"1 not on GitHub" / Send. | <img src="after/dark-07-unsent.png" width="420"><br>**● lab-notes · 1 unsent** / **Send**, the LN badge, the cloud's dot. |
| | <img src="after/dark-08-menu.png" width="420"><br>The menu, dark. |
| <img src="before/dark-09-send-box.png" width="420"><br>The Send dialog, dark. | <img src="after/dark-10-send-popover.png" width="420"><br>The Send popover, dark; **Send** with dark ink. |
| | <img src="after/dark-11-sent.png" width="420"><br>**● lab-notes ✓**, "Sent to GitHub". |
| <img src="before/dark-11-versions.png" width="420"><br>Versions, dark. | <img src="after/dark-12-versions.png" width="420"><br>History, dark. |
| | <img src="after/dark-13-compare.png" width="420"><br>Compare, dark: the drawings keep their white page; the new bond is painted. |
| <img src="before/dark-20-conflict-compare.png" width="420"><br>Conflict, dark. | <img src="after/dark-30-conflict.png" width="420"><br>Conflict, dark: amber status behind, both sides painted. (The outline on Keep mine is the pointer's hover.) |
| <img src="before/dark-21-conflict-chip.png" width="420"><br>"1 conflict" / Review, dark. | <img src="after/dark-32-review-chip.png" width="420"><br>Amber **Not sent · ring.rsk changed on GitHub** and **Review**; History open on the right with @alice's commit. |
| | <img src="after/dark-31-keep-both-tip.png" width="420"><br>**Keep both**'s tooltip, dark. |
| <img src="before/dark-32-about-signed-in-not-starred.png" width="420"><br>About, dark: Nightly filled grey, white text on mint. | <img src="after/dark-37-about.png" width="420"><br>About, dark: **Nightly** an outline, mint buttons with dark ink, the disabled one faded, **★ Star on GitHub**. |

## Verification

VERIFICATION_TABLE

| Check (macOS arm64, Apple M4) | Result |
| --- | --- |
| `cargo fmt --all --check` (at `3e0bb7b5b`) | passed |
| `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings` | passed |
| `cargo test --locked --no-default-features -p reshiki --lib --bins` | library 466 passed, 12 ignored; app 1666 passed, 186 ignored |
| After the last three commits (`b667bef55`, `3e0bb7b5b`: star card and tile wrap only) | clippy as above passed; `github`, `star_prompt`, `tabs` (with ignored) passed |
| `github`, `accessibility`, `popover`, `context_menu`, `star_prompt`, `tabs`, `updates` with `--include-ignored --test-threads=1` (skipping the mock server) | all passed except four that fail the same way on `feat/github-sync` here: `the_operating_system_store_round_trips` (Keychain over a remote shell), `changed_surfaces_expose_live_controls_and_mask_foreground_backgrounds` (Help node count 5 vs 4), `entries_match_captured_baseline` (needs `RESHIKI_VIEW_PARITY`), `verifies_and_stages_signed_macos_release_without_touching_installed_app` |
| The named ignored tests CI runs on Windows (focus, Help, context menu cascade, shortcut focus, pick list, figure export labels, inspector motion) | passed, except `help_renderer_evidence`, which needs `RESHIKI_HELP_QA_DIR` |
| `scripts/copy_lint.py` from `main` against this tree | no new finding (one fewer than `feat/github-sync`: "ON GITHUB" is gone) |
| `bun fmt --check` on the changed docs | passed |
| Adversarial review (Codex, two passes) | 11 findings, then 10 on the fixes; all fixed except the ones noted under Risk |

New tests: chip states, palette rows that apply, the encoded GitHub link, repository colors (stable, next free hue, chosen color wins, file round trip, late write dropped), monograms and collisions, badge contrast, picker order and last-used choice, signed-out picker and sign-in continuation, new drawing (name taken, no paths) and new folder, the chip's folder walk (including a folder GitHub does not have yet), Keep GitHub's wording, conflict details never reaching another conflict, Send on closing while signed out, History save names and default messages, palette word ranking, tab reuse and placement, window title, compare paint on copies.

`scripts/module_index.py --check` does not apply on this base (it and `docs/modules.md` arrive with `main`'s #1201); `identity.rs` starts with a one-sentence `//!` for it.

## Risk

- **Real GitHub**: only the mock was used. The new calls are one `GET /repos/{owner}/{repo}/commits?path=…` per drawing in an opened folder (a folder of 100 drawings is 100 requests) and the existing ones.
- **Repository-wide count**: the chip's "· 1 unsent" counts the repository, because Send sends the whole repository. An untouched drawing can therefore show "1 unsent" (seen in `after/light-15a`). Logged as a UX note with a proposal.
- **Diff paint replaces a changed atom's own highlight** on the compare copy (decision 48 draws existing highlights under the diff paint, so on a changed atom the diff color wins).
- **Avatar image (item 50)** not done; the initial disc is the fallback the decision allows.
- First sign-in with several repositories and none used yet still shows "Choose a repository." (decision 4 opens only the only or last-used one).

## Changelog

- GitHub drawings show their repository: a colored badge with its initials on each tab, the repository in the window title, and a status bar chip such as **● lab-notes / scheme · 1 unsent** with **Send**. Right-click a tab to change the color. **Send** opens a small box above the chip with the message selected; Enter sends. The GitHub button has a dot while anything is not sent, and its menu shows what applies now, then your account.
- Sign-in shows the code at once and closes by itself, then goes on with what started it. **Open from GitHub…** opens the repository used last, lists drawings newest first with who changed them, and makes a new repository, drawing or folder in place. Signed out, it shows the repositories known on this computer.
- A drawing changed on GitHub is a question, not an error: the status is amber, and GitHub's and yours show side by side with the differences painted in ReShiki's highlight. **Keep both** also opens GitHub's version. **Versions** is now **History**, a clock tab in the inspector that groups saves and commits by day.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any:

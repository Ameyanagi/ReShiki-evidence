## Summary

B1 of three stacked PRs on #1206 (`feat/github-ui-polish`): open other people's GitHub repositories by link. It follows the owner's decisions of 2026-11-16, items 26–30, 32, 34, 35, 38, 40 and 54, the access re-check on window focus, and the behaviours 59, 60 and 61 (61 for `.rsk` old versions). **B2** (item 31, "Newer on GitHub") and **B3** (items 55–58: other file types, Insert, big folders, Tiles/Tree) follow this PR.

- **Links everywhere (26, 35, 40).** The picker's search field reads **Search or paste a GitHub link**. A github.com link to a repository, folder (`tree`), file (`blob`), branch or commit shows one preview row (tile, **ligands / esters / esterification.rsk**, the link in grey, **Enter**); Enter opens it. A link pasted with Cmd+V while no text field has focus, a dropped `.webloc`/`.url` link file, and a link typed into the command palette (one row, **Open from GitHub: ligands/esters**) open the same way.
- **Shared repositories (38, 54).** **+ Add public repository…** (the last row) takes `owner/repo` or a link. A repository opened by link stays in the list as **alice/ligands** with a muted **shared** tag until right-click → **Remove from list**.
- **Signed out (54, 59).** Public repositories open without a token (GitHub's 60 requests an hour). The picker shows names only and **Sign in to see who changed each file and a preview.**; past the limit, **GitHub's limit for signed-out use is reached. Sign in to continue.** with **Sign in…**. Signed in, author/time and previews are asked only for the tiles on screen.
- **Read only (28).** A repository you may not send to shows an eye and **Read only** on its row, an outlined tab badge, and the chip **● ligands / aromatics · Read only · 1 change ▾** with **Save a copy…**, **Copy request for the owner** and **Open on GitHub ↗**. Editing and Cmd+S save on this computer; you are never asked to send. When access appears (on sign-in, or on window focus at most every five minutes), the label goes away and the saves count as unsent.
- **Can't open (29).** A private or wrong link: **Can't open alice/notes** / **Private, or the link is wrong. The owner can add ReShiki.** with **Copy request for the owner** and **Open on GitHub ↗**; the row is not kept.
- **Old versions (27, 60, 61).** A link to another branch or a commit opens that version in its own tab, kept in `<data>/github/<owner>/<repo>/old/<commit>/` and never sent; chip **Old version · Open latest**. Cmd+S there is **Save a copy…** (a repository of yours, or **This computer…**).
- **You (30).** Picker tiles, History rows, and the conflict and compare headers say **You** for the signed-in user's commits.
- **Copy GitHub link (32)** on a GitHub tab's right-click menu, above Color.
- **Palette rows (34)** for every repository and drawing known on this computer (no request): **Open from GitHub: lab-notes/ring** with "octo-test/lab-notes · ring.rsk"; a name that starts with the query ranks first, and for one or two letters they come after the commands.

Desktop only, as before. Docs: `docs/github.md`; release note `docs/changes/unreleased/feat-github-shared-repos.md`.

## Why it matters

The owner wants to "access other people's public repository so that you can take the structure". Until now ReShiki could open only repositories the GitHub App was installed on, and only while signed in; a link from a colleague led nowhere. This makes a link the way in, keeps someone else's repository safe to browse (nothing can be sent there by mistake), and gives a clear way on: save a copy into your own repository, or ask the owner.

## Approach

- **Signed out is a separate client**, `Client::public(ends)` (`src/github/client.rs`): no token is sent, a 401 is `NotSignedIn`, and an expired sign-in never falls back to it, so the existing "signed-out calls never reach GitHub" tests hold. The picker reads through `State::reader()` (the signed-in client, or else the public one); writes still need a sign-in.
- **Links** are parsed once in `src/github/link.rs` (github.com or the configured web host only; owner and repository names checked; repository paths percent-decoded and checked again by `valid_repo_path` before anything touches the disk). A link resolves the repository by name (`GET /repos/{owner}/{repo}`), then reuses the picker's existing walk to a folder or the existing open path for a file. A branch or commit lists and downloads through `GET /repos/…/commits/{ref}`.
- **Read only** is one flag on the repository's `state.json` (`read_only`, written only when true, so older builds read the file unchanged), set from GitHub's `permissions.push`. Send, the close question, the quit question and the unsent dot skip read-only repositories; the working copy and History work as before.
- **Old versions** live outside `files/`, so `workcopy::locate` never sees them and nothing in Send can reach them; `workcopy::locate_old` gives the tab its badge and chip.
- **Shared repositories** are kept in `prefs.json` (`shared`) by id. Signed out, the list is the repositories known here plus the shared ones; someone else's is listed only while shared, so Remove from list removes it.
- **On-screen loading** (59): every tile has one fixed height, so the tiles in view follow from the scroll offset, height and width; the first screenful sorts newest first once its dates are known, and tiles scrolled to later never move the others.
- **Window focus** comes from the app-wide event subscription as `github::Action::Focused`; paste checks the clipboard's text first (a link opens; anything else pastes into the tab Paste was pressed in). No new top-level `Message`.
- The mock (`src/github/mock.rs`) gained `alice/ligands` (public, with a `draft` branch), `alice/notes` (private: 404), anonymous access to public repositories, a signed-out rate limit (`POST /_mock/limit`) and the single-commit endpoint.

Interpretation to confirm: decision 28 says Cmd+S keeps saving locally in a read-only repository, and 61 makes Cmd+S **Save a copy…** for files that cannot be saved in place. Here Cmd+S saves locally for read-only **working copies** (as 28 and the mockup's "1 change" show) and is **Save a copy…** for **old versions** (the `.rsk` tabs that are never sent). B3 applies 61 to the other formats.

Not done here: a link's branch is read as its first folder (`tree/feature/x/...` reads branch `feature`), documented as a limit; a link dragged from a browser's address bar is not received by the window (winit only takes files), so only `.webloc`/`.url` files work by drag.

## Evidence

Real app, macOS arm64 debug builds, window 1280 × 852 pt, against the **local mock GitHub** (`src/github/mock.rs` served with `RESHIKI_GITHUB_CLIENT_ID=mock` and the API/web overrides, behind a pass-through that holds the sign-in approval), each run with a fresh `RESHIKI_DATA_DIR`, driven by Codex computer use; each image is a capture of the ReShiki window only. The mock's user is `@octo-test` (private `lab-notes`, `reaction-notes`, `spectra`); `alice/ligands` is someone else's public repository with a `draft` branch, `alice/notes` is private. Links are typed as `https://github.com/…`; ReShiki reads them against the mock, so nothing reached github.com.

- **Before**: `feat/github-ui-polish` at `a91c257d2`.
- **After**: this branch. `after/light-01…13` from `b04430b9d`; `after/light-11-palette-rows`, `after/light-20…22` and `after/dark-*` from `9e1a59d96` (the head adds only the palette ranking fix to `b04430b9d`).

### A pasted link shows one row (26, 40)

| Before | After |
| --- | --- |
| <img src="before/light-01-link-preview.png" width="420"><br>The field says "Search repositories"; a pasted link filters every repository away and Enter does nothing. | <img src="after/light-01-link-preview.png" width="420"><br>**Search or paste a GitHub link**: one row, **ligands / esters / esterification.rsk**, the link in grey and **Enter**. |
| <img src="before/dark-01-link-preview.png" width="420"><br>Dark, the same. | <img src="after/dark-01-link-preview.png" width="420"><br>Dark. |

### Add public repository and the shared row (38, 54, 28)

| Before | After |
| --- | --- |
| <img src="before/light-02-add-public.png" width="420"><br>The list ends with "+ New repository"; no way to add someone else's repository. | <img src="after/light-02-add-public.png" width="420"><br>**+ Add public repository…** turns into a field; `alice/ligands` typed. |
| | <img src="after/light-03-shared-row.png" width="420"><br>Enter: **alice/ligands** with a muted **shared** tag and an eye **Read only**, no lock (public); its folders and drawing, no **+ New** tiles (nothing can be sent there). Right-click the row for **Remove from list** (tested). |
| | <img src="after/dark-03-shared-row.png" width="420"><br>Dark. |

### Signed out (54, 59)

| Before | After |
| --- | --- |
| <img src="before/light-20-signed-out-picker.png" width="420"><br>Signed out, a fresh data folder: only **Sign in…**; nothing can be opened. | <img src="after/light-20-signed-out-picker.png" width="420"><br>Signed out: **+ Add public repository…** is offered, with **Sign in…** on the right. |
| | <img src="after/light-21-signed-out-names.png" width="420"><br>`https://github.com/alice/ligands` added signed out: names only (no preview, no author), and **Sign in to see who changed each file and a preview.** |
| | <img src="after/light-22-rate-limit.png" width="420"><br>The mock's signed-out limit spent (`POST /_mock/limit {"left":0}`), then a folder opened: **GitHub's limit for signed-out use is reached. Sign in to continue.** and **Sign in…**. |

### A read-only drawing (28)

No equivalent before: a repository the user cannot send to could not be opened at all.

| After | |
| --- | --- |
| <img src="after/light-04-read-only-chip-menu.png" width="420"><br>ligands' benzofuran.rsk, a bond added and Cmd+S: **Document saved**, the tab badge **LI** outlined, the chip **● ligands / aromatics · Read only · 1 change ▾** (no Send) and its menu **Save a copy…**, **Copy request for the owner**, **Open on GitHub ↗**. | <img src="after/dark-04-read-only-chip-menu.png" width="420"><br>Dark. |
| <img src="after/light-05-save-a-copy.png" width="420"><br>**Save a copy…**: the picker titled **Save a copy**, only repositories you may send to (ligands is not listed), **Name [benzofuran] .rsk**, **This computer…**, Cancel, Send. | |

### Can't open (29)

| After | |
| --- | --- |
| <img src="after/light-06-cant-open.png" width="420"><br>`https://github.com/alice/notes` (private): **Can't open alice/notes**, **Private, or the link is wrong. The owner can add ReShiki.**, **Copy request for the owner** (clicked: status **Request copied · Send it to the owner**; the clipboard holds "Please add ReShiki to alice/notes so I can send drawings: …/apps/reshiki/installations/new") and **Open on GitHub ↗**. No row was added. | |

### A branch link: the old version (27, 60, 61, and window paste 26)

| Before | After |
| --- | --- |
| <img src="before/light-07-old-version.png" width="420"><br>`…/blob/draft/esters/esterification.rsk` pasted with Cmd+V on the canvas: **Could not paste: Invalid SMILES at byte 0** (red). | <img src="after/light-07-old-version.png" width="420"><br>The same paste opens the drawing as it is on `draft` in its own tab: outlined badge, title **esterification.rsk — ligands — ReShiki**, chip **● ligands / esters · Old version** with **Open latest**. |
| | <img src="after/light-07b-old-version-save.png" width="420"><br>Cmd+S on the old version: **Save a copy** with **Name [esterification]**; nothing is ever sent from it. |

### You (30)

| Before | After |
| --- | --- |
| <img src="before/light-08-picker-authors.png" width="420"><br>lab-notes / scheme: route by **@octo-test**, the signed-in user. | <img src="after/light-08-picker-authors.png" width="420"><br>route by **You · Yesterday 23:02**; furan by **@alice**. |
| <img src="before/light-09-history-you.png" width="420"><br>History of ring.rsk: **@octo-test · 23:02**. | <img src="after/light-09-history-you.png" width="420"><br>**You · 23:02**. (The mock's commit is 14:02 UTC; the Mac shows Tokyo time.) |

### Copy GitHub link (32)

| Before | After |
| --- | --- |
| <img src="before/light-10-tab-menu.png" width="420"><br>Right-click a GitHub tab: Color only. | <img src="after/light-10-tab-menu.png" width="420"><br>**Copy GitHub link**, a line, then Color. Clicked: **Link copied**; the clipboard holds `…/octo-test/lab-notes/blob/main/ring.rsk`. |

### Command palette (34, 35)

| Before | After |
| --- | --- |
| <img src="before/light-11-palette-rows.png" width="420"><br>`ring` with ring.rsk open from lab-notes: commands only. | <img src="after/light-11-palette-rows.png" width="420"><br>**Open from GitHub: lab-notes/ring** first, with "octo-test/lab-notes · ring.rsk" below the list; read from this computer, no request. With `ri` (two letters) it comes after every command that can run (reported by the run, and tested). |
| <img src="before/dark-11-palette-rows.png" width="420"><br>Dark, `ring`: commands only; the palette has no rows for drawings known on GitHub. | <img src="after/dark-11-palette-rows.png" width="420"><br>Dark, `benzo` with ligands' benzofuran known: **Open from GitHub: ligands/benzofuran** first. |
| <img src="before/light-12-palette-link.png" width="420"><br>A pasted folder link: "Insert structure named “https://github.com/alice/ligands/tree/main/esters”". | <img src="after/light-12-palette-link.png" width="420"><br>One row: **Open from GitHub: ligands/esters**, "alice/ligands · main". |
| | <img src="after/light-13-palette-link-opened.png" width="420"><br>Enter: the picker in **ligands / esters**, alice/ligands selected (shared, Read only). |
| | <img src="after/dark-12-palette-link.png" width="420"><br>Dark. |

Not shown in images (covered by tests): a dropped `.webloc`/`.url` link file, Remove from list, the access re-check clearing Read only, Open latest, palette name collisions.

## Verification

VERIFICATION_TABLE

Commands (macOS arm64, Apple M4, at the head commit): `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`; `cargo clippy -p reshiki-web -p reshiki -p reshiki-web-worker --lib --bin reshiki --target wasm32-unknown-unknown --locked -- -D warnings`; `cargo test --locked --no-default-features -p reshiki --lib --bins`; the renderer tests `cargo test --locked --no-default-features -p reshiki --bin reshiki -- --include-ignored --test-threads=1 --skip manual_`; `uv run --locked python -m unittest discover -s tests -p 'test_*.py'`; `python3 scripts/module_index.py --check`; `python3 scripts/copy_lint.py`; `bun fmt --check` on the changed docs. InChI and naming helpers pointed at the built binary, `RESHIKI_DATA_DIR` and `RESHIKI_HELP_QA_DIR` in temporary folders.

New tests: link parsing (repository, tree, blob, commit, branch, other hosts, bad names); signed-out public listing, private 404 and the signed-out rate limit against the mock; branch and commit downloads; old-version paths and the `read_only` flag round trip; the preview row and Enter; shared row add, list persistence, Send excluding it and Remove from list; Add public repository; signed-out names only and folder navigation; the rate-limit message; Can't open and the request text; read-only Save here, chip menu, Save a copy and This computer; the access re-check (throttle, stale sign-in, sign-in listing); the old-version tab (title, badge, link, never unsent, Cmd+S, Open latest); You; Copy GitHub link; palette rows, name collisions, the link row and ranking; window paste and dropped `.url`/`.webloc` (XML and binary).

After merging `main` (#1206's last fixes), the resolution routes `can_create` (no **+ New** without push) through B1's read-only repositories and old versions, and window focus has one path (`github::Action::Focused`) that both re-lists the picker after **Choose repositories** and re-checks read-only access. A review of the resolution found two more, fixed with tests: **Send to GitHub** with a branch link read names at that branch (it now reads links at the default branch and refuses names read elsewhere), and a read-only drawing in front hid the Send box. Greptile's four findings were fixed with tests that fail without them (Save on a close question for an old version; access given later reaching the open picker; later tile dates ending the first wait; palette rows for repositories with no drawing opened yet), and a follow-up review found that a late download or listing could take access back (access now only widens).

Independent adversarial review (gpt-6.1-sol, two passes before the merge): 15 findings. Fixed: signed-out folders could not open; a link could be cancelled by an older folder walk; access replies from an earlier sign-in; focus re-check only on platforms with native accessibility; Remove from list undone signed out; tile geometry estimate; read-only saves holding a quit open; palette rows with the same name dropped (twice); link files parsed by text search; a weak test; the paste fallback running in another tab; a failed link leaving the previous folder half-loaded. Rejected: two old versions differing only by case at one commit (very unlikely, would need a per-commit index) and branch names with `/` (documented limit).

## Risk

- Paste now reads the clipboard's text first when GitHub is set up; anything that is not a github.com link pastes exactly as before, into the tab Paste was pressed in.
- `state.json` gains `read_only` only for read-only repositories; `prefs.json` gains `shared`. Older builds ignore both.
- Signed-out requests go only to the configured GitHub API, never with a token.
- The picker's newest-first order now applies to the first screenful of a folder; folders bigger than a screen list the rest by name (B3 item 57 reworks big folders).

## Changelog

See `docs/changes/unreleased/feat-github-shared-repos.md`.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

B2 ("Newer on GitHub") and B3 (other file types, Insert, big folders, Tiles/Tree) follow this PR.

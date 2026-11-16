Third of three PRs for GitHub sync, part B ("B3"), built on #1209 (B1, now in main). It covers decisions 55–58, with 59, 61 and 62 from the owner's GitHub UI decisions.

## Why it matters

- Most group repositories hold more than `.rsk` drawings: MOL, SDF, ChemDraw and SMILES files from instruments, colleagues and databases. B1's picker hides them, so a folder of `.mol` files looks **Empty** (see Before).
- Taking one structure from a colleague's file meant downloading it and dragging it in. **Insert** does it in one step, as a paste.
- A 240-file screening folder drew every tile. A deep repository could only be searched one folder at a time, and only by repository name.
- The owner approved a Tree view in an interactive mockup, with a preview pane, keyboard navigation and whole-repository search.

## Approach

- **Every chemistry file (55, 61).** `reshiki::github::format_label`/`listed` give `.mol .sdf .cdxml .cdx .rxn .smi` their labels (MOL, SDF, …). The API listing keeps them, and tiles and rows show the label in the corner of the drawing.
  - Opening one stores it the way B1 stores old versions, under `old/<commit>/`, and reads it with the import reader. The tab is read only (outlined badge; the chip shows **Read only** with Save a copy… / Open on GitHub ↗). It is never sent.
  - ⌘S goes through B1's **Save a copy** picker with the name prefilled as `name.rsk`. **This computer…** also suggests `.rsk` for formats Save cannot write back (`.sdf`, `.rxn`, `.smi`). The original file is untouched.
- **Insert (56).** Insert has three triggers: right-click a tile or row → **Insert into drawing**, ⇧Enter, or the footer's **Insert**.
  - It downloads the blob and reads it with the existing import reader (`import::load`). An SD file is split into records; each becomes a structure, side by side.
  - It then places the result with the existing paste placement (`clipboard.rs` `append_pasted`): one Undo step, selected, beside the drawing when it would cover it.
  - The result goes to the tab Insert was chosen in, and is dropped if that drawing changed meanwhile, as a paste is.
- **Big folders (57).**
  - Tiles show at most 200 files that match the search, with "Showing 200 of 240. Search to find the others."
  - With a repository open, the search field filters its files (the folder in Tiles, the whole repository in Tree), as in the mockup.
  - Newest first is as far as known. Only files on screen are asked for their last change (decision 59: no per-folder bulk fetch). The first screenful sorts newest first and the rest follow by name.
- **Tiles / Tree (58, 62).**
  - Two icon buttons at the right end of the folder-path row. The view is kept in `prefs.json`, so every picker opens in the view used last; Tiles the first time. Send to and Save a copy stay in Tiles.
  - The tree comes from one recursive tree request made when the repository opens (`api::tree_all`), kept until it reopens.
  - Rows: chevron, folder or page icon, name, format label, muted "@author · time" (folders "N items"). Only the rows on screen are built.
  - A 200 px pane shows the selected file's drawing, name, path, "who · time · FORMAT" and "Read only: Open makes a local copy".
  - Keys: ↑↓ move, →/← open/close (only while the search field is empty, so the field keeps its cursor keys), Enter open, ⇧Enter insert, Esc close. The footer hint is as in the mockup.
  - Search keeps matches in the tree with their folders opened.
  - A truncated listing says "Only part of this repository is listed", and its folders are recovered from file paths.
  - **+ New drawing / + New folder** are the last rows. They go to the selected folder and use `Picker::can_create`: not in read-only repositories, without push, at an old version, or when the listing is partial.
- **Signed out (59).** Rows and tiles show names and format labels only. The pane shows no drawing. The existing grey "Sign in to see who changed each file and a preview." stays.
- **Mock (`src/github/mock.rs`).**
  - `seed_formats()` adds `alice/ligands` files of every format across folders, plus `screening/` with 240 MOL files one minute apart.
  - Recursive tree replies are supported, and `Repo::truncated` returns half the listing with `truncated: true`. `octo-test/spectra` uses it in the served mock.
  - B1's tests keep their own seeds.

Rejected:
- A separate tree data path per folder. One recursive request is what decision 62 asks for, and it keeps search whole.
- A new insert placement. The spec asks to reuse paste and import.

## Evidence

Real app on macOS arm64 (Apple M4), debug builds, against the local mock GitHub; nothing touched github.com. Window captures only (`screencapture -l`), scripted GUI runs, fresh data folder per launch. **Before** = base `feat/github-shared-repos` 04bc41b84. **After**: the light and dark runs used this branch at 01f6a737a; the signed-out run used the final head 6e4244131. Two fixes came after 01f6a737a, both from these runs:
- a right-clicked file now asks for its preview (the blank pane in `light-10`);
- a tile's format label shows before its drawing loads and when signed out (seen in the signed-out run).

B1's commits merged since (054ad3801 … 4fca4778c) do not touch these screens.

### Mockup vs. app (Tree view)

<img src="after/compare-mockup-tree.png" width="100%" alt="Approved mockup and the real app's Tree view side by side">

The layout follows the mockup: switch at the right of the path row, rows with chevron, icon, name, format label and right-aligned "@author · time" / "N items", the 200 px preview pane, the footer hint, and Cancel / Insert / Open (Open read-only for a file that opens read only).

### 55 Every chemistry file, with its format

| Before (base) | After |
|---|---|
| <img src="before/light-01b-tiles-bipyridines.png" width="420" alt="Base: bipyridines folder shows Empty"> | <img src="after/light-01-tiles-formats.png" width="420" alt="After: bpy.cdxml, phen.mol, phenol.cdx tiles with CDXML, MOL, CDX labels"> |
| `alice/ligands/bipyridines` holds `bpy.cdxml`, `phen.mol` and `phenol.cdx`: the base shows **Empty**. | Each file shows its drawing, a CDXML / MOL / CDX label, and who changed it. |
| <img src="before/dark-01-tiles-bipyridines.png" width="420" alt="Base dark: Empty"> | <img src="after/dark-01-tiles-formats.png" width="420" alt="After dark: tiles with format labels"> |

### 55 + 61 Open a .mol read only; ⌘S is Save a copy as .rsk

| Opened read only | ⌘S → Save a copy |
|---|---|
| <img src="after/light-07-mol-read-only.png" width="420" alt="phen.mol open with an outlined badge and the chip ligands / bipyridines · Read only"> | <img src="after/light-08-save-a-copy.png" width="420" alt="Save a copy picker with Name phen .rsk, This computer…, Cancel, Send"> |
| <img src="after/dark-07-mol-read-only.png" width="420" alt="Dark: phen.mol read only"> | <img src="after/dark-08-save-a-copy.png" width="420" alt="Dark: Save a copy"> |

The base cannot list or open `phen.mol` at all (Before above). The unit test `a_mol_opens_read_only_and_cmd_s_saves_a_copy_as_rsk` checks the copy is written as `phen.rsk` and the original bytes are unchanged.

### 56 Insert into drawing (one Undo step, placed like a paste)

| Canvas before | Right-click → Insert into drawing |
|---|---|
| <img src="after/light-09-insert-before.png" width="420" alt="ring.rsk with the benzofuran ring only"> | <img src="after/light-10-insert-menu.png" width="420" alt="Tree with dppe.sdf right-clicked and the Insert into drawing menu"> |
| **After Insert** | **After one ⌘Z** |
| <img src="after/light-11-insert-after.png" width="420" alt="The two SDF records inserted beside the ring, selected; status Inserted dppe.sdf"> | <img src="after/light-11b-insert-undo.png" width="420" alt="Both inserted structures gone; the ring remains"> |

`dppe.sdf` has two records (acetophenone and benzene). They land side by side, beside the drawing they would otherwise cover, and are selected. One ⌘Z removes both. The base has no Insert.

### 57 A 200+ folder, newest first, and the filter

| Before (base) | After: top | After: end | After: search `hit-23` |
|---|---|---|---|
| <img src="before/light-02-big-folder.png" width="220" alt="Base: screening shows Empty"> | <img src="after/light-02-big-folder-top.png" width="220" alt="hit-011, hit-010, hit-009… newest first"> | <img src="after/light-02b-big-folder-end.png" width="220" alt="Showing 200 of 240. Search to find the others."> | <img src="after/light-03-big-folder-filter.png" width="220" alt="Only hit-230 to hit-239"> |

In the base, typing in the search field filtered the repository list instead (<a href="before/light-05-search.png">before/light-05-search.png</a>).

### 58 Tree with a folder open and the preview pane; 62 search over the whole repository

| Tree + preview | Search `phen`: matches with their folders opened |
|---|---|
| <img src="after/light-04-tree-preview.png" width="420" alt="Tree of alice/ligands, bipyridines open, phen.mol selected, preview pane"> | <img src="after/light-05-tree-search.png" width="420" alt="Only bipyridines, opened, with phen.mol and phenol.cdx"> |
| <img src="after/dark-04-tree-preview.png" width="420" alt="Dark: tree with preview"> | <img src="after/dark-05-tree-search.png" width="420" alt="Dark: tree search"> |

### 62 Truncated tree; 58 New rows

| `spectra`, listed in part | `lab-notes`: + New drawing / + New folder last |
|---|---|
| <img src="after/light-06-tree-truncated.png" width="420" alt="Folders ir, nmr, raman and Only part of this repository is listed; no New rows"> | <img src="after/light-06b-tree-new-rows.png" width="420" alt="scheme, ring.rsk, then + New drawing and + New folder"> |

Base for `spectra`: <a href="before/light-06-spectra.png">before/light-06-spectra.png</a> (tiles show the folders, and its `.mol` files nowhere).

### 59 Signed out: names and format labels only

| Before (base, signed out) | After: tiles | After: tree |
|---|---|---|
| <img src="before/light-out-01-tiles-signed-out.png" width="280" alt="Base signed out: folders only"> | <img src="after/light-out-01-tiles-signed-out.png" width="280" alt="Signed out: names and labels, no drawings or authors"> | <img src="after/light-out-02-tree-signed-out.png" width="280" alt="Signed out tree: names and labels only, pane without drawing"> |

Other base captures: <a href="before/light-01-tiles-top.png">before/light-01-tiles-top.png</a>.

## Verification

VERIFICATION_TABLE

Run on macOS arm64 (Apple M4) at 6e4244131. The head 0d4403857 only merges `main` after #1209 landed, and its tree is identical (`13d92652`):
- `cargo fmt --all --check`
- `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`
- wasm32 clippy (`-p reshiki-web -p reshiki -p reshiki-web-worker --lib --bin reshiki --target wasm32-unknown-unknown`)
- `cargo test --locked --no-default-features -p reshiki --lib --bins`: 482 lib + 1780 bin pass
- renderer tests (`--bin reshiki -- --include-ignored --test-threads=1 --skip manual_`): 1932 pass
- `uv run --locked python -m unittest discover -s tests -p 'test_*.py'`: 264 OK
- `scripts/module_index.py --check`, `scripts/copy_lint.py`, `bun fmt --check` on the docs, `scripts/check_docs_tree.mjs`, `assemble_changelog.py --check`

New tests:
- `src/app/github/tests/files.rs` (16 tests):
  - labels and listing;
  - a `.mol` opening read only, then ⌘S to a `.rsk` copy with the original untouched;
  - This computer… naming;
  - Insert as one Undo step for `.mol` and a two-record `.sdf`, and Insert landing in the tab it was chosen for;
  - the 200 cap, newest first and the filter;
  - folder tiles showing once their dates are known;
  - Tree expand/collapse, keys and Enter/Open;
  - whole-repository search with folders opened;
  - the truncated tree;
  - a late or failed whole listing;
  - the remembered view;
  - New rows needing push and the default branch;
  - signed-out names only;
  - only the rows on screen asked for;
  - tree keys leaving name fields alone.
- `src/github/tests/api.rs`: `a_repository_reads_whole_with_every_chemistry_file`, which covers the recursive listing, every format and truncation against the mock.

Review: an independent adversarial review (read-only) found 12 issues. Eleven are fixed:
- Insert reachable from Send;
- files hidden in subfolders after B1's newer wait logic;
- Insert into a tab switched away from;
- a late or failed whole listing;
- dropped import warnings;
- tree arrows stealing name-field cursor keys;
- a search-hidden selection still acting;
- SDF previews reading every record;
- per-record copies;
- Open on a tree folder.

A second pass found two more, both fixed (a listing error kept in either view; a tree click ends a half-typed name). One finding was kept on purpose: with a repository open, the search filters its files rather than the repository list, as the approved mockup does. The repository list stays clickable.

## Risk

- **Search behaviour change (B1):** while a repository is open, typing no longer filters the repository list; it filters files (decision 57 and the mockup). Pick another repository by clicking it. Links pasted in the field work as before.
- **"Newest first" in big folders** is newest first among the files on screen; decision 59 rules out asking GitHub about every file. The rest follow by name; the search reaches all 240.
- **`.sdf` is not added to File › Open**: it opens and inserts from GitHub, and drops/Insert from disk now take every record. File › Open still refuses `.sdf` as before.
- The tree's recursive request is one more call per repository opening; signed-out users have 60 an hour.
- A chemistry file opened from GitHub gets the engine's default (light) canvas, as **File › Open** of a `.mol` does, even when new drawings are dark.
- The read-only chip, tab hint and Send row now say **Read only** instead of **Old version** for a chemistry file that is not a drawing. These are small touches to the status chip, which B2 also edits; expect a trivial merge there.

## Changelog

`docs/changes/unreleased/feat-github-files-tree.md` (Changes). `docs/github.md` is updated: "Every chemistry file, and Insert", "Tiles or Tree", limits and implementation notes.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none. The mock reuses existing repository fixtures (`tests/fixtures/…`).

## Why it matters

An update left files in two places, and nothing ever removed them:

- the last check's result was `update-cache.json` (or
  `update-cache-nightly.json`) loose in the data folder;
- each update made a hidden `.reshiki-update-XXXXXX` folder **beside the app**
  (in `/Applications`, or next to the extracted Linux folder), downloaded and
  unpacked there, and after installing kept it for good: the archive, the
  previous version of the app, the helper script and its log. Every update
  added another one.

The owner decided on 2026-11-17 that all update files live in one folder,
`updates/` in the data folder, with a subfolder per version, pruned by
default. Uninstalling stays "delete the app and `~/.reshiki`".

## Approach

**One folder.** `reshiki_io::compatibility::updates_directory()` is
`data_directory_location()` + `updates`: `~/.reshiki/updates/` on macOS and
Linux, `%LOCALAPPDATA%\reshiki\ReShiki\data\updates\` on Windows, and inside
`RESHIKI_DATA_DIR` when that is set. It holds:

| Path                          | What                                                                 |
| ----------------------------- | -------------------------------------------------------------------- |
| `stable.json`, `nightly.json` | The last check per channel (were `update-cache*.json`).               |
| `<version>/`                  | `SHA256SUMS`, the downloaded archive and the verified, unpacked app. |
| `<version>/pid`               | The processes using that folder (see below).                         |

The old check files are not migrated: startup deletes them and the next check
writes the new one. That costs one extra request to GitHub, once.

**Download and verify there; swap by rename beside the app.** `prepare()`
downloads into `updates/<version>/` and verifies and unpacks there, exactly as
it did in the temp folder (checksum; on macOS the disk image's and the app's
signature, Gatekeeper and the version; on Linux the archive listing and
package contents; on Windows the publisher). At restart:

- **Updates folder on the app's volume** (the usual case): the helper works in
  `updates/<version>/`. It renames the running app into that folder and the
  new app into place, as before.
- **Another volume** (a data folder on another disk through
  `RESHIKI_DATA_DIR`, an app on an external disk, or two mounts of one disk):
  the verified app is first copied (`cp -a`) into a hidden
  `.reshiki-update-<version>` beside the app, and the helper works there, so
  the swap is still two renames on one volume. Which case applies is found by
  renaming an empty file from the update's folder to beside the app, not by
  comparing device numbers, which two bind mounts of one disk share.
- The digest of the whole payload (and on macOS the bundle's signature) is
  checked again **on what the helper installs, where it installs it from**:
  on the copy in the cross-volume case. A copy that differs installs nothing
  and is removed.
- Windows is unchanged in kind: the helper runs the verified installer, now
  from `updates\<version>\`. Nothing is renamed there, so there is no
  cross-volume case.
- `prepare()` still refuses before downloading when the folder beside the app
  cannot be written (same message as before).

**Pruned by default.**

- After a successful install the helper removes its stage: the archive, the
  previous app and its own files.
- After a failed install the helper puts the previous app back, as before, and
  then removes the stage, but only once nothing of the previous app is left in
  it (`[ -e previous.app ] ||` on macOS; `rmdir previous &&` on Linux, which
  fails while a file is still there).
- A download that fails, or an update given up before restart (channel
  switched), removes its version folder at once.
- **Startup** (`updates::install::clean`, on a background thread after the
  data folder is resolved) removes everything in `updates/` except the two
  check files, every `.reshiki-update-*` folder beside the app (also the ones
  earlier versions left, never the folder the app itself runs from), and the
  two old check files. So `updates/` only ever holds the check files and the
  version being installed.

**Not deleting an update in use.** Two ReShiki windows can run at once, and one
may launch while the other is downloading or its helper is mid-swap. Each
update folder has a `pid` file: the ReShiki that downloads it writes its
process ID, and the helper appends its own before it acknowledges. Startup
cleanup skips a folder with a live process in it (same liveness check as
recovery drafts), and `prepare()` refuses to take over a version folder
another live ReShiki is using. A stale ID only delays removal to a later
launch.

## Evidence

Folder listings through check → download → install → next launch, in a
throwaway data folder and applications folder. There is no local fake release
source (the updater only talks HTTPS to GitHub), so the download step writes
the files `prepare()` would; everything else is the real code: `Cache::save`,
`claim`, `Prepared::stage`/`beside_app`, the real `install.sh` and `clean_in`.

**Before** (main `df1f03d40`, with main's `install.sh`;
[script](before-main.sh), [full listing](before-main.txt)). After the
install and the next launch, 14 leftover paths stay beside the app for good:

```text
Applications/.reshiki-update-Ab12Cd
Applications/.reshiki-update-Ab12Cd/SHA256SUMS
Applications/.reshiki-update-Ab12Cd/extracted/…
Applications/.reshiki-update-Ab12Cd/install.log
Applications/.reshiki-update-Ab12Cd/install.sh
Applications/.reshiki-update-Ab12Cd/installed/…
Applications/.reshiki-update-Ab12Cd/previous/build.json
Applications/.reshiki-update-Ab12Cd/previous/reshiki
Applications/.reshiki-update-Ab12Cd/ready
Applications/.reshiki-update-Ab12Cd/reshiki-9.9.9-linux-arm64.tar.gz
Applications/ReShiki/…
data/update-cache.json
data/update-preferences.json
```

**After** (this branch; printed by the new test
`an_update_stays_in_its_version_folder_and_is_gone_after_the_next_launch`,
[macOS arm64](after-macos-arm64.txt), [Ubuntu arm64](after-ubuntu-arm64.txt)).
Same-volume case, Linux app folder:

```text
## linux, updates folder on the app's volume, install succeeds: after launch and a check
data/update-preferences.json
data/updates
data/updates/stable.json
Applications/ReShiki
Applications/ReShiki/reshiki

## linux, updates folder on the app's volume, install succeeds: after the download
data/update-preferences.json
data/updates
data/updates/9.9.9
data/updates/9.9.9/SHA256SUMS
data/updates/9.9.9/extracted
data/updates/9.9.9/extracted/reshiki-9.9.9-linux-arm64
data/updates/9.9.9/extracted/reshiki-9.9.9-linux-arm64/reshiki
data/updates/9.9.9/pid
data/updates/9.9.9/reshiki-9.9.9.archive
data/updates/stable.json
Applications/ReShiki
Applications/ReShiki/reshiki

## linux, updates folder on the app's volume, install succeeds: after the helper
data/update-preferences.json
data/updates
data/updates/stable.json
Applications/ReShiki
Applications/ReShiki/reshiki

## linux, updates folder on the app's volume, install succeeds: after the next launch
data/update-preferences.json
data/updates
data/updates/stable.json
Applications/ReShiki
Applications/ReShiki/reshiki
```

The full files have all eight runs: the Linux app folder and the macOS bundle,
from the version folder and from a copy beside the app, installing and failing
after the swap. In the cross-volume runs `Applications/.reshiki-update-9.9.9/`
appears at restart and is gone after the helper; in the failing runs the old
app is back and the listings end the same way.

## Verification

VERIFICATION_TABLE

New and changed tests (`src/updates/install/tests.rs`):

- `an_update_stays_in_its_version_folder_and_is_gone_after_the_next_launch`:
  the layout after a check, a download and an install; the previous version
  pruned; the same-volume rename and the cross-volume copy-then-rename; a
  failed install leaving the old app whole and nothing behind; the old check
  files and an old `.reshiki-update-*` folder removed. Eight runs: Linux app
  folder and macOS bundle × both volumes × success and failure, with the real
  `install.sh`.
- `startup_removes_leftovers_but_not_an_update_in_use`: a finished update, a
  half download and a stray file go; the check files, an update a live process
  is using (in `updates/` and beside the app), the target of a symbolic link,
  recovery drafts, other preferences, other apps and a portable copy that
  itself lives in a folder named `.reshiki-update-…` stay; `claim` refuses a
  folder another live process uses and takes it once that process is gone.
- `an_update_given_up_before_it_installs_removes_its_folder`.
- `helper_replaces_owned_files_and_rolls_back_an_interrupted_install` now also
  checks the stage is gone after success, a failed move and a missing binary.
- The two "changed after it was checked" tests keep passing against the new
  staging.

The macOS signature check (`codesign`) cannot pass on a test bundle, so the
tests call `stage`/`beside_app` and compare the digest themselves; the
re-check in `handoff` is covered by the refusal tests.

## Risk

- **The swap itself is unchanged**: the same two renames with the same
  rollback trap. What is new is where the stage is, one `cp -a` in the
  cross-volume case (re-verified after the copy), and `rm -rf "$stage"` at the
  end. `$stage` is always a folder this ReShiki created:
  `updates/<version>` (a validated stable `X.Y.Z`) or
  `.reshiki-update-<version>` beside the app.
- **The previous version and the failure log are no longer kept.** Before,
  the previous app and `install.log` stayed beside the app forever; now they go
  with the stage. A failed install still restores and reopens the previous app
  (macOS, Linux). Two consequences of pruning by default:
  - On Linux the helper starts the new app in the background and cannot see
    whether it runs. If a new release does not start on this system (say, a
    library it needs is missing), the previous version is no longer in a
    hidden folder to copy back; it has to be downloaded again from the
    releases page. That check was already missing; only the leftover copy is
    gone.
  - On Windows a failed installer and its log are removed at the next start,
    where the helper's message used to name the folder that kept them (the
    message only ever went to that log).
- **A data folder that cannot be written now blocks "Update and restart"**
  (the download needs `updates/<version>/`); checking for updates still
  works. Before, the download went beside the app. Settings and recovery
  drafts cannot be written in that state either.
- **Startup deletes by name beside the app**: only entries of the app's own
  parent folder whose name starts with `.reshiki-update-`, and only for an
  installed or portable release (a development build has no install target
  and skips this). A symbolic link is removed, never followed.
- **Unlikely cases, explained rather than handled:**
  - Process IDs are reused. A stale `pid` naming a now-unrelated live process
    keeps a leftover until a later launch; nothing is lost.
  - An *earlier* version's update has no `pid` file. If a ReShiki with this
    change, installed under another name in the same folder, starts during the
    about one second in which an earlier version's helper is swapping, it
    could remove that helper's stage. Two differently named copies in one
    folder, one updating in that second, was judged too unlikely to guard.
  - If the helper is killed between its two renames (power loss in a window
    of milliseconds), or the rollback's own rename fails, the previous app
    stays in the stage: the helper does not remove it. The next ReShiki to
    start with that data folder would, and by then the user has an app again.
    Before, it stayed until deleted by hand.
  - Two ReShiki windows that both pick the same version folder in the same
    instant (one cleaning up or downloading exactly as the other claims it)
    are not serialized by a lock; the `pid` file narrows this to the moment
    between reading it and acting. The outcome is a failed download or a
    refused install, except in the swap's own milliseconds.
  - A disk image still mounted in a version folder after a crash cannot be
    removed until it is unmounted; cleanup retries at each launch.
- **Windows** is covered by PR CI only (build, clippy, unit tests). The helper
  change there is three lines: append `$PID`, drop "retained in" from the
  failure message, and remove the stage after starting the new app. If that
  removal races the helper's own open log, the next launch removes the rest.
- **Earlier versions sharing the data folder** (a stable and a nightly side by
  side) write `update-cache*.json` again; the newer one deletes them at its
  next start. Harmless, one extra check each.

## Changelog

`docs/changes/unreleased/feat-updates-folder.md` (Changes).

## Docs updated

- `website/src/content/docs/guide/install.mdx`: **Your data folder** lists
  update downloads; **Uninstall** no longer asks you to hunt for a hidden
  folder beside the app (only after uninstalling an earlier version);
  **Updates** says where the download goes, when it is removed, the
  cross-volume copy, and what happens when the install itself fails.
- `docs/modules.md` is unchanged (`module_index.py --check` passes).

## Review

An independent adversarial review (a second model, read-only, on the diff)
looked for ways to lose or corrupt the installed app, partial downloads,
cross-volume renames, Windows file locking and deleting the wrong folder. Fixed
from it:

- startup cleanup could remove a portable copy that itself lives in a folder
  named `.reshiki-update-…`: the app's own folder is now never a leftover;
- equal device numbers do not promise a rename works (two bind mounts of one
  disk on Linux), and `mv` would then silently copy during the swap: the code
  now tries the rename with an empty file;
- a stage that cannot be removed made the rollback exit before reopening the
  restored app: removal there is now best effort;
- the Python restart-argument tests cut the helpers at a line that now comes
  after the `pid` write.

Explained under Risk instead of handled: the unlocked claim/cleanup instant,
an interrupted swap's backup, the Linux launch that is not confirmed, the
Windows failure log, and a read-only data folder.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

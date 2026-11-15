## Summary

The desktop app can keep drawings in the user's GitHub repositories.

- **Sign in with a code.** Toolbar **GitHub → GitHub account… → Sign in with GitHub** shows a code, copies it and opens GitHub; the user pastes it there. No password, client secret or private key is involved.
- **Open from GitHub.** A picker lists the repositories ReShiki may use and one folder at a time, with each drawing rendered as a thumbnail.
- **Save stays local, Send goes to GitHub.** Cmd+S saves on this computer at once and offline. The status bar then shows **1 not on GitHub · Send**. **Send** makes one commit of every changed drawing in that repository, each with an SVG preview beside it, and the chip turns to **On GitHub**.
- **Never overwrites silently.** If a drawing changed on GitHub since it was opened, Send leaves it out and shows **GitHub’s** and **Yours** side by side with the differences highlighted, then **Keep GitHub’s**, **Keep mine** or **Keep both** (`<name> (2).rsk`). Escape decides later; the chip shows **1 conflict · Review**.
- **Versions** lists the saves on this computer since the last send and the GitHub commits that changed the drawing; **Compare with current**, **Open** and **Restore**.
- **Closing** a drawing with saves not on GitHub asks **Send to GitHub** or **Later**.
- **New private repository…** in the picker makes a private repository and selects it.
- **Signed in, Star on GitHub stars ReShiki in one click** (no browser), and the star card never asks someone who already starred.

Desktop only (macOS, Windows, Linux). Docs: `docs/github.md`, privacy policy section, release note.

## Why it matters

ReShiki drawings live in local `.rsk` files, so moving between computers, keeping a history or sharing with a group means copying files by hand. Many chemists already have GitHub accounts (for code or lab notebooks), and `.rsk` is JSON, which GitHub stores and diffs well. With the SVG preview beside each drawing, a repository also shows the drawings on github.com without ReShiki.

The owner set the shape of the feature on 2026-11-15: a two-step save (local save, separate Send), private repositories, a visual conflict choice instead of a silent overwrite, Versions, and a one-click star when signed in.

## Approach

- **REST API only.** ReShiki reads trees and blobs and writes blobs, one tree, one commit and a fast-forward ref update through GitHub's REST API (`src/github/api.rs`, `send.rs`). Only the files the user opens are downloaded, into a working copy under the data folder (`<data>/github/<owner>/<repo>/files/` with `state.json` and up to 50 local saves per drawing in `versions/`). A drawing is "not on GitHub" when its saved bytes differ from what was last synced, so no extra flag can drift. If the branch moved, Send retries against the new head and treats only drawings that changed there as conflicts.
- **GitHub App with device-flow sign-in** (`src/github/auth.rs`). Tokens expire after 8 hours and refresh without a secret. They are kept only in the system credential store: Keychain on macOS, Credential Manager on Windows (new wrapper in `native/windows`), Secret Service on Linux; without a keyring the sign-in lasts until quit. Any `RESHIKI_GITHUB_API` / `RESHIKI_GITHUB_WEB` override keeps the sign-in in memory only, and an override must be `https` or loopback `http`.
- **Compare** (`src/app/github/compare.rs`) matches atoms, text, arrows and graphics by id and bonds by their two atoms, and draws boxes under the two drawings, so saved highlight colours are never repainted. Anything else in the file is reported as **Style or settings changed**.
- **UI** lives in `src/app/github.rs` and `src/app/github/` (account, picker, versions, conflict). Every dialog close returns keyboard focus to the drawing (`focus_drawing`).
- **Tests run against a local mock GitHub** (`src/github/mock.rs`, test-only) with device codes, tokens, repositories as commits, request logging, injected faults and races. No test or CI job talks to github.com.

Alternatives rejected:

- **`git clone` / a git library.** Needs git installed or a large native dependency on three platforms, downloads the whole repository and its history, and brings merges, rebases and index state that ReShiki would have to explain. The REST API needs only the existing HTTP client and moves only the files the user opens.
- **A local git folder the user manages.** Pushes the work (clone, commit, push, conflicts) onto chemists who mostly do not use git, and ReShiki could not show a visual conflict choice or keep the "not on GitHub" state reliable.
- **An OAuth App.** Its tokens get the broad `repo` scope over every repository and do not expire. A GitHub App lets the user pick which repositories ReShiki may use, has fine-grained permissions (Contents, Metadata, Starring, repository creation) and expiring tokens.
- **Browser sign-in with a redirect** instead of the device flow. A desktop app would need a loopback redirect server or a custom URL scheme on each platform, and GitHub's web flow exchanges the code with the client secret, which cannot stay secret in a distributed app. The device flow needs no secret, no listener and works the same on all three platforms; the cost is pasting an 8-character code, which ReShiki copies for the user.

## Evidence

Real app, macOS arm64 debug build of `5d96de06d`, window 1280 × 852 pt, against a **local mock GitHub** (the test mock in `src/github/mock.rs`, served with `RESHIKI_GITHUB_CLIENT_ID=mock` and the API/web overrides; a small pass-through in front of it held the code approval so the code dialog could be captured). User `@octo-test`, private repository `lab-notes` with `ring.rsk` (benzofuran), `ring.svg` and `scheme/route.rsk`. Each run used a fresh `RESHIKI_DATA_DIR`. Driven with Codex computer use; each image is a capture of the ReShiki window only (for the close question, the window with ReShiki's own alert on top). The mock dates its commits 2026-11-15 14:02 UTC, so GitHub entries read "Today 23:02" in Japan time.

### Sign in

| Light | Dark |
| --- | --- |
| <img src="light-03-sign-in-code.png" width="420"><br>Sign in with GitHub: the code ABCD-1234, "Code copied. Paste it on GitHub.", Open GitHub ↗ / Copy code / Cancel, "Waiting for GitHub…". | <img src="dark-03-sign-in-code.png" width="420"><br>The same code dialog in the dark interface. |
| <img src="light-04-signed-in.png" width="420"><br>After approval: "Signed in as @octo-test", 1 repository; status bar "Signed in to GitHub". | <img src="dark-04-signed-in.png" width="420"><br>The same, dark. |

<img src="light-01-github-menu.png" width="420"> <img src="light-02-account-signed-out.png" width="420">

The toolbar's GitHub (cloud) menu on an Untitled drawing (Versions is disabled because the drawing is not on GitHub), and the signed-out account dialog.

### Open from GitHub

| Light | Dark |
| --- | --- |
| <img src="light-05-open-picker.png" width="420"><br>Open from GitHub: repository octo-test/lab-notes (lock = private), a `scheme` folder tile and the ring.rsk thumbnail. | <img src="dark-05-open-picker.png" width="420"><br>The same picker, dark. The thumbnail keeps the drawing's own white page. |
| <img src="light-06-open-picker-folder.png" width="420"><br>Inside `scheme`: the route.rsk thumbnail. | <img src="light-07-opened-on-github.png" width="420"><br>ring.rsk opened; the status bar chip says "On GitHub". |

### Save, then Send

| Light | Dark |
| --- | --- |
| <img src="light-08-saved-not-on-github.png" width="420"><br>One bond added to the right of the ring, then Cmd+S: "Document saved", chip "1 not on GitHub" with Send. | <img src="dark-08-saved-not-on-github.png" width="420"><br>The same state, dark interface (the drawing keeps its white page). |
| <img src="light-09-send-box.png" width="420"><br>Send to GitHub: octo-test/lab-notes, "1 drawing: ring.rsk", message "Update ring.rsk", Cancel / Send. | <img src="dark-09-send-box.png" width="420"><br>The same Send box, dark. |
| <img src="light-10-sent.png" width="420"><br>After Send with the message "Add an ethyl group": chip "On GitHub", status "Sent to GitHub". The mock's newest commit is "Add an ethyl group". | |

### Versions

| Light | Dark |
| --- | --- |
| <img src="light-11-versions.png" width="420"><br>Versions after two more saves: ON THIS MAC (two saves, Today 18:33) and ON GITHUB ("Add an ethyl group", "Remote change to ring.rsk"). The upper fragment is a C=O group the test run drew by mistake; it is part of the saved drawing. | <img src="dark-11-versions.png" width="420"><br>Versions, dark: one save on this Mac, two commits on GitHub. |
| <img src="light-12-versions-compare.png" width="420"><br>Compare with current: the "Add an ethyl group" commit (left) beside the drawing now (right); the two changes since are boxed. "Highlighted: different". | |

### Close with saves not on GitHub

| Light | Dark |
| --- | --- |
| <img src="light-13-close-unsent.png" width="420"><br>Cmd+W on ring.rsk with one save not on GitHub: "Send “ring.rsk” to GitHub? Saved on this computer only." Send to GitHub / Later. Send to GitHub closed the tab and made the commit "Update ring.rsk". | <img src="dark-13-close-unsent.png" width="420"><br>The same question, dark (answered Later). |

### New private repository

| | |
| --- | --- |
| <img src="light-14-save-to-github.png" width="420"><br>Send to GitHub on an Untitled drawing opens "Save to GitHub" with a name field (Untitled.rsk) and Save here. | <img src="light-15-new-repo.png" width="420"><br>New private repository…: name "reaction-notes" and Create. |
| <img src="light-16-new-repo-created.png" width="420"><br>After Create: octo-test/reaction-notes (private) is listed and selected, "No drawings here.", Save here enabled. | <img src="light-17-saved-to-new-repo.png" width="420"><br>Saved as first-route: tab first-route.rsk, chip "On GitHub", status "Sent to GitHub". The mock repository holds README.md, first-route.rsk and first-route.svg. |

### A drawing changed on GitHub (conflict)

Each conflict: a bond added and saved in ReShiki, then a commit on the mock changes one ring carbon of ring.rsk to N, then Send.

| Light | Dark |
| --- | --- |
| <img src="light-20-conflict-compare.png" width="420"><br>""ring.rsk" changed on GitHub": GitHub's (the N, boxed) beside Yours (the new bond, boxed); "Keep both: yours becomes “ring (2).rsk”"; Keep GitHub's / Keep mine / Keep both. | <img src="dark-20-conflict-compare.png" width="420"><br>The same compare, dark, with two local bonds. |
| <img src="light-21-conflict-chip.png" width="420"><br>Escape: the chip shows "1 conflict" with Review. | <img src="dark-21-conflict-chip.png" width="420"><br>The same, dark. |
| <img src="light-22-kept-mine.png" width="420"><br>Review → Keep mine: yours stays and is sent; chip "On GitHub", status "Sent to GitHub". | <img src="light-23-conflict-b.png" width="420"><br>Second conflict: GitHub's has the N at another position; yours has two new bonds. |
| <img src="light-24-kept-github.png" width="420"><br>Keep GitHub's: the drawing becomes GitHub's (the N ring, no new bonds); status "Kept GitHub’s", chip "On GitHub". | <img src="light-25-undo-brings-yours.png" width="420"><br>One Cmd+Z brings yours back (both bonds); chip "1 not on GitHub", status "History restored". |
| <img src="light-26-kept-both.png" width="420"><br>Third conflict → Keep both: the open tab is now ring (2).rsk with your bonds, chip "On GitHub", status "Sent to GitHub". | <img src="light-27-picker-after-keep-both.png" width="420"><br>Open from GitHub afterwards: ring (2).rsk (yours) and ring.rsk (GitHub's N ring) side by side. |

### One-click star when signed in

| | |
| --- | --- |
| <img src="light-30-star-card.png" width="420"><br>The "Enjoying ReShiki?" card (data folder seeded so the card is due), signed in. | <img src="light-31-starred.png" width="420"><br>After Star on GitHub: no browser, the card closes, status "Starred on GitHub. Thank you!". The mock now reports ReShiki as starred. |
| <img src="light-32-about-starred.png" width="420"><br>About (click the ReShiki wordmark): the star link reads "★ Starred". | <img src="dark-32-about-signed-in-not-starred.png" width="420"><br>About while signed in and not starred, dark: "Star ReShiki on GitHub" without ↗, because a click stars through the API instead of opening the browser. |

### Keyboard focus after each dialog

After each dialog closed, with no click, `?` was pressed (Help opens, or the properties of the atom or bond under the keyboard-drawing cursor open; both mean the key reached the drawing).

| Dialog closed | Result |
| --- | --- |
| Account (Close) | Help opened |
| Send box (Send) | Keys reached the drawing (checked with tool keys) |
| Close question (Send to GitHub) | Help opened |
| Conflict (Escape, Keep mine, Keep GitHub's) | Help opened |
| Conflict (Keep both) | Properties of the active atom opened |
| Open from GitHub (Open) | Properties of the active bond opened |
| Open from GitHub (Cancel) | Help opened |
| Star card (Star on GitHub), About (Close) | Help opened |
| Save to GitHub (Save here) | Inconclusive: neither Help nor properties showed while the chip went from Sending… to On GitHub |

Unit tests on macOS arm64 (local): `github` backend tests in the library 68 passed; app-level `github` tests 47 passed; `star_prompt` tests 14 passed.

## Verification

VERIFICATION_TABLE

## Risk

- **Real GitHub is untested.** Every run above and every test used the local mock; no request went to github.com. The GitHub App "ReShiki" (client ID `Iv23li1avBvJkyU0uwhc`, slug `reshiki`) is registered and is the built-in default, but nobody has signed in to it from ReShiki yet. Behaviour that only real GitHub can confirm: the device-flow and refresh responses, `/user/installations` listing, `POST /user/repos` with a GitHub App user token (and whether a new repository joins a "selected repositories" installation), secondary rate limits, and `PUT /user/starred` with the Starring permission.
- **What the owner must do before merging:**
  1. In the GitHub App settings, confirm Device Flow is enabled and "Expire user authorization tokens" is on; permissions Contents read/write, Metadata read, Starring read/write, and Repository creation write (or Administration write; drop Administration if Repository creation alone lets **New private repository…** work).
  2. Install the app on a test account limited to one test repository, then in a release-like build: sign in, Open from GitHub, edit, Cmd+S, Send; check on github.com that one commit holds the `.rsk` and its `.svg`.
  3. Edit the same drawing on github.com, then Send from ReShiki: the compare must appear; try each of the three choices.
  4. **New private repository…**: check the repository is private and that ReShiki can open it right away.
  5. Star from the card while signed in, and sign out/in once to check the Keychain entry (macOS), Credential Manager (Windows x64) and Secret Service (Linux).
- **Credential stores.** The evidence runs used the in-memory store (any address override forces it). A Keychain round trip was run once on macOS arm64 during development; Windows Credential Manager and Linux Secret Service were not exercised in this evidence run.
- **Found in this evidence run (not fixed here):** the status bar says "Sent · 1 drawing changed on GitHub and was left out" in red even when that one drawing was the only one and nothing was sent; the star card can open while the GitHub toolbar menu is open; the GitHub menu items and the account dialog's signed-in buttons are not in the accessibility tree until another action refreshes it.
- Scope: default branch only, `.rsk` and `.svg` only, desktop only.

## Changelog

- The desktop app keeps drawings in your GitHub repositories. A new **GitHub** button in the toolbar signs in with a code, opens drawings with **Open from GitHub…** and sends them with **Send to GitHub**. **Save** stays on this computer; **Send** makes one commit of every changed drawing in the repository, with an SVG preview beside each. The status bar shows what is not on GitHub yet, closing such a drawing asks **Send to GitHub** or **Later**, and **Versions** opens or restores earlier saves and commits. A drawing changed on GitHub meanwhile is never overwritten: ReShiki shows GitHub's and yours side by side with the differences highlighted, then **Keep GitHub’s**, **Keep mine** or **Keep both**.
- Signed in to GitHub, **Star on GitHub** stars ReShiki with one click, without a browser, and the star card never asks someone who already starred.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any:

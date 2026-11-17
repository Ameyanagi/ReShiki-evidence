## Why it matters

The owner reported on the Windows nightly `0.15.0-nightly.20261116.43935165397.1`:
signed in to GitHub, **About › ★ Star on GitHub** (no ↗, so the one-click
path) opened the browser instead of starring. They had already starred
ReShiki, yet About did not say **Starred**.

## Root cause

- **About never asked GitHub.** The link showed **★ Starred on GitHub** only
  after a star made in the same run. A star from the website, another computer
  or an earlier run was never looked up. Confirmed in the code.
- **Any failed star was silent.** Whatever GitHub answered, the app dropped the
  reason and opened the browser. Confirmed in the code; this is why the report
  could not say what went wrong.
- **The star request stated no length.** `PUT /user/starred/{owner}/{repo}`
  went out with no `Content-Length`. GitHub's REST documentation for this
  endpoint says the length must be set to zero. Confirmed that the app sent
  none: the new mock check fails without the fix (`Rejected("GitHub refused
  the request.")`). **Not confirmed live** that this is what GitHub refused:
  without an account, `PUT /user/starred/octocat/hello-world` with an invalid
  token answers 401 with and without `Content-Length: 0` (HTTP/1.1 and
  HTTP/2), and the anonymous `POST /markdown` reaches the API either way, so
  GitHub's edge does not turn a lengthless write away today. If the star still
  fails after this change, the status now names the reason (for example **No
  access on GitHub**, which would point at the sign-in's permissions).

## Approach

- `client.send`: a PUT, POST or PATCH without a body sends
  `Content-Length: 0`. The star is the only such request today. Four lines, to
  stay clear of the HTTP client work in progress elsewhere.
- The mock answers 411 to a write that states no length.
- **About** asks GitHub once per sign-in whether ReShiki is starred (again on
  the next open only if GitHub could not tell). When it is, the link reads
  **★ Starred on GitHub** and opens the project page. The accessible name is
  the label.
- A failed one-click star sets the status, for example "Couldn't star through
  GitHub (No access on GitHub). Opened GitHub instead." An expired sign-in
  signs out as it does elsewhere. A second star is the same 204 and counts as
  success.
- The command palette has **Star ReShiki on GitHub** (with ↗ when signed out),
  the same action as About's link. It is gone once starred.
- The privacy policy names the new check: opening About while signed in
  contacts GitHub.

## Evidence

Pending: before/after window captures against the local mock (About with an
existing star; the palette row).

## Verification

VERIFICATION_TABLE

Pending: full checks and review notes.

## Risk

- Small. The length header only affects bodiless writes, and the star is the
  only one.
- One more request to GitHub per sign-in, when About opens.
- If GitHub refuses the star for another reason, the browser still opens, now
  with the reason in the status.

## Changelog

- Signed in to GitHub, **★ Star on GitHub** stars ReShiki instead of opening
  the browser: the request GitHub refused now states its length. If GitHub
  still cannot make the star, the status says why before the page opens.
- **About** shows **★ Starred on GitHub** when you already starred ReShiki,
  also from the website or another computer.
- The command palette has **Star ReShiki on GitHub**.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

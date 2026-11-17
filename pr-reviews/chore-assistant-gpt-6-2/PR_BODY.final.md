## Why it matters

Codex now offers the GPT-6.2 models. ReShiki's built-in assistant still asked for GPT-6 Astra by default, and the assistant benchmark ran GPT-6.1 Sol by default. This makes GPT-6.2 Sol the assistant's default.

## Approach

- The assistant's default model is `gpt-6.2-sol` (`src/assistant/settings.rs`). Resolution is unchanged: a model you chose yourself stays chosen; otherwise the default is used when the Codex catalog offers it, then the account default, then the newest model.
- The model menu, Settings and the composer name **GPT-6.2 Sol**.
- The benchmark driver and example default to `gpt-6.2-sol`. The documented reproduction of the recorded baseline now passes `--model gpt-6.1-sol`, so it still measures the model that baseline used.
- Docs (`docs/assistant.md`, `docs/assistant-setup.md`, the website guide) say GPT-6.2 Sol and name the newest-model fallback. A changelog fragment is added.

## Evidence

The change only renames a model ID and its labels; the evidence is the tests.

- The resolver test now checks literal IDs: with GPT-6 Sol and GPT-6.2 Astra in the catalog, Default resolves to the account default; once `gpt-6.2-sol` appears, Default resolves to it, and a newer generic model (`gpt-6.3`) does not take over. Before this change the test compared against the constant itself, so it could not catch a wrong default.
- The benchmark test asserts the driver passes `gpt-6.2-sol` when no model is given.

[Check output](https://github.com/Ameyanagi/ReShiki-evidence/blob/dcdeffc12270e66527bf2ec14622826f6e0e5d17/pr-reviews/chore-assistant-gpt-6-2/checks.txt)

## Verification

| Platform | Result |
|---|---|
| macOS arm64 (Apple M4) | pass · fmt, clippy, assistant + Settings tests incl. renderer, benchmark tests, changelog, docs tree |
| PR CI | Linux and Windows on this PR |

macOS arm64: `cargo fmt --check`; workspace clippy `--all-targets --all-features -D warnings`; lib and bin tests filtered to `assistant` and `settings_page` (27 + 53 passed); the same renderer tests with `--include-ignored` (60 passed); benchmark Python tests (10 passed); changelog and docs-tree checks.

Two independent Codex (GPT-6.2 Sol) reviews. The first found the UI labels, guides and benchmark command still naming the old models and a test that could not fail; all fixed. The second confirmed the fixes.

## Risk

Low. Someone who never chose a model and whose Codex catalog lacks `gpt-6.2-sol` gets the account default instead of GPT-6 Astra.

Known and left as is:
- The Default entry always reads "Default · GPT-6.2 Sol", even when the account lacks it and the composer shows the fallback. This was already so for GPT-6 Astra.
- Two guide screenshots still show older model names (GPT-6 Astra in setup, GPT-6 Sol in the website's model menu); they need a fresh capture with a signed-in Codex account.

## Changelog

- The assistant now defaults to GPT-6.2 Sol when your Codex account offers it.

## Contribution license

- [x] I have read [CONTRIBUTING.md](https://github.com/Ameyanagi/ReShiki/blob/main/CONTRIBUTING.md). I have the right to submit this contribution and agree to offer my original contributions under both MIT and Apache-2.0, so recipients may choose either license (`MIT OR Apache-2.0`).
- [x] Any third-party material is identified below with its source and license, and its required notices are preserved; otherwise, no third-party material is added.

Third-party sources, if any: none.

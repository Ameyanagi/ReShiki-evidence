# Equipment authoring review

Captured in the native macOS drawing editor at ReShiki commit `e4feeb21580aa8dc01305b620d4798eade96f311`, using an isolated application profile. The app executable SHA-256 was `86c78b558d2e16e8033c84f23e948e0947d2f9961b9997e7c527a5f7db44b5e0`.

The measured flask uses the unmodified source fixture at 183% in the Publication theme. I marked the top rim as 16 mm, accepted the draft, and used one drawing Undo and Redo. The saved and reopened drawing has a glass body and an open outline in the equipment definition. The outline retains the standard 0.6 pt weight. The exact-head IO regressions cover the exchange routes.

The standard neck uses the corresponding unmodified source fixture at 250%. I previewed the outward 15/25 socket, flipped it inward and confirmed the error and disabled controls, then used draft Undo to restore the valid direction. Add joint and Accept created one drawing edit. One drawing Undo restored the clean source, and Redo restored the adapter. The saved and reopened definition has one 15/25 socket with outward direction.

The in-flight Assistant interactions were exercised by the deterministic app tests.

[Reproduction steps and source fixtures](https://github.com/Ameyanagi/ReShiki/blob/e4feeb21580aa8dc01305b620d4798eade96f311/tests/fixtures/equipment-authoring/README.md)

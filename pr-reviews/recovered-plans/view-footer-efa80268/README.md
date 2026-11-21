# Light/Dark stays in the status bar

These are native macOS captures from ReShiki at `efa80268576f9ab65c8fa866c879e4eb2a2a5fb7`. The bottom row keeps the Styles chooser, the dedicated Sun/Moon button, and View side by side.

1. Open the Fischer esterification drawing. Click the Sun in the status bar and verify the entire canvas and interface switch to Dark at the same 81% zoom.
2. Click the Moon to return to Light. Both clicks work with View closed.
3. Open View. Down and Return enable Rulers and return focus to View. Turn on Grid, then reopen the menu to see both checked. Escape returns focus to View.

The exact build also passed the real-renderer test for both 700 px and 1040 px windows. It verifies one visible bottom toggle, pointer and accessibility activation, and preservation of the drawing, camera and history.

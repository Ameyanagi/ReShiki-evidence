# Light/Dark in the bottom status bar

Native macOS captures from `53070ebd36871a16097b9b5c17c693bb277ff88f`, including the merged Add tab.

The same Fischer esterification drawing stays at 81% in both Light and Dark. The Sun/Moon button sits between Styles and View, and both transitions work with View closed. View opens above its button. Down and Return enable Rulers; Grid can be enabled separately. Escape returns focus to View.

With the drawing selected and Grid focused inside View, I pressed Left, Right, Backspace, and Delete. View stayed open, the document did not become dirty, and Undo was still disabled after dismissal. The exact build also passes the real renderer checks for View layout and keyboard input, the direct footer toggle, six View state tests, and three Add renderer tests.

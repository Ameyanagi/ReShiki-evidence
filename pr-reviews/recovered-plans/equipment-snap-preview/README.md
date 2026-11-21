# Test snapping in an equipment draft

These are native macOS screenshots from ReShiki commit `05f9b67963cb8268008a20876074efd0a41ae4dc` with the JACS / ACS preset and Publication presentation. The parent equipment authoring branch was at `e4feeb21580aa8dc01305b620d4798eade96f311`. The screenshots are 2560 × 1704 pixels.

1. Open `standard-joint-neck.rsk`, select its artwork and choose **Define equipment**. Name the piece *Glass socket adapter* and add a 15/25 female taper at the rim.
2. Start **Test snapping** and drag the gray 15/25 stopper toward the socket. The matching fit appears at 250% in light and dark themes.
3. At 128%, rotate the round-bottom flask trial by 180° and bring its socket toward the authored socket. The app reports that the two sockets do not seat.
4. Try a 29/42 stopper at 128%. The preview suggests an expansion adapter from 15/25 to 29/42.
5. With the adapter preview still visible, accept the authored piece. One drawing Undo restores the original artwork. Redo restores the authored piece. The saved file `accepted-glass-socket.rsk` reopened with a single placed piece, a single 15/25 female joint, and an empty Undo history.

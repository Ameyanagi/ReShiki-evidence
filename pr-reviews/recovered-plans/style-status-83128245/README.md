# Journal preset and color theme in ReShiki

The screenshots come from a native macOS run at commit `83128245a6f1f4e6e1476d5c5c38dfd1343a6381`. The test executable has SHA-256 `5ad18c4394dcc815a6dc6c3d7468bdad328cb8348c5c55cde1790c3051c0149a`.

1. Open [Fischer esterification.rsk](fixtures/Fischer%20esterification.rsk). The footer shows [JACS · Publication](01-closed.jpg). Open it to see [two separate selectors](02-open.jpg) and the two managers. The paper and zoom stay in place.
2. Change the journal preset to [Nature while keeping Publication](03-nature-publication.jpg). Change the theme to [Pastel while keeping Nature](04-nature-pastel.jpg). Undo once to return to Nature and Publication and once more to [restore JACS and Publication](05-undo-restored.jpg).
3. With the chooser open, Tab moves through Journal preset, Color theme, Manage styles, and Manage themes. Shift+Tab reverses the order. Return opens the focused manager. The [theme manager](06-manage-themes.jpg) and [drawing style manager](07-manage-styles.jpg) open without writing to the drawing. Escape closes the chooser and returns focus to its status button.
4. Open [Embedded theme.rsk](fixtures/Embedded%20theme.rsk) in an empty theme library. The footer shortens the long theme name. The [chooser and its accessible value](08-embedded-theme.jpg) keep the name saved in the drawing.

With keyboard drawing enabled, Return and Backspace stayed in the open chooser. They left the drawing and its Undo history unchanged. The two selector controls also accepted choices by accessible name.

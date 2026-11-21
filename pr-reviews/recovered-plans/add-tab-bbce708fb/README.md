# Add gallery and import follow-up

These captures use the native macOS app at `bbce708fb4a06d318f99f84b55ad5051b5f95248`. Executable SHA-256 `61f9574500e0f296434f3435c1544a25d2ca10437eb40946d72909d1ce1cabbd`.

1. Open Add in an empty drawing. Browse the template categories, then type benzene. A chemical name result and the Benzene template appear together.
2. Press Enter. The name field keeps its text while resolving the name. On success the drawing receives focus, and the labeled ring appears at the view center with zoom still at 100%.
3. Open More import options and return to Add. The search remains benzene. Try “an unsupported chemical name”. Add keeps the text and focus, shows the warning, and leaves the drawing intact.
4. Open a fresh tab and type `CCO ethanol`. The result says “from SMILES”. Press Enter to insert ethanol, then Undo once to restore the empty drawing.

The captures use the Publication theme. The headless regressions also cover CXSMILES warnings, a pending request across tabs, and keyboard focus in advanced Import.

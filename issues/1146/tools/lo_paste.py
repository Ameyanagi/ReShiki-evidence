# Run with LibreOffice's python: connects to a running soffice, reports the
# system clipboard flavors LibreOffice sees, then pastes into Writer and Impress.
import sys, time, uno
from com.sun.star.beans import PropertyValue
ctx = uno.getComponentContext()
resolver = ctx.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", ctx)
for _ in range(60):
    try:
        rctx = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % sys.argv[1]); break
    except Exception: time.sleep(1)
smgr = rctx.ServiceManager
clip = smgr.createInstanceWithContext("com.sun.star.datatransfer.clipboard.SystemClipboard", rctx)
print("LibreOffice sees flavors:")
for f in clip.getContents().getTransferDataFlavors():
    print("  ", f.MimeType, "|", f.HumanPresentableName)
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", rctx)
disp = smgr.createInstanceWithContext("com.sun.star.frame.DispatchHelper", rctx)
def p(n, v):
    x = PropertyValue(); x.Name = n; x.Value = v; return x
for kind in ("swriter", "simpress"):
    doc = desktop.loadComponentFromURL("private:factory/" + kind, "_blank", 0, ())
    frame = doc.getCurrentController().getFrame()
    time.sleep(1)
    disp.executeDispatch(frame, ".uno:Paste", "", 0, ())
    time.sleep(2)
    page = doc.getDrawPage() if kind == "swriter" else doc.getDrawPages().getByIndex(0)
    print(kind, "shapes after paste:", page.getCount())
    for i in range(page.getCount()):
        s = page.getByIndex(i)
        info = [s.getShapeType()]
        for prop in ("Graphic",):
            try:
                g = s.getPropertyValue(prop)
                if g is not None:
                    gp = g.queryInterface(uno.getTypeByName("com.sun.star.beans.XPropertySet")) if hasattr(g, "queryInterface") else g
                    info.append("MimeType=" + str(g.MimeType))
            except Exception as e: pass
        try: info.append("CLSID=" + s.getPropertyValue("CLSID"))
        except Exception: pass
        sz = s.getSize(); info.append("size=%dx%d (1/100 mm)" % (sz.Width, sz.Height))
        print("  ", " ".join(info))
    if kind == "swriter":
        print("  text:", repr(doc.getText().getString()[:80]))
    doc.close(True)

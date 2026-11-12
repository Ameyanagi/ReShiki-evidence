# Run with a python that has LibreOffice's uno module: connects to a running soffice,
# reports the clipboard flavors LibreOffice sees, pastes into Writer and Impress,
# reports the pasted shapes and screenshots each window. usage: lo_paste.py PORT OUTDIR
import os, subprocess, sys, time, uno
ctx = uno.getComponentContext()
resolver = ctx.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", ctx)
for _ in range(60):
    try:
        rctx = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext" % sys.argv[1]); break
    except Exception: time.sleep(1)
out = sys.argv[2]
smgr = rctx.ServiceManager
clip = smgr.createInstanceWithContext("com.sun.star.datatransfer.clipboard.SystemClipboard", rctx)
print("LibreOffice sees flavors:")
for f in clip.getContents().getTransferDataFlavors():
    print("  ", f.MimeType)
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", rctx)
disp = smgr.createInstanceWithContext("com.sun.star.frame.DispatchHelper", rctx)
for kind in ("swriter", "simpress"):
    doc = desktop.loadComponentFromURL("private:factory/" + kind, "_blank", 0, ())
    frame = doc.getCurrentController().getFrame()
    time.sleep(2)
    disp.executeDispatch(frame, ".uno:Paste", "", 0, ())
    time.sleep(3)
    page = doc.getDrawPage() if kind == "swriter" else doc.getDrawPages().getByIndex(0)
    print(kind, "shapes after paste:", page.getCount())
    for i in range(page.getCount()):
        s = page.getByIndex(i)
        info = [s.getShapeType()]
        try:
            g = s.getPropertyValue("Graphic")
            if g is not None: info.append("MimeType=" + str(g.MimeType))
        except Exception: pass
        sz = s.getSize(); info.append("size=%dx%d (1/100 mm)" % (sz.Width, sz.Height))
        print("  ", " ".join(info))
    if kind == "swriter":
        print("  text:", repr(doc.getText().getString()[:120]))
    subprocess.run(["import", "-window", "root", os.path.join(out, "libreoffice-%s.png" % kind)])
    doc.close(True)

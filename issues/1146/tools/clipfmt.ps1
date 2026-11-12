# Dot-source: Dump-Clipboard lists every clipboard format in enumeration order with its size.
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public static class CB {
  [DllImport("user32.dll")] static extern bool OpenClipboard(IntPtr h);
  [DllImport("user32.dll")] static extern bool CloseClipboard();
  [DllImport("user32.dll")] static extern uint EnumClipboardFormats(uint f);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClipboardFormatName(uint f, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern IntPtr GetClipboardData(uint f);
  [DllImport("user32.dll")] static extern IntPtr GetClipboardOwner();
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("kernel32.dll")] static extern UIntPtr GlobalSize(IntPtr h);
  [DllImport("kernel32.dll")] static extern IntPtr GlobalLock(IntPtr h);
  [DllImport("kernel32.dll")] static extern bool GlobalUnlock(IntPtr h);
  [DllImport("gdi32.dll")] static extern uint GetEnhMetaFileBits(IntPtr h, uint n, byte[] b);
  static string Std(uint f) { switch (f) { case 1: return "CF_TEXT"; case 2: return "CF_BITMAP"; case 3: return "CF_METAFILEPICT"; case 7: return "CF_OEMTEXT"; case 8: return "CF_DIB"; case 13: return "CF_UNICODETEXT"; case 14: return "CF_ENHMETAFILE"; case 16: return "CF_LOCALE"; case 17: return "CF_DIBV5"; default: return null; } }
  public static List<string> Dump(string saveDir) {
    var o = new List<string>();
    for (int i = 0; i < 40 && !OpenClipboard(IntPtr.Zero); i++) System.Threading.Thread.Sleep(50);
    try {
      uint pid; GetWindowThreadProcessId(GetClipboardOwner(), out pid); o.Add("owner pid " + pid);
      uint f = 0; int n = 0;
      while ((f = EnumClipboardFormats(f)) != 0) {
        string name = Std(f); if (name == null) { var s = new StringBuilder(256); GetClipboardFormatName(f, s, 256); name = s.ToString(); }
        long size = -1; string head = "";
        if (f == 2 || f == 3) { size = -2; }
        else {
          IntPtr h = GetClipboardData(f);
          if (h != IntPtr.Zero) {
            if (f == 14) { size = GetEnhMetaFileBits(h, 0, null); }
            else { size = (long)GlobalSize(h).ToUInt64();
              if (size > 0 && size < 200000000) { IntPtr p = GlobalLock(h); if (p != IntPtr.Zero) { var b = new byte[size]; Marshal.Copy(p, b, 0, (int)size); GlobalUnlock(h);
                head = BitConverter.ToString(b, 0, (int)Math.Min(8, size)).Replace("-", "");
                if (saveDir != null) System.IO.File.WriteAllBytes(System.IO.Path.Combine(saveDir, n.ToString("00") + "-" + string.Join("_", name.Split(System.IO.Path.GetInvalidFileNameChars())) + ".bin"), b); } } }
          }
        }
        o.Add(String.Format("{0,2} {1,6} {2,-36} {3,10} {4}", n++, f, name, size, head));
      }
    } finally { CloseClipboard(); }
    return o;
  }
}
"@
function Dump-Clipboard($dir) { if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }; [CB]::Dump($dir) }

# Dot-source. [RP]::Snapshot() captures the current clipboard (HGLOBAL formats and EMF, skipping
# synthesized formats and Ole Private Data); [RP]::Publish(snapshot, extraNames, extraBytes) puts it
# back plus extra registered/standard formats. Used only to test which format each app prefers.
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public class Fmt { public uint Id; public string Name; public byte[] Data; }
public static class RP {
  [DllImport("user32.dll")] static extern bool OpenClipboard(IntPtr h);
  [DllImport("user32.dll")] static extern bool CloseClipboard();
  [DllImport("user32.dll")] static extern bool EmptyClipboard();
  [DllImport("user32.dll")] static extern uint EnumClipboardFormats(uint f);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClipboardFormatName(uint f, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern uint RegisterClipboardFormat(string s);
  [DllImport("user32.dll")] static extern IntPtr GetClipboardData(uint f);
  [DllImport("user32.dll")] static extern IntPtr SetClipboardData(uint f, IntPtr h);
  [DllImport("kernel32.dll")] static extern UIntPtr GlobalSize(IntPtr h);
  [DllImport("kernel32.dll")] static extern IntPtr GlobalLock(IntPtr h);
  [DllImport("kernel32.dll")] static extern bool GlobalUnlock(IntPtr h);
  [DllImport("kernel32.dll")] static extern IntPtr GlobalAlloc(uint f, UIntPtr n);
  [DllImport("gdi32.dll")] static extern uint GetEnhMetaFileBits(IntPtr h, uint n, byte[] b);
  [DllImport("gdi32.dll")] static extern IntPtr SetEnhMetaFileBits(uint n, byte[] b);
  static void Open() { for (int i = 0; i < 40 && !OpenClipboard(IntPtr.Zero); i++) System.Threading.Thread.Sleep(50); }
  public static List<Fmt> Snapshot() {
    var list = new List<Fmt>(); Open();
    try {
      uint f = 0;
      while ((f = EnumClipboardFormats(f)) != 0) {
        if (f == 2 || f == 3 || f == 17 || f == 1 || f == 7 || f == 16) continue;
        var s = new StringBuilder(256); GetClipboardFormatName(f, s, 256); string name = s.ToString();
        if (name == "Ole Private Data") continue;
        IntPtr h = GetClipboardData(f); if (h == IntPtr.Zero) continue;
        byte[] b;
        if (f == 14) { uint n = GetEnhMetaFileBits(h, 0, null); b = new byte[n]; GetEnhMetaFileBits(h, n, b); }
        else { long n = (long)GlobalSize(h); b = new byte[n]; IntPtr p = GlobalLock(h); Marshal.Copy(p, b, 0, (int)n); GlobalUnlock(h); }
        list.Add(new Fmt { Id = f, Name = name, Data = b });
      }
    } finally { CloseClipboard(); }
    return list;
  }
  static IntPtr Global(byte[] b) { IntPtr h = GlobalAlloc(2, (UIntPtr)b.Length); IntPtr p = GlobalLock(h); Marshal.Copy(b, 0, p, b.Length); GlobalUnlock(h); return h; }
  public static string Publish(List<Fmt> list, string[] names, byte[][] extras) {
    var o = new StringBuilder(); Open();
    try {
      EmptyClipboard();
      foreach (var x in list) {
        IntPtr h = x.Id == 14 ? SetEnhMetaFileBits((uint)x.Data.Length, x.Data) : Global(x.Data);
        o.Append((SetClipboardData(x.Id, h) != IntPtr.Zero ? "" : "FAILED ") + (x.Name == "" ? x.Id.ToString() : x.Name) + "; ");
      }
      for (int i = 0; i < names.Length; i++) {
        uint id = names[i] == "CF_DIB" ? 8u : RegisterClipboardFormat(names[i]);
        o.Append((SetClipboardData(id, Global(extras[i])) != IntPtr.Zero ? "+" : "FAILED +") + names[i] + "; ");
      }
    } finally { CloseClipboard(); }
    return o.ToString();
  }
}
"@
function CfHtml([string]$fragment) {
  $pre = '<html><body><!--StartFragment-->'; $suf = '<!--EndFragment--></body></html>'
  $hdr = { param($a,$b,$c,$d) "Version:0.9`r`nStartHTML:{0:D10}`r`nEndHTML:{1:D10}`r`nStartFragment:{2:D10}`r`nEndFragment:{3:D10}`r`n" -f $a,$b,$c,$d }
  $sh = (& $hdr 0 0 0 0).Length; $sf = $sh + $pre.Length; $ef = $sf + [Text.Encoding]::UTF8.GetByteCount($fragment); $eh = $ef + $suf.Length
  [Text.Encoding]::UTF8.GetBytes((& $hdr $sh $eh $sf $ef) + $pre + $fragment + $suf + [char]0)
}

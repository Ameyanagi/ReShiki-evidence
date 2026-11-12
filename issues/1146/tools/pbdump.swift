// Usage: pbdump [outdir]  -- prints every pasteboard item/type with byte size and a short head; saves data per type when outdir is given.
import AppKit
let pb = NSPasteboard.general
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : nil
print("changeCount \(pb.changeCount)")
for (i, item) in (pb.pasteboardItems ?? []).enumerated() {
  print("item \(i)")
  for (j, t) in item.types.enumerated() {
    let d = item.data(forType: t)
    let n = d?.count ?? -1
    var head = ""
    if let d = d { head = d.prefix(8).map { String(format: "%02x", $0) }.joined() }
    print(String(format: "  %2d %-48@ %10d  %@", j, t.rawValue as NSString, n, head as NSString))
    if let out = out, let d = d {
      let name = t.rawValue.replacingOccurrences(of: "/", with: "_")
      try? d.write(to: URL(fileURLWithPath: "\(out)/item\(i)-\(j)-\(name).bin"))
    }
  }
}

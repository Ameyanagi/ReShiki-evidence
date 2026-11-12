// Usage: pbdump <outdir>  -> writes the general pasteboard's first item, one file per type, and prints the types.
import AppKit
let out = CommandLine.arguments[1]
try! FileManager.default.createDirectory(atPath: out, withIntermediateDirectories: true)
let pb = NSPasteboard.general
guard let item = pb.pasteboardItems?.first else { print("empty pasteboard"); exit(1) }
print("changeCount \(pb.changeCount), items \(pb.pasteboardItems!.count)")
for (n, t) in item.types.enumerated() {
  let data = item.data(forType: t) ?? Data()
  let name = "\(n)-\(t.rawValue.replacingOccurrences(of: "/", with: "_")).bin"
  try! data.write(to: URL(fileURLWithPath: out + "/" + name))
  print("\(n) \(t.rawValue) \(data.count) bytes")
}

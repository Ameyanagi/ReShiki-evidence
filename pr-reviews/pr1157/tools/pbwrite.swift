// Usage: pbwrite <dir> [--text <string>] [--text-item] [--text-first]
// Writes item0-N-<type>.bin files from <dir> (in N order) as one pasteboard item, optionally
// with public.utf8-plain-text appended (default), prepended (--text-first) or as a second item (--text-item).
import AppKit
var args = Array(CommandLine.arguments.dropFirst())
let dir = args.removeFirst()
var text: String? = nil; var second = false; var first = false
while !args.isEmpty { let a = args.removeFirst()
  if a == "--text" { text = args.removeFirst() } else if a == "--text-item" { second = true } else if a == "--text-first" { first = true } }
let files = try! FileManager.default.contentsOfDirectory(atPath: dir).filter { $0.hasPrefix("item0-") && $0.hasSuffix(".bin") }
  .sorted { Int($0.split(separator: "-")[1])! < Int($1.split(separator: "-")[1])! }
let item = NSPasteboardItem()
let plain = NSPasteboard.PasteboardType("public.utf8-plain-text")
if let t = text, first, !second { item.setString(t, forType: plain) }
for f in files {
  let parts = f.dropLast(4).split(separator: "-", maxSplits: 2)
  let type = String(parts[2])
  item.setData(try! Data(contentsOf: URL(fileURLWithPath: dir + "/" + f)), forType: NSPasteboard.PasteboardType(type))
}
if let t = text, !first, !second { item.setString(t, forType: plain) }
var items = [item]
if let t = text, second { let i2 = NSPasteboardItem(); i2.setString(t, forType: plain); items.append(i2) }
let pb = NSPasteboard.general
pb.clearContents()
print(pb.writeObjects(items) ? "ok changeCount \(pb.changeCount)" : "FAILED")

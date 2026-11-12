// swift pbwrite.swift <dir>: put one pasteboard item whose types are the files
// <dir>/NN-<type>.bin in name order, the way ReShiki's macOS clipboard worker does.
import AppKit
let dir = URL(fileURLWithPath: CommandLine.arguments[1])
let files = try! FileManager.default.contentsOfDirectory(atPath: dir.path).filter { $0.hasSuffix(".bin") }.sorted()
let item = NSPasteboardItem()
for f in files {
    let type = String(f.dropFirst(3).dropLast(4)).replacingOccurrences(of: "_", with: "/")
    item.setData(try! Data(contentsOf: dir.appendingPathComponent(f)), forType: NSPasteboard.PasteboardType(type))
    print("wrote", type)
}
NSPasteboard.general.clearContents()
print(NSPasteboard.general.writeObjects([item]))

// swift pbdump.swift <outdir> : write every type of every pasteboard item to <outdir>/<item>-<type>.bin
import AppKit
let out = CommandLine.arguments[1]
try? FileManager.default.createDirectory(atPath: out, withIntermediateDirectories: true)
for (i, item) in (NSPasteboard.general.pasteboardItems ?? []).enumerated() {
    for t in item.types {
        let d = item.data(forType: t) ?? Data()
        let name = "\(i)-\(t.rawValue.replacingOccurrences(of: "/", with: "_")).bin"
        try? d.write(to: URL(fileURLWithPath: out).appendingPathComponent(name))
        print(i, t.rawValue, d.count)
    }
}

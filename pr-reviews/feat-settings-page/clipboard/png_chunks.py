"""List a PNG file's chunks in order: index, type, length; pHYs as dpi, iTXt keyword."""
import os
import struct
import sys

for path in sys.argv[1:]:
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path}: not a PNG"
    w, h = struct.unpack(">II", data[16:24])
    print(f"{os.path.basename(path)}: {len(data)} bytes, {w} x {h} px")
    pos, n = 8, 0
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos : pos + 8])
        body = data[pos + 8 : pos + 8 + length]
        note = ""
        if kind == b"pHYs":
            ppm, _, unit = struct.unpack(">IIB", body)
            note = f"  {ppm} px/m = {ppm * 0.0254:.0f} dpi" if unit == 1 else ""
        elif kind == b"iTXt":
            note = f"  keyword {body.split(bytes(1))[0].decode()}"
        print(f"  {n:2} {kind.decode()} {length}{note}")
        pos += 12 + length
        n += 1

"""Write the crafted inputs for the wave1b/import-limits evidence into the folder given as argv[1]."""

import base64, json, os, struct, sys, zlib

out = sys.argv[1]
os.makedirs(out, exist_ok=True)


def write(name, text):
    with open(os.path.join(out, name), "w") as f:
        f.write(text)


# S1: elements nested 3,000 levels deep.
write("deep_3000.cdxml", "<CDXML><page>" + "<group>" * 3000 + "</group>" * 3000 + "</page></CDXML>")

# S2: one element with 20,000 attributes.
attrs = " ".join(f'a{i}="1"' for i in range(20000))
write("attr_20000.cdxml", f"<CDXML><page><n {attrs}/></page></CDXML>")

style = {"bold": False, "color": [0, 0, 0], "family": "Arial", "formula": False, "italic": False,
         "script": "normal", "size_pt": 10.0, "underline": False}


def atom(i, x):
    return {"id": i, "element": "C", "position": {"x": x, "y": 0}, "charge": 0, "isotope": 0,
            "explicit_h": 0, "no_implicit": False, "aromatic": False, "stereo": None, "map_num": 0}


def text_doc(chars):
    return json.dumps({
        "version": 15,
        "atoms": [atom(1, 0), atom(2, 42)],
        "bonds": [{"a": 1, "b": 2, "order": 1, "display": "plain", "stereo": None, "stereo_atoms": []}],
        "annotations": [{"id": 5, "position": {"x": 0, "y": 50}, "text": "A" * chars,
                         "format": {"alignment": "left", "line_spacing": 1.2, "style": style, "width_pt": None}}],
        "arrows": [],
    })


# S3: one text box with 200,000 characters (over the 64 KB cap), and one with 32,000 (under it).
write("text_200k.rsk", text_doc(200_000))
write("text_32k.rsk", text_doc(32_000))


# S4: 30 pictures of 4000 x 4000 pixels (480 million pixels; the budget is 64 million).
def png(width, height):
    row = bytes([0]) + bytes((x * 255 // width, 128, 255 - x * 255 // width, 255)[c]
                             for x in range(width) for c in range(4))
    # Later rows use the PNG "Up" filter and repeat the first row, so they compress to almost nothing.
    raw = zlib.compress(row + (bytes([2]) + bytes(width * 4)) * (height - 1), 9)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


picture = base64.b64encode(png(4000, 4000)).decode()
graphics = [{"picture": picture, "id": i + 1, "kind": "picture",
             "origin": {"x": i * 900.0, "y": 0.0}, "axis_x": {"x": 826.7717, "y": 0.0},
             "axis_y": {"x": 0.0, "y": 826.7717},
             "style": {"stroke": [0, 0, 0], "fill": None, "width_pt": 0.6, "pattern": "solid"},
             "sides": "both", "phase": "solid", "phase_flipped": False, "layer": -1}
            for i in range(30)]
write("pics_30.rsk", json.dumps({"version": 15, "atoms": [], "bonds": [], "annotations": [],
                                 "arrows": [], "graphics": graphics}))

# usage: python3 -I svgsum.py FILE -> one-line summary of an SVG clipboard flavor
import sys
import xml.etree.ElementTree as ET

data = open(sys.argv[1], "rb").read()
root = ET.fromstring(data)


def count(name):
    return sum(1 for e in root.iter() if e.tag.rsplit("}", 1)[-1] == name)


print(
    f"bytes {len(data)} text_elements {count('text')} path_elements {count('path')} "
    f"width {root.get('width')} height {root.get('height')} viewBox {root.get('viewBox')} "
    f"carries_drawing {b'reshiki' in data[:4000].lower()}"
)

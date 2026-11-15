"""Lay copied PNGs side by side on a checkerboard so transparency shows.

usage: sheet.py <out.png> <title> <label=path>...
Each tile shows the PNG scaled to a common height, with its label, pixel size and file size.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

out, title, items = sys.argv[1], sys.argv[2], [a.split("=", 1) for a in sys.argv[3:]]
TILE_H, PAD, TEXT_H = 360, 24, 64
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)

tiles = []
for label, path in items:
    img = Image.open(path).convert("RGBA")
    w = round(img.width * TILE_H / img.height)
    tiles.append((label, img.resize((w, TILE_H), Image.LANCZOS), img.size, os.path.getsize(path)))

width = PAD + sum(t[1].width + PAD for t in tiles)
sheet = Image.new("RGB", (width, 60 + TILE_H + TEXT_H + PAD), "white")
draw = ImageDraw.Draw(sheet)
draw.text((PAD, 16), title, fill="black", font=bold)
x = PAD
for label, img, (pw, ph), size in tiles:
    y = 60
    for cy in range(0, TILE_H, 16):
        for cx in range(0, img.width, 16):
            shade = 204 if (cx // 16 + cy // 16) % 2 else 255
            draw.rectangle([x + cx, y + cy, min(x + cx + 15, x + img.width - 1), min(y + cy + 15, y + TILE_H - 1)], fill=(shade,) * 3)
    sheet.paste(img, (x, y), img)
    draw.rectangle([x - 1, y - 1, x + img.width, y + TILE_H], outline=(150, 150, 150))
    draw.text((x, y + TILE_H + 8), label, fill="black", font=font)
    draw.text((x, y + TILE_H + 36), f"{pw} x {ph} px, {size / 1024:.0f} KB", fill=(90, 90, 90), font=font)
    x += img.width + PAD
sheet.save(out)
print(out, sheet.size)

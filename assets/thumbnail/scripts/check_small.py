"""Readability check sheets.

    python check_small.py <image.png> <sheet.png> [<small.png>]   16:9: full size next to 256x144
    python check_small.py --icon <icon.png> <sheet.png>            square: 512, 128 and 64 px

The small versions are shown at actual size and again enlarged with nearest-neighbour scaling,
so you see exactly the pixels a viewer gets.
"""
import sys
from PIL import Image, ImageDraw

BG, FG = (28, 28, 34), (220, 220, 230)
args = sys.argv[1:]
if args and args[0] == "--icon":
    src, sheet_path = args[1], args[2]
    im = Image.open(src).convert("RGB")
    i512 = im.resize((512, 512), Image.LANCZOS)
    i128 = im.resize((128, 128), Image.LANCZOS)
    i64 = im.resize((64, 64), Image.LANCZOS)
    sheet = Image.new("RGB", (512 + 24 + 384 + 24 + 24, 512 + 48), BG)
    sheet.paste(i512, (12, 36))
    x = 512 + 36
    sheet.paste(i128, (x, 36))
    sheet.paste(i64, (x + 128 + 24, 36))
    sheet.paste(i128.resize((384, 384), Image.NEAREST), (x, 36 + 128 + 24))
    d = ImageDraw.Draw(sheet)
    d.text((12, 12), "icon 512x512", fill=FG)
    d.text((x, 12), "128 and 64 px, actual size", fill=FG)
    d.text((x, 36 + 128 + 6), "128 px, 3x", fill=FG)
    sheet.save(sheet_path)
    sys.exit(0)

src, sheet_path = args[0], args[1]
im = Image.open(src).convert("RGB")
small = im.resize((256, 144), Image.LANCZOS)
if len(args) > 2:
    small.save(args[2])
big = im.resize((1280, 720), Image.LANCZOS)
zoom = small.resize((768, 432), Image.NEAREST)
W = 1280 + 24 + 768
sheet = Image.new("RGB", (W + 24, 720 + 48), BG)
sheet.paste(big, (12, 36))
sheet.paste(small, (1280 + 36, 36))
sheet.paste(zoom, (1280 + 36, 36 + 144 + 30))
d = ImageDraw.Draw(sheet)
d.text((12, 12), "full size (shown at 1280x720)", fill=FG)
d.text((1280 + 36, 12), "256x144, actual size", fill=FG)
d.text((1280 + 36, 36 + 144 + 8), "the same 256x144 pixels, 3x", fill=FG)
sheet.save(sheet_path)

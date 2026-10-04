"""
compare.py - BEFORE | AFTER pictures side by side (same camera), for REPORT.md.

    /home/user/bvenv/bin/python tools/compare.py            (every image that exists in both folders)

Reads renders/before/<name>.png and renders/after/<name>.png, writes renders/compare/<name>.jpg.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
BEFORE = os.path.join(ROOT, "renders", "before")
AFTER = os.path.join(ROOT, "renders", "after")
OUT = os.path.join(ROOT, "renders", "compare")


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def pair(name, width=1100):
    a = Image.open(os.path.join(BEFORE, name)).convert("RGB")
    b = Image.open(os.path.join(AFTER, name)).convert("RGB")
    h = int(a.height * width / a.width)
    a, b = a.resize((width, h), Image.LANCZOS), b.resize((width, h), Image.LANCZOS)
    bar = 36
    out = Image.new("RGB", (width * 2 + 8, h + bar), (40, 26, 58))
    out.paste(a, (0, bar))
    out.paste(b, (width + 8, bar))
    d = ImageDraw.Draw(out)
    f = font(22)
    d.text((10, 6), "BEFORE", fill=(255, 255, 255), font=f)
    d.text((width + 18, 6), "AFTER", fill=(255, 214, 92), font=f)
    d.text((width * 2 - 330, 8), os.path.splitext(name)[0], fill=(210, 215, 235), font=font(16))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, os.path.splitext(name)[0] + ".jpg")
    out.save(path, quality=88, optimize=True)
    return path


def main():
    names = sorted(n for n in os.listdir(BEFORE) if n.endswith(".png") and os.path.exists(os.path.join(AFTER, n)))
    for n in names:
        print(pair(n))


if __name__ == "__main__":
    main()

"""
contact_sheet.py - a grid of model renders with names (for review and for REPORT.md).

    python3 tools/contact_sheet.py <out.png> [--view front34|back34|eye] [--cols N] template ...
    python3 tools/contact_sheet.py <out.png> --all          (every built model, in plan order)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def main():
    args = sys.argv[1:]
    out = args.pop(0)
    view, cols, cell = "front34", 4, 400
    names = []
    while args:
        a = args.pop(0)
        if a == "--view":
            view = args.pop(0)
        elif a == "--cols":
            cols = int(args.pop(0))
        elif a == "--cell":
            cell = int(args.pop(0))
        elif a == "--all":
            plan = json.load(open(os.path.join(ROOT, "data", "plan.json")))
            status = json.load(open(os.path.join(ROOT, "data", "model_status.json")))
            names = [n for n in plan["order"] if n in status and status[n].get("renders")]
        else:
            names.append(a)
    status = json.load(open(os.path.join(ROOT, "data", "model_status.json")))
    w, h = cell, int(cell * 0.75)
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 28)), (60, 70, 100))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    for i, name in enumerate(names):
        path = os.path.join(ROOT, "renders", "objects", name, "%s_%s.jpg" % (name, view))
        if not os.path.exists(path):
            path = path[:-4] + ".png"
        x, y = (i % cols) * w, (i // cols) * (h + 28)
        if os.path.exists(path):
            img = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
            sheet.paste(img, (x, y))
        e = status.get(name, {})
        label = "%s  %s tris  [%s]" % (name, e.get("triangles", "?"), e.get("status", ""))
        d.text((x + 6, y + h + 5), label, fill=(255, 255, 255), font=font)
    sheet.save(out)
    print("sheet", out, len(names))


if __name__ == "__main__":
    main()

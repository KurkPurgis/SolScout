"""
png_to_jpg.py - converts any leftover PNG renders in renders/objects/ to JPG (replacing an older JPG).

    /home/user/bvenv/bin/python tools/png_to_jpg.py
"""
import glob
import os

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
n = 0
for p in glob.glob(os.path.join(ROOT, "renders", "objects", "**", "*.png"), recursive=True):
    Image.open(p).convert("RGB").save(p[:-4] + ".jpg", quality=88, optimize=True)
    os.remove(p)
    n += 1
print("converted", n)

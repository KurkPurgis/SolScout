"""Rags to Riches thumbnail - finishing: outlines, near coins, title, colour grade.

Run after build_thumbnail.py (same Python with bpy, numpy, scipy, Pillow):
    python finish.py --passes <dir with the .exr passes> --out <assets/thumbnail>

Steps, on the linear HDR passes:
  1. bloom from the bright glow (blurred highlights added back, warm)
  2. exposure, then display encoding (sRGB) with a soft shoulder instead of a hard clip
  3. grade: more contrast (S-curve) and saturation, slight vignette
  4. INK outline (the palette's icon-outline colour) around the character, the dream (yacht,
     chains, padlock, price tag) and the debt number: grown from the matte pass, skipped where
     something nearer than the outlined object covers the pixel (depth pass)
  5. the near coin (own pass), lightly blurred and laid on top
  6. text version: the title drawn flat on top - white letters, a dark navy outline grown from
     the letter shapes (so letters never overlap), a soft drop shadow, tracked spacing
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY

ap = argparse.ArgumentParser()
ap.add_argument("--passes", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--prefix", default="main")
ap.add_argument("--name", default="thumbnail_1920x1080.png")
ap.add_argument("--text-name", default="thumbnail_text.png")
ap.add_argument("--size", default="")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
A = ap.parse_args(argv)

INK = np.array([40, 26, 58], np.float32) / 255.0


def load_exr(path):
    import bpy
    im = bpy.data.images.load(path)
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1].copy()


def blur(img, sigma):
    if img.ndim == 2:
        return ndimage.gaussian_filter(img, sigma)
    return np.stack([ndimage.gaussian_filter(img[..., c], sigma) for c in range(img.shape[2])], -1)


def to_display(lin):
    """Linear -> display: soft shoulder above 0.8 (keeps the glow from clipping flat), sRGB encode."""
    x = np.maximum(lin, 0.0)
    k = 0.8
    over = x > k
    x = np.where(over, k + (1 - k) * (1 - np.exp(-(x - k) / (1 - k))), x)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def grade(d, contrast=0.32, sat=1.35, vignette=0.16):
    lum = (d * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    d = lum + (d - lum) * sat                                     # saturation
    d = np.clip(d, 0, 1)
    s = d * d * (3 - 2 * d)                                       # S-curve (smoothstep)
    d = d + (s - d) * contrast
    h, w = d.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    d = d * (1 - vignette * np.clip(r - 0.35, 0, 1) ** 1.6 / 0.42)[..., None]
    return np.clip(d, 0, 1)


def outline(img, matte, depth, width, colour=INK, softness=1.0, front_only=True, close=0):
    """Draws `colour` around the matte's silhouette, `width` px thick, behind the object itself and
    not over anything nearer to the camera than the object at that spot. `close` (px) first fills
    small gaps (between chain links, railings) so the line follows the overall silhouette."""
    solid = matte > 0.5
    if not solid.any():                               # nothing of this group in frame (e.g. the icon)
        return img, np.zeros(matte.shape, np.float32)
    if close >= 1:
        r = int(round(close))
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        disk = (xx * xx + yy * yy) <= r * r
        solid = ndimage.binary_closing(solid, structure=disk)
    dist, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
    a = np.clip((width + 0.5 - dist) / softness, 0, 1)             # anti-aliased outer edge
    if front_only and depth is not None:
        own = depth[iy, ix]                                        # depth of the nearest object pixel
        a = a * (depth >= own - 0.05 * own).astype(np.float32)     # skip what is in front of it
    # stays behind the object, but covers its half-transparent edge pixels (no light seam)
    m = np.clip((matte - 0.55) / 0.45, 0, 1)
    a = a * (1 - m * m * (3 - 2 * m))
    return img * (1 - a[..., None]) + colour * a[..., None], a


def over(dst, rgba):
    a = rgba[..., 3:4]
    return dst * (1 - a) + rgba[..., :3] * a


P = lambda n: os.path.join(A.passes, f"{A.prefix}_{n}.exr")
beauty = load_exr(P("beauty"))
H, W = beauty.shape[:2]
scale = H / 1080.0                    # outline/blur sizes are tuned for a 1080 px tall frame
matte = load_exr(P("matte"))
depth = load_exr(P("depth"))[..., 0]
depth[depth <= 0] = 1e9                                            # sky = far away

# 1. bloom from the HDR glow and rays only (the subjects themselves are masked out), warm tinted
lin = beauty[..., :3]
subjects = np.clip(matte[..., 0] + matte[..., 1] + matte[..., 2], 0, 1)
lum = (lin * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1)
hi = lin * (np.clip(lum - 1.3, 0, None) / np.maximum(lum, 1e-4))[..., None] * (1 - subjects)[..., None]
bloom = blur(hi, 22 * scale) * 0.5 + blur(hi, 70 * scale) * 0.5
lin = lin + bloom * np.array([1.0, 0.8, 0.5], np.float32) * 0.7

# 2-3. display + grade
img = grade(to_display(lin * 1.05))

# 4. outlines (character, dream, debt number), thickness in px at 1920 wide
for ch, wpx, cl in ((0, 9.0, 2), (1, 8.0, 6), (2, 13.5, 0)):
    img, _ = outline(img, matte[..., ch], depth, wpx * scale, close=cl * scale)

# 5. the near coin, lightly blurred (shallow depth of field)
near_path = P("near")
if os.path.exists(near_path):
    near = load_exr(near_path)
    rgb = to_display(near[..., :3] / np.maximum(near[..., 3:4], 1e-4)) * (near[..., 3:4] > 0)
    rgb = grade(rgb, vignette=0.0)
    prem = np.concatenate([rgb * near[..., 3:4], near[..., 3:4]], -1)
    prem = blur(prem, 2.6 * scale)
    a = prem[..., 3:4]
    img = img * (1 - a) + prem[..., :3]
img = np.clip(img, 0, 1)


def save(arr, name):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))
    if A.size:                                            # e.g. "512x512": render big, shrink cleanly
        im = im.resize(tuple(int(v) for v in A.size.split("x")), Image.LANCZOS)
    im.save(os.path.join(A.out, name))
    return os.path.join(A.out, name)


out_plain = save(img, A.name)

# 6. text version: the title, drawn flat
def draw_title(base):
    TI = LY.F_TITLE
    h, w = base.shape[:2]
    font_path = os.path.join(HERE, "fonts", "Fredoka-Bold.ttf")
    probe = ImageFont.truetype(font_path, 200)
    _, t_, _, b_ = probe.getbbox("H")
    cap_ratio = (b_ - t_) / 200.0                       # cap height per unit of font size
    layer = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(layer)
    y = h * 0.2
    for text, cap in TI["lines"]:
        size = cap * h / cap_ratio
        f = ImageFont.truetype(font_path, int(round(size)))
        top_off = f.getbbox("H")[1]
        x = w * 0.2
        for ch in text:                                 # tracked: room for the outline between letters
            d.text((x, y - top_off), ch, font=f, fill=255)
            x += f.getlength(ch) + TI["tracking"] * size
        y += cap * h * 1.36
    layer = layer.rotate(TI["tilt"], resample=Image.BICUBIC, center=(w * 0.2, h * 0.2))
    fill = np.asarray(layer).astype(np.float32) / 255.0
    stroke = TI["stroke"] * h
    solid = fill > 0.5
    rim = np.clip(stroke + 0.5 - ndimage.distance_transform_edt(~solid), 0, 1)
    rim = np.maximum(rim, fill)
    # move the block so its outline's top-left sits on the safe-area corner
    ys, xs = np.nonzero(rim > 0.02)
    sy = int(round((1 - TI["top"]) * h - ys.min()))
    sx = int(round(TI["left"] * w - xs.min()))
    fill = np.roll(np.roll(fill, sy, 0), sx, 1)
    rim = np.roll(np.roll(rim, sy, 0), sx, 1)
    dx, dy, sb, so = TI["shadow"]
    shadow = ndimage.shift(rim, (dy * h, dx * h), order=1)
    shadow = ndimage.gaussian_filter(shadow, sb * h) * so
    navy = np.array(TI["outline"], np.float32) / 255.0
    white = np.array(TI["fill"], np.float32) / 255.0
    out = base * (1 - shadow[..., None]) + navy * shadow[..., None]
    out = out * (1 - rim[..., None]) + navy * rim[..., None]
    out = out * (1 - fill[..., None]) + white * fill[..., None]
    return out


if A.text_name:
    save(draw_title(img), A.text_name)
print("wrote", out_plain)

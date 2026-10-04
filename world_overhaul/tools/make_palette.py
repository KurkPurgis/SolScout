"""
make_palette.py - the ONE palette every model in the world uses.

Writes:
  palette/palette_color.png      256 x 128, 8 x 4 swatches of 32 x 32 px   (SurfaceAppearance.ColorMap)
  palette/palette_roughness.png  same layout, grey = roughness              (SurfaceAppearance.RoughnessMap)
  palette/palette.json           name -> index, rgb, roughness, uv (center of the swatch)
  palette/palette_sheet.png      big labelled preview for people

Every face of every model has its UVs on the CENTER of one swatch, so the whole world shares one texture.
Colors come from assets/icons_3d/scripts/icon_defs.py (named the same where possible); a few world-only
colors (grass, stone) were added. Run with any Python that has Pillow.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "palette")

COLS, ROWS, SW = 8, 4, 32

# (name, sRGB, roughness, where it comes from / what it is for)
PALETTE = [
    # row 1 - warm
    ("CREAM", (250, 240, 220), 0.40, "warm white: walls, marble, sofas (icon PAPER/WHITE, warmer for the world)"),
    ("GOLD_LIGHT", (255, 214, 92), 0.30, "icon GOLD_LIGHT: highlights, school walls, lamps' casing"),
    ("GOLD", (255, 182, 34), 0.25, "icon GOLD: money, trophies, gold trim"),
    ("ORANGE", (244, 136, 20), 0.30, "icon GOLD_ORANGE/FACTORY: garage, padlock, cones"),
    ("RED", (236, 66, 78), 0.30, "icon RED: roofs, cars, awnings"),
    ("BRICK", (186, 40, 48), 0.35, "icon SIGN_RED: pizzeria walls, deep red details"),
    ("PINK", (255, 120, 170), 0.30, "flowers, toy shop, kids' shirts"),
    ("SKIN", (245, 200, 160), 0.45, "kids' faces and hands"),
    # row 2 - cool
    ("WHITE", (234, 238, 248), 0.30, "icon WHITE (cool off-white, never pure white): trims, fences, hospital"),
    ("SKY", (110, 190, 250), 0.25, "icon SKY: windows, glass panes, water details"),
    ("BLUE", (44, 116, 222), 0.30, "icon BOOK_BLUE/CARD_BLUE: bus depot, office, signs"),
    ("NAVY", (34, 52, 120), 0.30, "icon NAVY: police, lobby walls, yacht hull"),
    ("TEAL", (40, 186, 176), 0.30, "clinic walls, accents"),
    ("PURPLE", (146, 84, 226), 0.30, "game studio, epic cards, podium room"),
    ("WINDOW", (160, 214, 250), 0.15, "icon WINDOW_LIGHT: shiny window panes"),
    ("STEEL", (128, 130, 154), 0.30, "icon STEEL/SILVER: metal, lamp posts, office walls"),
    # row 3 - nature and earth
    ("LEAF", (52, 170, 74), 0.45, "icon LEAF_GREEN: tree crowns, palm leaves"),
    ("GREEN", (88, 208, 96), 0.30, "icon GREEN: bright accents, pizzeria awning, money"),
    ("GRASS", (104, 186, 84), 0.80, "world only: the ground (matte so it never shines)"),
    ("GREEN_DARK", (38, 132, 64), 0.35, "icon GREEN_DARK: school accent, blackboard frame"),
    ("SAND", (236, 200, 128), 0.75, "icon SAND (lighter): sandbox, lots, beach"),
    ("TAN", (214, 150, 80), 0.45, "icon CRUST: light wood, cardboard, desks"),
    ("WOOD", (170, 98, 44), 0.45, "icon WOOD: furniture, chests, trunks"),
    ("WOOD_DARK", (112, 60, 26), 0.50, "icon WOOD_DARK: trunks, dark wood"),
    # row 4 - neutrals and special
    ("STONE", (226, 218, 200), 0.70, "world only: plaza, paths, yard"),
    ("STONE_DARK", (176, 166, 150), 0.70, "world only: city wall, steps, pads"),
    ("SLATE", (104, 108, 132), 0.50, "icon ROOF_GREY: dark grey roofs, debt pad, bank"),
    ("CHARCOAL", (58, 52, 76), 0.35, "icon TYRE/DARK: tires, openings, piano, screens off"),
    ("INK", (40, 26, 58), 0.40, "icon OUTLINE color: tiny dark details and the optional outline"),
    ("WATER", (60, 160, 240), 0.10, "icon WATER: fountain, pools, sea"),
    ("GLOW_WARM", (255, 236, 160), 0.50, "Neon only: lamps, lit windows (MeshPart.Color with Material Neon)"),
    ("GLOW_COOL", (130, 230, 255), 0.50, "Neon only: screens, portals (MeshPart.Color with Material Neon)"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    color = Image.new("RGB", (COLS * SW, ROWS * SW))
    rough = Image.new("L", (COLS * SW, ROWS * SW))
    draw_c, draw_r = ImageDraw.Draw(color), ImageDraw.Draw(rough)
    data = {"columns": COLS, "rows": ROWS, "swatch_px": SW, "size_px": [COLS * SW, ROWS * SW], "colors": {}}
    for index, (name, rgb, roughness, note) in enumerate(PALETTE):
        col, row = index % COLS, index // COLS
        box = [col * SW, row * SW, col * SW + SW - 1, row * SW + SW - 1]
        draw_c.rectangle(box, fill=rgb)
        draw_r.rectangle(box, fill=int(round(roughness * 255)))
        u = (col + 0.5) / COLS
        v = 1 - (row + 0.5) / ROWS  # Blender/Roblox UV: v = 0 at the bottom of the image
        data["colors"][name] = {"index": index, "rgb": list(rgb), "hex": "#%02X%02X%02X" % rgb,
                                "roughness": roughness, "uv": [round(u, 5), round(v, 5)], "note": note}
    color.save(os.path.join(OUT, "palette_color.png"))
    rough.save(os.path.join(OUT, "palette_roughness.png"))
    json.dump(data, open(os.path.join(OUT, "palette.json"), "w"), indent=1)

    # human preview
    cell_w, cell_h = 200, 120
    sheet = Image.new("RGB", (COLS * cell_w, ROWS * cell_h), (60, 70, 100))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
        small = ImageFont.truetype("DejaVuSans.ttf", 12)
    except OSError:
        font = small = ImageFont.load_default()
    for index, (name, rgb, roughness, note) in enumerate(PALETTE):
        col, row = index % COLS, index // COLS
        x, y = col * cell_w, row * cell_h
        d.rounded_rectangle([x + 8, y + 8, x + cell_w - 8, y + cell_h - 40], radius=14, fill=rgb, outline=(40, 26, 58), width=3)
        d.text((x + 12, y + cell_h - 36), "%d %s" % (index, name), fill=(255, 255, 255), font=font)
        d.text((x + 12, y + cell_h - 18), "#%02X%02X%02X  r%.2f" % (rgb + (roughness,)), fill=(210, 215, 235), font=small)
    sheet.save(os.path.join(OUT, "palette_sheet.png"))
    print("palette:", len(PALETTE), "colors")


if __name__ == "__main__":
    main()

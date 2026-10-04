"""
parts.py - the shared kit parts (STYLE_GUIDE section 4). Built once, used by every model.
All coordinates are Roblox local (x right, y up, z back; front = -Z).
"""

import math

from kit import deg, rb_angles

# Workplace themes (STYLE_GUIDE section 2): wall / accent / floor, from Themes.luau moved to the palette
THEMES = {
    "PIZZERIA": dict(wall="BRICK", accent="GREEN", floor="CREAM", trim="WHITE", sign_text="WHITE"),
    "BUSDEPOT": dict(wall="BLUE", accent="GOLD", floor="SLATE", trim="WHITE", sign_text="WHITE"),
    "HOSPITAL": dict(wall="WHITE", accent="RED", floor="SKY", trim="RED", sign_text="WHITE"),
    "CLINIC": dict(wall="TEAL", accent="WHITE", floor="WHITE", trim="WHITE", sign_text="WHITE"),
    "SCHOOL": dict(wall="GOLD_LIGHT", accent="GREEN_DARK", floor="TAN", trim="WHITE", sign_text="WHITE"),
    "POLICE": dict(wall="NAVY", accent="WHITE", floor="STONE", trim="WHITE", sign_text="WHITE"),
    "OFFICE": dict(wall="STEEL", accent="BLUE", floor="WHITE", trim="WHITE", sign_text="WHITE"),
    "GARAGE": dict(wall="ORANGE", accent="CHARCOAL", floor="SLATE", trim="WHITE", sign_text="WHITE"),
    "FASTTRACK": dict(wall="CREAM", accent="GOLD", floor="CREAM", trim="GOLD", sign_text="WHITE"),
}


def window(m, center, w, h, facing="-Z", frame="WHITE", pane="WINDOW", depth=0.5, sill=True, cross=False,
           frame_w=0.45):
    """A window like the icons: a shiny pane in front of a thicker rounded frame slab (+ sill).
    center = middle of the pane, on the wall surface. facing: "-Z" front, "+Z" back, "-X" left, "+X" right."""
    yaw = {"-Z": 0, "+Z": 180, "-X": 90, "+X": -90}[facing]
    fw = frame_w
    with m.at(center, yaw):
        m.box((w + 2 * fw, h + 2 * fw, depth), (0, 0, -depth / 2 + 0.2), frame, bevel="S")
        m.box((w, h, 0.3), (0, 0, -depth + 0.2 - 0.05), pane, bevel="S")
        if cross:
            m.box((0.3, h, 0.3), (0, 0, -depth + 0.2 - 0.2), frame, bevel="XS")
            m.box((w, 0.3, 0.3), (0, 0, -depth + 0.2 - 0.2), frame, bevel="XS")
        if sill:
            m.box((w + 2 * fw + 0.4, 0.35, 0.6), (0, -h / 2 - fw - 0.1, -depth + 0.2 - 0.1), frame, bevel="S")


def door(m, bottom_center, w, h, facing="-Z", color="WOOD", frame="WHITE", knob="GOLD", mat=True):
    """A door with a frame and a gold knob (+ a doormat: the detail every door gets)."""
    yaw = {"-Z": 0, "+Z": 180, "-X": 90, "+X": -90}[facing]
    with m.at(bottom_center, yaw):
        m.box((w, h, 0.35), (0, h / 2, 0.05), color, bevel="S")
        m.box((w * 0.62, h * 0.32, 0.3), (0, h * 0.68, -0.05), color, bevel="S")  # raised panel
        m.box((w + 0.8, 0.4, 0.5), (0, h + 0.2, -0.1), frame, bevel="S")
        m.box((0.4, h, 0.5), (-w / 2 - 0.2, h / 2, -0.1), frame, bevel="S")
        m.box((0.4, h, 0.5), (w / 2 + 0.2, h / 2, -0.1), frame, bevel="S")
        m.sphere(0.18, (w * 0.32, h * 0.46, -0.2), knob, segs=10, rings=6)
        if mat:
            m.box((w * 0.9, 0.3, 1.0), (0, 0.15, -0.75), "RED", bevel="S")


def sign_board(m, center, w, h, board, frame="WHITE", frame_w=0.5, depth=0.6, text_plane_z=None, bolts=True):
    """A sign: the board (the SurfaceGui text of the old, now invisible, sign part shows on it) in front of a
    bigger rounded frame slab. center = center of the text area; text_plane_z = z of the old part's front face
    (the board's front stays 0.06 behind it, so the text is never hidden)."""
    cx, cy, cz = center
    front = text_plane_z if text_plane_z is not None else cz - depth / 2
    board_front = front + 0.06
    m.box((w, h, depth), (cx, cy, board_front + depth / 2), board, bevel="S")
    fw = frame_w
    m.box((w + 2 * fw, h + 2 * fw, depth), (cx, cy, board_front + depth / 2 + 0.25), frame, bevel="M")
    if bolts:  # the detail: four round gold bolts in the frame corners
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.sphere(0.17, (cx + sx * (w / 2 + fw / 2), cy + sy * (h / 2 + fw / 2), board_front + 0.18),
                         "GOLD", segs=8, rings=4)


def bulb(m, center, radius, glow="GLOW_WARM", cap="STEEL"):
    """A glowing lamp bulb with a little cap on top."""
    cx, cy, cz = center
    m.sphere(radius, center, glow, glow=glow, segs=10, rings=6)
    m.cyl(radius * 0.7, radius * 0.5, (cx, cy + radius * 0.85, cz), cap, bevel="XS", verts=10)


def stripes_awning(m, x0, x1, n, y_top, y_bottom, z_back, z_front, colors, thick=0.45, lip=0.38):
    """Striped awning: n sloped stripes from (y_top, z_back) down to (y_bottom, z_front), with a rolled lip."""
    width = (x1 - x0) / n
    dz = z_back - z_front
    dy = y_top - y_bottom
    length = math.hypot(dz, dy - lip)
    angle = math.atan2(dy - lip, dz)  # slope down toward the front
    for i in range(n):
        color = colors[i % len(colors)]
        cx = x0 + (i + 0.5) * width
        mid_z = (z_back + z_front + lip) / 2
        mid_y = (y_top + y_bottom + lip) / 2 - thick / 2
        m.box((width - 0.06, thick, length), (cx, mid_y, mid_z), color, bevel="XS",
              rot=rb_angles(-angle, 0, 0))
        m.cyl(lip, width - 0.06, (cx, y_bottom + lip, z_front + lip), color, axis="X", bevel="XS", verts=12)


def pillar(m, bottom, height, w, color, cap="WHITE", base=None, cap_w=None, cap_h=0.6):
    """A chunky square pillar with a rounded cap (and optional base)."""
    x, y, z = bottom
    m.box((w, height, w), (x, y, z), color, bevel="L", bottom=True)
    cw = cap_w or (w + 0.6)
    m.box((cw, cap_h, cw), (x, y + height, z), cap, bevel="M", bottom=True)
    if base:
        m.box((w + 0.4, 0.6, w + 0.4), (x, y, z), base, bevel="M", bottom=True)


def wheel(m, center, radius, width, axis="X", hub="STEEL", cap="RED", tyre="CHARCOAL"):
    """A chunky toy wheel: fat tire, steel hub, colored cap (icon wheel)."""
    cx, cy, cz = center
    m.cyl(radius, width, center, tyre, axis=axis, bevel=min(0.45 * width, radius * 0.35), verts=20)
    side = width / 2 + 0.02
    off = {"X": (side, 0, 0), "Z": (0, 0, side)}[axis]
    for s in (-1, 1):
        p = (cx + s * off[0], cy, cz + s * off[2])
        m.cyl(radius * 0.5, 0.12 + 0.18, p, hub, axis=axis, bevel="XS", verts=14)
        p2 = (cx + s * (off[0] + 0.12 * (1 if off[0] else 0)), cy, cz + s * (off[2] + 0.12 * (1 if off[2] else 0)))
        m.cyl(radius * 0.22, 0.3, p2, cap, axis=axis, bevel="XS", verts=10)


def round_tree(m, base, trunk_h, trunk_r, crown_r, trunk="WOOD", leaf="LEAF", leaf2="GREEN"):
    """A toy tree: tapered trunk, one big crown with two smaller bumps (reads as a cloud of leaves)."""
    x, y, z = base
    m.cyl(trunk_r, trunk_h, (x, y, z), trunk, bevel="S", bottom=True, radius_top=trunk_r * 0.75, verts=12)
    cy = y + trunk_h + crown_r * 0.55
    m.sphere(crown_r, (x, cy, z), leaf, segs=18, rings=12)


def bush(m, center, r, color="LEAF"):
    m.sphere(r, center, color, scale=(1, 0.8, 1), segs=12, rings=8)


def flower(m, center, r, petal="PINK", heart="GOLD_LIGHT"):
    cx, cy, cz = center
    m.sphere(r, center, petal, scale=(1, 0.75, 1), segs=12, rings=8)
    m.sphere(r * 0.4, (cx, cy + r * 0.6, cz), heart, segs=8, rings=6)


def lamp_post(m, bottom, height, bulb_r, post="STEEL", base="CHARCOAL", glow="GLOW_WARM"):
    x, y, z = bottom
    m.cyl(0.55, 0.6, (x, y, z), base, bevel="S", bottom=True, verts=14)
    m.cyl(0.22, height - bulb_r * 2 - 0.4, (x, y + 0.6, z), post, bevel="XS", bottom=True, verts=10)
    bulb(m, (x, y + height - bulb_r, z), bulb_r, glow=glow, cap=post)


def chunky_rail(m, x0, x1, y, z, thick, color):
    """A horizontal round rail along X."""
    m.capsule(thick / 2, abs(x1 - x0) + thick, ((x0 + x1) / 2, y, z), color, axis="X", segs=10)

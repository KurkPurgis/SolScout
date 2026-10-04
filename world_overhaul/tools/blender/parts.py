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


def sign_board(m, center, w, h, board, frame="WHITE", frame_w=0.5, depth=0.6, text_plane_z=None, bolts=True,
               frame_back=0.25):
    """A sign: the board (the SurfaceGui text of the old, now invisible, sign part shows on it) in front of a
    bigger rounded frame slab. center = center of the text area; text_plane_z = z of the old part's front face
    (the board's front stays 0.06 behind it, so the text is never hidden)."""
    cx, cy, cz = center
    front = text_plane_z if text_plane_z is not None else cz - depth / 2
    board_front = front + 0.06
    m.box((w, h, depth), (cx, cy, board_front + depth / 2), board, bevel="S")
    fw = frame_w
    m.box((w + 2 * fw, h + 2 * fw, depth), (cx, cy, board_front + depth / 2 + frame_back), frame, bevel="M")
    if bolts:  # the detail: four round gold bolts in the frame corners
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.sphere(0.17, (cx + sx * (w / 2 + fw / 2), cy + sy * (h / 2 + fw / 2), board_front + 0.18),
                         "GOLD", segs=8, rings=4)


def bulb(m, center, radius, glow="GLOW_WARM", cap="STEEL"):
    """A glowing lamp bulb with a little cap on top."""
    cx, cy, cz = center
    m.sphere(radius, center, glow, glow=glow, segs=10, rings=6)
    m.cyl(radius * 0.7, max(radius * 0.5, 0.3), (cx, cy + radius * 0.85, cz), cap, bevel="XS", verts=10)


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
    """A chunky toy wheel: fat tire, steel hub, colored cap (icon wheel). cap=None: small wheel, one hub."""
    cx, cy, cz = center
    m.cyl(radius, width, center, tyre, axis=axis, bevel=min(0.45 * width, radius * 0.35), verts=20)
    if cap is None:
        m.cyl(radius * 0.5, width + 0.12, center, hub, axis=axis, bevel=None, verts=10)
        return
    # hub ring just proud of the tire face, cap 0.13 out: the wheel stays inside the original wheel's box
    side = width / 2 - 0.02
    off = {"X": (1, 0, 0), "Z": (0, 0, 1)}[axis]
    for s in (-1, 1):
        p = (cx + s * off[0] * (side - 0.1), cy, cz + s * off[2] * (side - 0.1))
        m.cyl(radius * 0.5, 0.3, p, hub, axis=axis, bevel="XS", verts=14)
        p2 = (cx + s * off[0] * side, cy, cz + s * off[2] * side)
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


def palm_leaf(m, top, azimuth, length, color="LEAF", thick=0.3, droop=0.95, rise=0.35, width=0.26, steps=10):
    """One drooping, folded palm leaf like the icon palm (a closed, 0.3-thick shape)."""
    import math as _m
    d = (_m.cos(azimuth), 0.0, _m.sin(azimuth))
    side = (-_m.sin(azimuth), 0.0, _m.cos(azimuth))
    tx, ty, tz = top
    rows_top, rows_bot = [], []
    for i in range(steps + 1):
        t = 0.04 + 0.96 * i / steps
        cx = tx + d[0] * length * t
        cz = tz + d[2] * length * t
        cy = ty + length * (rise * t - droop * t * t)
        w = width * length * _m.sin(_m.pi * t) ** 0.8 + 0.08
        fold = 0.3 * w
        row = [(cx - side[0] * w, cy + fold, cz - side[2] * w), (cx, cy, cz), (cx + side[0] * w, cy + fold, cz + side[2] * w)]
        rows_top.append(row)
        rows_bot.append([(x, y - thick, z) for x, y, z in row])
    verts = [v for row in rows_top for v in row] + [v for row in rows_bot for v in row]
    n = steps + 1
    off = 3 * n
    faces = []
    for i in range(steps):
        a, b = 3 * i, 3 * (i + 1)
        faces += [(a, a + 1, b + 1, b), (a + 1, a + 2, b + 2, b + 1)]
        faces += [(off + b, off + b + 1, off + a + 1, off + a), (off + b + 1, off + b + 2, off + a + 2, off + a + 1)]
        faces += [(a, b, off + b, off + a), (a + 2, off + a + 2, off + b + 2, b + 2)]
    faces += [(0, off, off + 1, 1), (1, off + 1, off + 2, 2)]
    last = 3 * steps
    faces += [(last, last + 1, off + last + 1, off + last), (last + 1, last + 2, off + last + 2, off + last + 1)]
    m.custom(verts, faces, color)


def palm(m, base, height, lean=1.5, leaf_length=4.2, leaves=6, trunk="WOOD", leaf="LEAF", coconuts=True,
         trunk_r=0.42, lean_dir=(1.0, 0.0), segs=6, leaf_steps=8, trunk_verts=10):
    """Icon palm: a curved trunk of stacked tapered segments (ringed look) and drooping leaves.
    base = bottom of the trunk (Roblox local); the top bends `lean` studs toward lean_dir (x, z)."""
    import math as _m
    bx, by, bz = base
    ldx, ldz = lean_dir
    pts = []
    for i in range(segs + 1):
        f = i / segs
        pts.append((bx + ldx * lean * f * f, by + height * f, bz + ldz * lean * f * f))
    for i in range(segs):
        a, b = pts[i], pts[i + 1]
        r0 = trunk_r * (1 - 0.35 * i / segs)
        # each segment slightly wider at its bottom: the ringed trunk of the icon
        ext = (b[0] + (b[0] - a[0]) * 0.12, b[1] + (b[1] - a[1]) * 0.12, b[2] + (b[2] - a[2]) * 0.12)
        m.stick(a, ext, r0, trunk, radius_b=r0 * 0.78, verts=trunk_verts, bevel=None)
    top = pts[-1]
    for k in range(leaves):
        az = 2 * _m.pi * k / leaves + 0.3
        palm_leaf(m, (top[0], top[1] + 0.25, top[2]), az, leaf_length, color=leaf if k % 2 == 0 else "GREEN",
                  steps=leaf_steps)
    m.sphere(0.45, (top[0], top[1] + 0.1, top[2]), leaf, segs=10, rings=6)
    if coconuts:
        for k in range(3):
            az = 2 * _m.pi * k / 3 + 1.0
            m.sphere(0.32, (top[0] + 0.45 * _m.cos(az), top[1] - 0.35, top[2] + 0.45 * _m.sin(az)), "WOOD_DARK",
                     segs=8, rings=5)


def shop(m, size, wall, sign_color, window, awning=("WHITE", "WHITE"), door="WOOD", glass_window=False,
         sign_frame="WHITE"):
    """Props.luau shop(): a box with a big front window, a white awning and a sign (all Money Maker shops).
    size = (x, y, z); front = -Z. Window y 0.6..0.6+0.45h, awning at 0.62h, sign at 0.82h."""
    sx, sy, sz = size
    m.box((sx, sy - 0.2, sz), (0, 0, 0), wall, bevel="L", bottom=True)  # top hidden inside the rim (no z-fight)
    fz = -sz / 2
    # roof rim
    m.box((sx, 0.4, sz), (0, sy - 0.4, 0), "WHITE" if wall != "WHITE" else "STEEL", bevel="M", bottom=True)
    # shop window (left) and door (right) inside one frame
    ww, wh = sx * 0.7, sy * 0.45
    m.box((ww + 0.5, wh + 0.5, 0.45), (0, 0.35, fz - 0.05), "WHITE", bevel="S", bottom=True)
    win_w = ww * 0.62
    m.box((win_w, wh - 0.1, 0.3), (-ww / 2 + win_w / 2 + 0.15, 0.6, fz - 0.15), window,
          glow=None if not window.startswith("GLOW") else window, bevel="S", bottom=True)
    dw = ww - win_w - 0.45
    m.box((dw, wh - 0.1, 0.3), (ww / 2 - dw / 2 - 0.15, 0.6, fz - 0.15), door, bevel="S", bottom=True)
    m.sphere(0.15, (ww / 2 - dw + 0.1, 0.6 + wh * 0.45, fz - 0.33), "GOLD", segs=8, rings=5)
    # awning: striped (2 colors), over the window (Props: y 0.62h, z front - 0.6, 1.2 deep)
    n = 4
    for i in range(n):
        x0 = -sx / 2 + i * sx / n
        color = awning[i % 2]
        m.box((sx / n - 0.04, 0.4, 1.2), (x0 + sx / n / 2, sy * 0.62 - 0.2, fz - 0.6), color, bevel="S",
              rot=None)
    m.cyl(0.3, sx - 0.1, (0, sy * 0.62 - 0.25, fz - 0.95), awning[0], axis="X", bevel="XS", verts=10)
    # sign: text stays on the old sign part (front face at fz - 0.3)
    sign_board(m, (0, sy * 0.82, fz - 0.2), sx * 0.75, sy * 0.25, sign_color, frame=sign_frame,
               frame_w=0.3, depth=0.3, text_plane_z=fz - 0.3, bolts=False)


def tower(m, size, wall, rows, sign=None, sign_color="RED", lit="GLOW_WARM", frame="WHITE"):
    """Props.luau tower(): a building with a 3 x rows grid of lit windows and maybe a sign on top."""
    sx, sy, sz = size
    m.box((sx, sy - 0.2, sz), (0, 0, 0), wall, bevel="L", bottom=True)  # top hidden inside the rim (no z-fight)
    m.box((sx, 0.45, sz), (0, sy - 0.45, 0), frame, bevel="M", bottom=True)
    fz = -sz / 2
    for row in range(rows):
        for col in range(3):
            x = (col - 1) * (sx / 3.2)
            y = 1.2 + row * ((sy - 2.5) / rows)
            m.box((1.75, 1.75, 0.35), (x, y - 0.17, fz - 0.05), frame, bevel="S", bottom=True)
            m.box((1.35, 1.35, 0.3), (x, y + 0.03, fz - 0.12), lit, glow=lit if lit.startswith("GLOW") else None,
                  bevel="XS", bottom=True)
    if sign:
        sign_board(m, (0, sy - 0.9, fz - 0.2), sx * 0.8, 1.4, sign_color, frame="WHITE", frame_w=0.25, depth=0.3,
                   text_plane_z=fz - 0.3, bolts=False)


def plus_sign(m, center, size, bar, color, plane="XY", depth=0.3, bevel=None):
    """A medical cross / plus made of 3 boxes that do NOT overlap (overlapping coplanar boxes z-fight and render
    black spots). plane "XY": on a wall facing -Z/+Z; plane "XZ": lying flat on a top surface."""
    cx, cy, cz = center
    side = (size - bar) / 2
    off = bar / 2 + side / 2
    if plane == "XY":
        m.box((bar, size, depth), (cx, cy, cz), color, bevel=bevel)
        for s_ in (-1, 1):
            m.box((side, bar, depth), (cx + s_ * off, cy, cz), color, bevel=bevel)
    else:
        m.box((bar, depth, size), (cx, cy, cz), color, bevel=bevel)
        for s_ in (-1, 1):
            m.box((side, depth, bar), (cx + s_ * off, cy, cz), color, bevel=bevel)


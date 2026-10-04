"""
decoration.py - fences, lamps, flower boxes, walls, fountains, light strips...
"""

import parts


def workplace_fence(m):
    """Plots.luau:182-187: low white fence, 18 long, 6 posts, 2 rails (one each side of the entrance)."""
    for i in range(6):
        x = -8.5 + i * 3.4
        m.box((0.55, 2.25, 0.55), (x, 0, 0), "WHITE", bevel="S", bottom=True)
        m.sphere(0.34, (x, 2.26, 0), "WHITE", segs=10, rings=6)  # round finial (detail)
    for y in (1.15, 2.0):
        parts.chunky_rail(m, -8.82, 8.82, y, 0, 0.36, "WHITE")


def workplace_lamp_post(m):
    """Plots.luau:189-195: lamp post at the entrance (pole 7 tall, glowing ball d 1.3 at y 7.3).
    The PointLight stays on the old (invisible) ball part."""
    m.cyl(0.6, 0.5, (0, 0, 0), "CHARCOAL", bevel="S", bottom=True, verts=14)
    m.cyl(0.24, 6.3, (0, 0.5, 0), "STEEL", bevel="XS", bottom=True, verts=10)
    m.cyl(0.42, 0.35, (0, 6.55, 0), "STEEL", bevel="XS", bottom=True, verts=12, radius_top=0.55)  # cup
    m.sphere(0.62, (0, 7.3, 0), "GLOW_WARM", glow="GLOW_WARM", segs=12, rings=8)
    m.cyl(0.32, 0.3, (0, 7.62, 0), "STEEL", bevel="XS", bottom=True, verts=10)  # little cap (detail)


def workplace_flower_box(m):
    """Plots.luau:199-203: wooden flower box (5 x 1.2 x 1.6) with three flowers."""
    m.box((5, 1.2, 1.6), (0, 0, 0), "WOOD", bevel="M", bottom=True)
    m.box((5.0, 0.3, 1.6), (0, 0.95, 0), "WOOD_DARK", bevel="S", bottom=True)  # rim
    for x in (-1.5, 0, 1.5):
        parts.bush(m, (x, 1.32, 0), 0.62, "LEAF")
    for x, petal in ((-1.5, "PINK"), (0, "RED"), (1.5, "GOLD_LIGHT")):
        parts.flower(m, (x + 0.15, 1.72, -0.15), 0.42, petal=petal, heart="WHITE" if petal == "GOLD_LIGHT" else "GOLD_LIGHT")


MODELS = {
    "Workplace_Fence": {"build": workplace_fence},
    "Workplace_LampPost": {"build": workplace_lamp_post},
    "Workplace_FlowerBox": {"build": workplace_flower_box},
}


def plaza_fountain(m):
    """Plaza.luau:69-72: fountain in the middle of the plaza (22 wide, 9 tall).
    A round stone basin with a fat rim, see-through water, a column with a bowl and a glowing water ball.
    Detail: gold coins on the bottom of the water (a wishing fountain - it is a money game)."""
    m.cyl(11.0, 1.25, (0, 0, 0), "STONE", bevel="M", bottom=True, verts=36)
    m.torus(10.1, 0.85, (0, 1.2, 0), "STONE", axis="Y", segs=36, ring_segs=8)
    m.cyl(9.4, 0.45, (0, 1.25, 0), "WATER", glass=True, bevel="XS", bottom=True, verts=32)
    for i, (r, a) in enumerate(((4.5, 20), (6.2, 95), (7.6, 160), (5.4, 230), (7.0, 300), (3.6, 330))):
        import math
        x, z = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        m.cyl(0.42, 0.3, (x, 1.22, z), "GOLD", bevel="XS", bottom=True, verts=12)
    m.cyl(1.25, 0.7, (0, 1.25, 0), "STONE_DARK", bevel="S", bottom=True, verts=16)
    m.cyl(0.85, 4.0, (0, 1.9, 0), "STONE", bevel="S", bottom=True, verts=16, radius_top=0.7)
    m.cyl(2.2, 0.9, (0, 5.0, 0), "STONE", bevel="M", bottom=True, verts=24, radius_top=3.0)
    m.cyl(2.5, 0.3, (0, 5.62, 0), "WATER", glass=True, bevel="XS", bottom=True, verts=24)
    m.sphere(1.5, (0, 7.5, 0), "GLOW_COOL", glow="GLOW_COOL", segs=16, rings=10)


def city_wall(m):
    """Plaza.luau:41-46: the low stone wall around a city (4 sides, 368 long, 6 tall + cap).
    The invisible tall barrier part inside it stays as it is. Chunky stone wall, lighter rounded cap,
    pillars at the corners and in the middle of each side with gold ball finials (detail)."""
    half = 183.0
    for (x, z, sx, sz) in ((0, half, 368, 2), (0, -half, 368, 2), (half, 0, 2, 368), (-half, 0, 2, 368)):
        m.box((sx, 6, sz), (x, 0, z), "STONE_DARK", bevel="L", bottom=True)
        m.box((sx + 0.6 if sx > 2 else 2.6, 0.8, sz + 0.6 if sz > 2 else 2.6), (x, 6.0, z), "STONE", bevel="M",
              bottom=True)
    spots = [(sx * half, sz * half) for sx in (-1, 1) for sz in (-1, 1)]
    spots += [(0, half), (0, -half), (half, 0), (-half, 0)]
    for x, z in spots:
        m.box((2.8, 6.4, 2.8), (x, 0, z), "STONE", bevel="M", bottom=True)
        m.sphere(0.42, (x, 6.38, z), "GOLD", segs=10, rings=6)


MODELS["Plaza_Fountain"] = {"build": plaza_fountain, "budget": 6000}
MODELS["City_Wall"] = {"build": city_wall, "budget": 6000}


# ----------------------------------------------------------------------------
# Wall pieces inside the workplaces (all 0.3 deep against the back wall, front = -Z)
# ----------------------------------------------------------------------------

def school_blackboard(m):
    """Themes.luau:124: green blackboard (20 x 6) with a wood frame, chalk tray and a chalk sum (detail)."""
    m.box((20, 6, 0.3), (0, 0, 0.0), "WOOD", bevel="S", bottom=True)
    m.box((19.0, 5.0, 0.3), (0, 0.5, -0.05), "GREEN_DARK", bevel="XS", bottom=True)
    m.box((18, 0.3, 0.45), (0, 0.35, -0.2), "WOOD", bevel="XS", bottom=True)
    # 1 + 1 = 2 in chalk. The board faces -Z, so the viewer's right is -X: the sum runs towards -X and the "2"
    # glyph is drawn mirrored in X.
    for x0 in (6.0, -0.6):
        m.box((0.3, 1.8, 0.3), (x0, 2.6, -0.2), "WHITE", bevel=None, bottom=True)
    parts.plus_sign(m, (3.6, 3.5, -0.2), 1.3, 0.3, "WHITE", plane="XY")
    for y in (3.15, 3.65):
        m.box((1.3, 0.3, 0.3), (-3.2, y, -0.2), "WHITE", bevel=None, bottom=True)
    two = [(5.4, 4.4), (6.7, 4.4), (6.7, 4.1), (5.85, 3.1), (6.7, 3.1), (6.7, 2.6), (5.4, 2.6), (5.4, 2.95),
           (6.2, 4.05), (5.4, 4.05)]
    m.prism([(-x, y) for x, y in two], 0.3, (0, 0, -0.2), "WHITE", plane="XY", bevel=None)


def clinic_wall_screen(m):
    """Themes.luau:111-112: heart monitor on the wall (8 x 5) with a heartbeat line (detail)."""
    m.box((8, 5, 0.3), (0, 0, 0.0), "CHARCOAL", bevel="M", bottom=True)
    m.box((6, 3, 0.3), (0, 1.0, -0.08), "GREEN", glow="GREEN", bevel="XS", bottom=True)
    pts = [(-2.6, 2.5), (-1.0, 2.5), (-0.6, 3.4), (-0.1, 1.6), (0.4, 2.9), (0.7, 2.5), (2.6, 2.5)]
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):  # alternate depth: no coplanar overlaps
        z = -0.2 - 0.02 * (i % 2)
        m.bar((-x0, y0, z), (-x1, y1, z), 0.3, "WHITE", round_bar=False, bevel=None)


def hospital_wall_cross(m):
    """Themes.luau:94-95: the red cross on the hospital's back wall (icon hospital cross)."""
    arm, half = 2.5, 0.75
    cross = [(-half, arm), (half, arm), (half, half), (arm, half), (arm, -half), (half, -half), (half, -arm),
             (-half, -arm), (-half, -half), (-arm, -half), (-arm, half), (-half, half)]
    m.prism([(x, y + 2.5) for x, y in cross], 0.3, (0, 0, 0), "RED", plane="XY", bevel="S")


def office_screen(m):
    """Themes.luau:162-163: presentation screen (14 x 7) showing a growing bar chart (icon chart, detail)."""
    m.box((14, 7, 0.3), (0, 0, 0.05), "BLUE", bevel="M", bottom=True)
    m.box((10, 4, 0.3), (0, 1.0, -0.05), "GLOW_COOL", glow="GLOW_COOL", bevel="XS", bottom=True)
    # the chart grows to the viewer's right (= -X on a wall that faces -Z)
    for i, (h, c) in enumerate(((1.2, "GREEN"), (2.0, "GOLD"), (2.9, "GREEN"))):
        m.box((1.4, h, 0.3), (3 - i * 2.6, 1.4, -0.2), c, bevel="XS", bottom=True)
    m.bar((4.0, 2.2, -0.3), (-3.8, 4.6, -0.3), 0.3, "RED", round_bar=False, bevel=None)


def garage_tool_board(m):
    """Themes.luau:178: tool board on the garage wall (10 x 6) with a wrench, hammer and screwdriver (detail)."""
    m.box((10, 6, 0.3), (0, 0, 0.0), "ORANGE", bevel="M", bottom=True)
    m.box((9, 5, 0.3), (0, 0.5, -0.05), "TAN", bevel="XS", bottom=True)
    # wrench (icon wrench)
    m.bar((-3.6, 1.6, -0.22), (-1.8, 4.4, -0.22), 0.4, "STEEL", round_bar=False, bevel="XS")
    m.torus(0.45, 0.17, (-1.65, 4.65, -0.25), "STEEL", axis="Z", segs=10, ring_segs=6)
    # hammer
    m.box((0.35, 3.0, 0.3), (0.6, 1.2, -0.22), "WOOD", bevel="XS", bottom=True)
    m.box((1.6, 0.7, 0.4), (0.6, 4.1, -0.25), "CHARCOAL", bevel="XS", bottom=True)
    # screwdriver
    m.box((0.5, 1.2, 0.4), (3.0, 3.3, -0.25), "RED", bevel="XS", bottom=True)
    m.box((0.3, 1.8, 0.3), (3.0, 1.5, -0.22), "STEEL", bevel=None, bottom=True)


# Wall boards were 0.2-0.4 thick: with the 0.3 minimum part thickness their details may stand up to 0.3 studs
# further out from the wall (DECISIONS.md #13). Nobody walks through a wall board, so gameplay is unchanged.
WALL_TOLERANCE = 0.3
MODELS["School_Blackboard"] = {"build": school_blackboard, "tolerance": WALL_TOLERANCE}
MODELS["Clinic_WallScreen"] = {"build": clinic_wall_screen, "tolerance": WALL_TOLERANCE}
MODELS["Hospital_WallCross"] = {"build": hospital_wall_cross}
MODELS["Office_Screen"] = {"build": office_screen, "tolerance": WALL_TOLERANCE}
MODELS["Garage_ToolBoard"] = {"build": garage_tool_board, "tolerance": WALL_TOLERANCE}


def lobby_pillar(m):
    """Lobby.luau:358-365: marble pillar (26 tall) with a gold cap and a lamp on the hall side (+X)."""
    m.box((3.6, 1.0, 3.6), (-0.3, 0, 0), "GOLD", bevel="M", bottom=True)
    m.cyl(1.45, 23.5, (-0.3, 1.0, 0), "CREAM", bevel="M", bottom=True, verts=18)
    m.box((4.0, 1.0, 4.0), (-0.3, 24.5, 0), "GOLD", bevel="M", bottom=True)
    m.box((3.4, 0.5, 3.4), (-0.3, 25.5, 0), "CREAM", bevel="S", bottom=True)
    # wall lamp: a gold arm and cup with a glowing bulb (detail)
    m.box((0.6, 0.4, 0.4), (1.1, 10.55, 0), "GOLD", bevel="XS", bottom=True)
    m.cyl(0.45, 0.4, (1.6, 10.55, 0), "GOLD", bevel="XS", bottom=True, verts=10, radius_top=0.55)
    m.sphere(0.7, (1.6, 11.5, 0), "GLOW_WARM", glow="GLOW_WARM", segs=12, rings=8)


def fast_track_gate(m):
    """Plots.luau:214-216: the golden FREE! gate (Fast Track only). The text stays on the old sign part."""
    for x in (-7, 7):
        m.box((2.0, 0.8, 2.0), (x, 0, 0), "CREAM", bevel="M", bottom=True)
        m.box((1.5, 11.2, 1.5), (x, 0.8, 0), "GOLD", bevel="M", bottom=True)
        m.prism(star_points_dec(0.55, 0.25, cx=x, cy=7.0), 0.3, (0, 0, -0.85), "GOLD_LIGHT", plane="XY", bevel=None)
    parts.sign_board(m, (0, 12.5, 0), 15.0, 2.6, "GOLD", frame="CREAM", frame_w=0.2, depth=0.6, text_plane_z=-0.5,
                     bolts=True)


def star_points_dec(outer, inner, n=5, cx=0.0, cy=0.0):
    import math
    return [(cx + math.sin(2 * math.pi * k / (2 * n)) * (outer if k % 2 == 0 else inner),
             cy + math.cos(2 * math.pi * k / (2 * n)) * (outer if k % 2 == 0 else inner)) for k in range(2 * n)]


def lux_chandelier(m):
    """Themes.luau:214-219: a glowing chandelier on a gold rod (the PointLight stays on the old ball)."""
    import math
    m.cyl(0.42, 0.3, (0, 3.3, 0), "GOLD", bevel="XS", bottom=True, verts=10)
    m.cyl(0.15, 1.8, (0, 1.6, 0), "GOLD", bevel=None, bottom=True, verts=6)
    m.sphere(0.72, (0, 1.1, 0), "GLOW_WARM", glow="GLOW_WARM", segs=12, rings=8)
    m.torus(0.92, 0.15, (0, 0.9, 0), "GOLD", axis="Y", segs=16, ring_segs=6)
    for k in range(6):
        a = 2 * math.pi * k / 6
        m.sphere(0.18, (0.92 * math.cos(a), 1.12, 0.92 * math.sin(a)), "GLOW_WARM", glow="GLOW_WARM", segs=6, rings=4)


def auction_room_lamp(m):
    """AuctionRoom.luau:53: a ceiling lamp panel (6 x 0.5 x 6)."""
    m.box((6, 0.3, 6), (0, 0.2, 0), "CHARCOAL", bevel="S", bottom=True)
    m.box((5.0, 0.3, 5.0), (0, 0.0, 0), "GLOW_WARM", glow="GLOW_WARM", bevel="XS", bottom=True)


def podium_light_strip(m):
    """PodiumRoom.luau:69: a glowing vertical light strip on the backdrop (0.8 x 30)."""
    m.box((0.8, 30, 0.3), (0, 0, 0.15), "CHARCOAL", bevel="XS", bottom=True)
    m.box((0.5, 29.4, 0.3), (0, 0.3, -0.12), "GOLD", glow="GOLD@0.55", bevel="XS", bottom=True)


MODELS["Lobby_Pillar"] = {"build": lobby_pillar}
MODELS["FastTrack_Gate"] = {"build": fast_track_gate}
MODELS["Lux_Chandelier"] = {"build": lux_chandelier}
MODELS["AuctionRoom_Lamp"] = {"build": auction_room_lamp}
MODELS["PodiumRoom_LightStrip"] = {"build": podium_light_strip}

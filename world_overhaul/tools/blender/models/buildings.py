"""
buildings.py - buildings category. Coordinates = Roblox local of each template (see tools/blueprint.py).
"""

import parts
from parts import THEMES

# Per-theme extras: sign board (white text must stay readable), sign frame, awning stripes, roof detail
SIGN = {
    "PIZZERIA": ("GREEN_DARK", "WHITE", ("GREEN", "WHITE"), "chimney"),
    "BUSDEPOT": ("BLUE", "GOLD", ("GOLD", "WHITE"), "vent"),
    "HOSPITAL": ("RED", "WHITE", ("RED", "WHITE"), "helipad"),
    "CLINIC": ("TEAL", "WHITE", ("WHITE", "TEAL"), "vent"),
    "SCHOOL": ("GREEN_DARK", "WHITE", ("GREEN_DARK", "WHITE"), "bell"),
    "POLICE": ("BLUE", "WHITE", ("BLUE", "WHITE"), "siren"),
    "OFFICE": ("BLUE", "WHITE", ("BLUE", "WHITE"), "vent"),
    "GARAGE": ("CHARCOAL", "GOLD", ("CHARCOAL", "GOLD_LIGHT"), "vent"),
    "FASTTRACK": ("NAVY", "GOLD", ("GOLD", "CREAM"), "star"),
}


def workplace_building(m, theme_name):
    """Plots.buildWorkplace (Plots.luau:130-169): the job building at the back of the plot.
    Open front, walls on 3 sides, corner pillars, roof over the back half, striped awning, big sign."""
    th = THEMES[theme_name]
    board, frame, awning, roof_detail = SIGN[theme_name]
    wall, accent, floor, trim = th["wall"], th["accent"], th["floor"], th["trim"]

    # floor slab (y -1..0, z 6..24)
    m.box((48, 1, 18), (0, -0.5, 15), floor, bevel="S")
    # walls: back and both sides (1 stud thick, 14 tall), front beam over the opening
    m.box((47, 14, 1), (0, 0, 23.5), wall, bevel="L", bottom=True)
    for x in (-23.5, 23.5):
        m.box((1, 14, 16), (x, 0, 15), wall, bevel="L", bottom=True)
    m.box((46, 2, 1), (0, 12, 6.5), wall, bevel="L", bottom=True)
    # corner pillars with caps and plinths
    for x in (-23.5, 23.5):
        for z in (6.5, 23.5):
            parts.pillar(m, (x, 0, z), 14, 2.0, accent, cap="WHITE" if trim != "GOLD" else "GOLD", cap_w=2.6)
    # a darker plinth band around the outside of the walls (grounds the building)
    m.box((47.0, 1.2, 0.4), (0, 0, 24.15), "STONE_DARK", bevel="S", bottom=True)
    for x in (-24.15, 24.15):
        m.box((0.4, 1.2, 16), (x, 0, 15), "STONE_DARK", bevel="S", bottom=True)
    # roof over the back half (y 14..15, z 13..24) with a fat rounded rim
    m.box((47, 0.95, 11), (0, 14.05, 18.5), wall, bevel="M", bottom=True)
    m.box((48, 0.5, 0.7), (0, 15, 23.65), trim, bevel="S", bottom=True)
    m.box((48, 0.5, 0.7), (0, 15, 13.35), trim, bevel="S", bottom=True)
    for x in (-23.65, 23.65):  # side rims end at the front/back rims (no overlapping faces)
        m.box((0.7, 0.5, 9.6), (x, 15, 18.5), trim, bevel="S", bottom=True)
    # front trim above the beam, left and right of the sign (y 14..14.6)
    for x0, x1 in ((-24, -13.6), (13.6, 24)):  # 14.05..14.5: no face shared with the pillar caps (z-fight)
        m.box((x1 - x0, 0.45, 1.4), ((x0 + x1) / 2, 14.05, 6.5), accent, bevel="S", bottom=True)
    # side windows (Plots.luau:151-156): 5 wide, 4.5 tall, centered y 6.75 at z 11 and 19
    for x, facing in ((-24.0, "-X"), (24.0, "+X")):
        for z in (11, 19):
            parts.window(m, (x, 6.75, z), 4.6, 4.3, facing=facing, frame="WHITE", cross=False)
    # striped awning over the open front (Plots.luau:160-163): y 10..11.6, z 2.5..6
    parts.stripes_awning(m, -24, 24, 8, 11.6, 10.0, 6.0, 2.5, awning)
    # the big sign: text area 26 x 3 at y 15.5; the old sign part's front face is at z 6.2
    parts.sign_board(m, (0, 15.5, 6.5), 26, 3, board, frame=frame, frame_w=0.5, depth=0.6, text_plane_z=6.2)
    # two little lamps on goosenecks above the sign (detail 1)
    for x in (-9, 9):
        m.box((0.3, 0.45, 0.6), (x, 17.4, 6.55), "STEEL", bevel="XS", bottom=True)
        parts.bulb(m, (x, 18.0, 6.2), 0.4)
    # roof detail per job (detail 2)
    if roof_detail == "chimney":  # the pizza oven's chimney, above the oven (Themes.luau:56 at x -14, z 20)
        m.cyl(0.9, 2.6, (-14, 15, 20), "BRICK", bevel="M", bottom=True, verts=14)
        m.cyl(1.15, 0.4, (-14, 17.6, 20), "CHARCOAL", bevel="S", bottom=True, verts=14)
    elif roof_detail == "helipad":
        m.cyl(3.2, 0.3, (12, 15, 18.5), "SLATE", bevel="S", bottom=True, verts=20)
        m.box((0.6, 0.31, 2.6), (11.0, 15.0, 18.5), "WHITE", bevel="XS", bottom=True, min_thick=False)
        m.box((0.6, 0.31, 2.6), (13.0, 15.0, 18.5), "WHITE", bevel="XS", bottom=True, min_thick=False)
        m.box((1.4, 0.31, 0.6), (12, 15.0, 18.5), "WHITE", bevel="XS", bottom=True, min_thick=False)  # H bar
    elif roof_detail == "bell":  # a little school bell tower
        m.box((2.4, 2.2, 2.4), (0, 15, 20), "WHITE", bevel="M", bottom=True)
        m.prism([(-1.7, 0), (1.7, 0), (0, 1.1)], 2.8, (0, 17.2, 20), "RED", bevel="S")
        m.sphere(0.5, (0, 16.2, 18.75), "GOLD", segs=10, rings=6)
    elif roof_detail == "siren":
        m.box((3.0, 0.6, 1.4), (0, 15, 20), "CHARCOAL", bevel="S", bottom=True)
        m.sphere(0.55, (-0.75, 15.8, 20), "RED", scale=(1, 0.8, 1), segs=10, rings=6)
        m.sphere(0.55, (0.75, 15.8, 20), "BLUE", scale=(1, 0.8, 1), segs=10, rings=6)
    elif roof_detail == "star":
        star = [(0.0, 1.0), (0.24, 0.33), (0.95, 0.31), (0.38, -0.12), (0.59, -0.81), (0.0, -0.4),
                (-0.59, -0.81), (-0.38, -0.12), (-0.95, 0.31), (-0.24, 0.33)]
        m.box((1.6, 0.6, 1.6), (0, 15, 20), "GOLD", bevel="S", bottom=True)
        m.prism([(x * 1.4, y * 1.4 + 17.0) for x, y in star], 0.5, (0, 0, 20), "GOLD", bevel="S")
    else:  # an air conditioner box with a round fan
        m.box((3.2, 1.3, 2.4), (14, 15, 19.5), "WHITE", bevel="M", bottom=True)
        m.cyl(0.85, 0.3, (14, 16.3, 19.5), "STEEL", bevel="XS", bottom=True, verts=14)


MODELS = {}
for _theme in THEMES:
    MODELS["Workplace_Building_" + _theme] = {"build": (lambda t: (lambda m: workplace_building(m, t)))(_theme)}


# ----------------------------------------------------------------------------
# Dream: Beach Villa (BeachVillaBuilder.luau, bbox x +-20, y 0..13.2, z -17.418..16)
# ----------------------------------------------------------------------------

def dream_beach_villa(m):
    top = 1.0
    # stone terrace and a front step
    m.box((40, 1, 32), (0, 0, 0), "STONE", bevel="L", bottom=True)
    m.box((8, 0.5, 1.2), (-4, 0, -16.6), "STONE", bevel="S", bottom=True)
    # ground floor: white block, big glass front with dark frames, wooden door, side window
    m.box((22, 6, 11), (-3, top, 8.5), "WHITE", bevel="L", bottom=True)
    m.box((19.4, 5.4, 0.45), (-4.5, top + 0.2, 3.15), "CHARCOAL", bevel="S", bottom=True)
    for i in range(4):
        x = -14 + 2.375 + i * 4.75
        m.box((4.3, 4.8, 0.35), (x, top + 0.5, 2.95), "WINDOW", bevel="S", bottom=True)
    m.box((2.6, 4.4, 0.5), (6.4, top, 2.95), "WOOD", bevel="S", bottom=True)
    m.sphere(0.18, (5.6, top + 2.1, 2.65), "GOLD", segs=8, rings=5)
    parts.window(m, (8.0, top + 3.3, 8.5), 5.6, 2.8, facing="+X", frame="CHARCOAL", sill=False)
    for x in (-14.3, 8.3):
        m.box((0.45, 0.55, 0.4), (x, top + 4.5, 2.8), "GLOW_WARM", glow="GLOW_WARM", bevel="XS")
    # slab between the floors, upper floor pushed forward over the balcony, wood slats, roof
    m.box((25, 0.6, 13), (-3, top + 6, 8.5), "SLATE", bevel="M", bottom=True)
    m.box((20, 5, 10), (2, top + 6.6, 6), "WHITE", bevel="L", bottom=True)
    m.box((18.4, 4.4, 0.45), (2, top + 6.9, 1.15), "CHARCOAL", bevel="S", bottom=True)
    for i in range(3):
        m.box((5.6, 3.8, 0.35), (2 - 6.0 + i * 6.0, top + 7.2, 0.95), "WINDOW", bevel="S", bottom=True)
    for i in range(5):
        m.box((0.4, 5, 0.6), (-8.15, top + 6.6, 2 + i * 2), "WOOD", bevel="XS", bottom=True)
    m.box((22, 0.6, 12), (2, top + 11.6, 6), "SLATE", bevel="M", bottom=True)
    # balcony with a glass railing and a round rail
    m.box((20, 0.4, 4), (2, top + 6.1, 0), "SLATE", bevel="S", bottom=True)
    m.box((19.6, 1.2, 0.3), (2, top + 6.5, -1.9), "WINDOW", glass=True, bevel="XS", bottom=True)
    parts.chunky_rail(m, -7.8, 11.8, top + 7.75, -1.9, 0.32, "STEEL")
    # pool with a stone edge, water and a ladder; a rubber duck floats in it (detail)
    px, pz = -4, -9
    m.box((15.2, 0.4, 7.2), (px, top - 0.15, pz), "WATER", bevel="S", bottom=True)
    for dz in (-4.1, 4.1):
        m.box((16.6, 0.45, 0.8), (px, top, pz + dz), "STONE", bevel="S", bottom=True)
    for dx in (-8.1, 8.1):  # ends butt against the long edge stones
        m.box((0.8, 0.45, 7.4), (px + dx, top, pz), "STONE", bevel="S", bottom=True)
    for x in (-0.5, 0.5):
        m.cyl(0.15, 1.4, (px + 7 + x, top, pz + 3.8), "STEEL", bevel="XS", bottom=True, verts=8)
    m.sphere(0.45, (px - 3, top + 0.55, pz - 1), "GOLD_LIGHT", scale=(1, 0.8, 1.2), segs=10, rings=6)
    m.sphere(0.3, (px - 3, top + 1.0, pz - 1.35), "GOLD_LIGHT", segs=8, rings=6)
    m.box((0.3, 0.3, 0.35), (px - 3, top + 0.95, pz - 1.7), "ORANGE", bevel="XS")
    # two sun loungers and a striped umbrella
    for x in (9, 12.5):
        m.box((1.7, 0.4, 4.2), (x, top, -9), "WOOD", bevel="S", bottom=True)
        m.box((1.5, 0.3, 2.8), (x, top + 0.4, -9.6), "WHITE", bevel="S", bottom=True)
        m.wedge((1.5, 1.1, 1.3), (x, top + 0.35, -7.5), "WHITE", bevel="S", bottom=True)
    m.cyl(0.15, 4.2, (10.75, top, -12), "WHITE", bevel="XS", bottom=True, verts=8)
    m.cyl(2.75, 0.9, (10.75, top + 4.1, -12), "ORANGE", bevel="S", bottom=True, verts=16, radius_top=0.3)
    m.cyl(1.6, 0.42, (10.75, top + 4.42, -12), "WHITE", bevel="XS", bottom=True, verts=16, radius_top=0.95)
    m.sphere(0.28, (10.75, top + 5.05, -12), "WHITE", segs=8, rings=5)
    # palms and potted plants
    parts.palm(m, (-17, top, -13), 10.3, lean=2.0, leaf_length=3.6, leaves=5, segs=5, leaf_steps=5, trunk_verts=8)
    parts.palm(m, (17, top, -3), 9.4, lean=2.0, lean_dir=(-1, 0), leaf_length=3.6, leaves=5, segs=5,
               leaf_steps=5, trunk_verts=8)
    for x, z in ((-15.5, 1.5), (9.5, 1.5), (16, 12)):
        m.cyl(0.65, 1.0, (x, top, z), "TAN", bevel="S", bottom=True, verts=12, radius_top=0.75)
        parts.bush(m, (x, top + 1.7, z), 0.9, "LEAF")


MODELS["Dream_BeachVilla"] = {"build": dream_beach_villa, "export": "BeachVilla", "mesh_name": "BeachVilla"}


from models.props import BUILDING_MAKERS  # noqa: E402

for _t, (_fn, _export) in BUILDING_MAKERS.items():
    MODELS[_t] = {"build": _fn, "export": _export}


# ----------------------------------------------------------------------------
# Lobby hall, auction room, podium room (shells and booths)
# ----------------------------------------------------------------------------

ROOM_COLORS = {"Lobby_RoomBooth": "RED", "Lobby_RoomBooth_v2": "BLUE", "Lobby_RoomBooth_v3": "GREEN",
               "Lobby_RoomBooth_v4": "GOLD"}


def star_points(outer, inner, n=5, cx=0.0, cy=0.0):
    import math
    return [(cx + math.sin(2 * math.pi * k / (2 * n)) * (outer if k % 2 == 0 else inner),
             cy + math.cos(2 * math.pi * k / (2 * n)) * (outer if k % 2 == 0 else inner)) for k in range(2 * n)]


def lobby_room_booth(m, color):
    """Lobby.luau:420-437: one room door. Front = +Z (it faces the spawn). The glowing platform behind the arch
    is the JOIN TRIGGER: the old part stays (invisible) and does the work, this is only its look."""
    m.box((23.5, 0.9, 19.5), (0, 0, -0.98), "CHARCOAL", bevel="M", bottom=True)
    m.box((22, 0.35, 18), (0, 0.75, -0.98), color, glow=color + "@0.45", bevel="S", bottom=True)
    m.box((22, 0.3, 1.2), (0, 0.8, 9.02), "GOLD", bevel="XS", bottom=True)  # gold threshold (detail)
    for x in (-12, 12):
        m.box((3.2, 1, 3.2), (x, 0, 9.02), "GOLD", bevel="M", bottom=True)
        m.cyl(1.2, 13.0, (x, 1.0, 9.02), color, bevel="M", bottom=True, verts=18)
        m.cyl(1.45, 0.5, (x, 13.45, 9.02), "GOLD", bevel="S", bottom=True, verts=18)
    m.box((27, 2.6, 2.6), (0, 14.0, 9.02), color, bevel="L", bottom=True)
    m.box((21.6, 13.0, 0.3), (0, 1.05, 9.02), color, glow=color + "@0.7", bevel="XS", bottom=True)  # portal
    with m.at((0, 0, 0), yaw=180):  # the sign faces +Z: build it turned around
        parts.sign_board(m, (0, 15.3, -10.52), 23.0, 2.0, color, frame="WHITE", frame_w=0.3, depth=0.42,
                         text_plane_z=-10.72, bolts=False)
    m.prism(star_points(1.0, 0.45, cy=17.8), 0.6, (0, 0, 9.02), "GOLD", plane="XY", bevel="XS", glow="GOLD")


def lobby_walls(m):
    """Lobby.luau:343-348: the hall walls (26 tall) with gold trim; inside: a dark wainscot band and a gold rail."""
    w, d = 148, 100
    # the side walls and their caps end where the front/back ones begin (no overlapping faces at the corners)
    for (x, z, sx, sz) in ((0, -49, w, 2), (0, 49, w, 2), (-73, 0, 2, d - 4), (73, 0, 2, d - 4)):
        m.box((sx, 26, sz), (x, 0, z), "NAVY", bevel="L", bottom=True)
        m.box((sx + 0.8 if sx > 2 else 2.8, 1, sz + 0.8 if sx > 2 else sz - 0.8), (x, 26, z), "GOLD", bevel="M",
              bottom=True)
    # inside faces: wainscot (INK) and a gold chair rail at hand height (detail)
    for (x, z, sx, sz) in ((0, -47.85, 143.6, 0.3), (0, 47.85, 143.6, 0.3), (-71.85, 0, 0.3, 95.4),
                           (71.85, 0, 0.3, 95.4)):
        m.box((sx, 6.0, sz), (x, 1.0, z), "INK", bevel="XS", bottom=True)
        m.box((sx + (0.2 if sx > 1 else 0.15), 0.4, sz - 0.2 if sz > 1 else 0.45), (x, 7.0, z), "GOLD",
              bevel="XS", bottom=True)


def lobby_window(m):
    """Lobby.luau:368: a big window in the side wall (0.6 x 10 x 14). Inside of the hall = +X here."""
    m.box((0.4, 10, 14), (-0.1, 0, 0), "WHITE", bevel="S", bottom=True)
    m.box((0.3, 9.0, 13.0), (0.25, 0.5, 0), "SKY", glass=True, bevel="XS", bottom=True)
    m.box((0.3, 8.9, 0.4), (0.3, 0.55, 0), "WHITE", bevel=None, bottom=True)
    for s_ in (-1, 1):  # the cross bar in two halves, so the bars do not overlap
        m.box((0.3, 0.4, 6.25), (0.3, 4.8, s_ * 3.325), "WHITE", bevel=None, bottom=True)


def auction_room_shell(m):
    """AuctionRoom.luau:44-49: the closed auction room: wood floor, dark red walls, ceiling."""
    m.box((64, 0.4, 50), (0, -1.0, 0), "WOOD_DARK", bevel="S", bottom=True)
    for i in range(24):  # floor planks
        z = -24.0 + i * 2.06 + 1.0
        m.box((63.4, 0.6, 1.9), (0, -0.6, z), "WOOD", bevel="XS", bottom=True)
    for (x, z, sx, sz) in ((0, -25, 64, 1), (0, 25, 64, 1), (-32, 0, 1, 50), (32, 0, 1, 50)):
        m.box((sx, 24, sz), (x, 0, z), "BRICK", bevel="M", bottom=True)
    for (x, z, sx, sz) in ((0, -24.35, 62.6, 0.3), (0, 24.35, 62.6, 0.3), (-31.35, 0, 0.3, 48.4),
                           (31.35, 0, 0.3, 48.4)):
        m.box((sx, 5.0, sz), (x, 0, z), "WOOD_DARK", bevel="XS", bottom=True)
        m.box((sx + (0.1 if sx > 1 else 0.1), 0.4, sz + (0.1 if sz > 1 else 0.1)), (x, 5.0, z), "GOLD", bevel="XS",
              bottom=True)
        m.box((sx, 0.6, sz), (x, 23.0, z), "GOLD", bevel="XS", bottom=True)
    m.box((65, 1, 51), (0, 24, 0), "CHARCOAL", bevel="M", bottom=True)


def podium_room_shell(m):
    """PodiumRoom.luau:66-67: floor (80 x 64) and the dark backdrop (80 x 34) with gold stars (detail)."""
    m.box((80, 1, 64), (0, -1, 5), "NAVY", bevel="M", bottom=True)
    m.cyl(18, 0.3, (0, -0.28, -4), "PURPLE", bevel="S", bottom=True, verts=40)  # a purple circle around the podium
    m.box((79.6, 34, 1), (0, -1, -20), "INK", bevel="M", bottom=True)
    for x, y, r in ((-34, 27, 1.0), (-22, 30, 0.7), (-8, 31, 0.8), (8, 30.5, 0.9), (21, 29, 0.7), (35, 27, 1.0),
                    (-28, 14, 0.6), (28, 15, 0.6)):
        m.prism(star_points(r, r * 0.45, cx=x, cy=y), 0.3, (0, 0, -19.45), "GOLD", plane="XY", bevel=None)


MODELS["Lobby_Walls"] = {"build": lobby_walls}
MODELS["Lobby_Window"] = {"build": lobby_window}
MODELS["AuctionRoom_Shell"] = {"build": auction_room_shell}
MODELS["PodiumRoom_Shell"] = {"build": podium_room_shell}
for _t, _c in ROOM_COLORS.items():
    MODELS[_t] = {"build": (lambda c: (lambda m: lobby_room_booth(m, c)))(_c)}

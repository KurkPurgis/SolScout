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
    m.box((47, 1, 11), (0, 14, 18.5), wall, bevel="M", bottom=True)
    m.box((48, 0.5, 0.7), (0, 15, 23.65), trim, bevel="S", bottom=True)
    m.box((48, 0.5, 0.7), (0, 15, 13.35), trim, bevel="S", bottom=True)
    for x in (-23.65, 23.65):
        m.box((0.7, 0.5, 11), (x, 15, 18.5), trim, bevel="S", bottom=True)
    # front trim above the beam, left and right of the sign (y 14..14.6)
    for x0, x1 in ((-24, -13.6), (13.6, 24)):
        m.box((x1 - x0, 0.6, 1.4), ((x0 + x1) / 2, 14, 6.5), accent, bevel="S", bottom=True)
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
        m.box((2.0, 0.31, 0.6), (12, 15.0, 18.5), "WHITE", bevel="XS", bottom=True, min_thick=False)
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

"""
props.py - small things: sandbox, kids, debts, Money Makers, investments, furniture...
"""

import parts


def workplace_sandbox(m):
    """Plots.luau:207-209: sandbox 12 x 10 with a wooden edge (0.6 tall). Kids stand in it at y 0."""
    m.box((12, 0.35, 10), (0, -0.1, 0), "SAND", bevel="S", bottom=True)
    for z in (-5.0, 5.0):
        m.box((12.6, 0.6, 0.45), (0, 0, z), "WOOD", bevel="M", bottom=True)
    for x in (-6.0, 6.0):
        m.box((0.45, 0.6, 9.55), (x, 0, 0), "WOOD", bevel="M", bottom=True)
    # a red bucket and a little sandcastle in the corners (detail)
    m.cyl(0.36, 0.55, (4.6, 0.2, 3.6), "RED", bevel="XS", bottom=True, verts=12, radius_top=0.45)
    m.box((1.6, 0.35, 1.0), (-4.0, 0.2, -3.3), "SAND", bevel="S", bottom=True)
    for x in (-4.65, -3.35):
        m.cyl(0.3, 0.5, (x, 0.2, -3.3), "SAND", bevel="XS", bottom=True, verts=10)
    m.box((0.3, 0.3, 0.3), (-4.0, 0.45, -3.3), "RED", bevel="XS", bottom=True)  # a tiny flag


MODELS = {
    "Workplace_Sandbox": {"build": workplace_sandbox},
}


import json as _json
import math
import os as _os

from kit import rb_angles

_TEMPLATES = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "data",
                                           "templates.json")))


# ----------------------------------------------------------------------------
# Money Makers (Props.luau makerBuilders) - builder-local coords, front = -Z, base on the lot top
# ----------------------------------------------------------------------------

def lemonade_stand(m):
    # counter booth (5 x 3 x 2.5) with a white top
    m.box((5, 2.7, 2.5), (0, 0, 0), "GOLD_LIGHT", bevel="M", bottom=True)
    m.box((5.2, 0.35, 2.7), (0, 2.65, 0), "WHITE", bevel="S", bottom=True)
    # sign board: "LEMONADE" text stays on the old sign (front face at z -1.45)
    parts.sign_board(m, (0, 1.6, -1.35), 4.3, 1.0, "GOLD", frame="WHITE", frame_w=0.25, depth=0.3,
                     text_plane_z=-1.45, bolts=False)
    # striped umbrella on a pole behind the counter
    m.cyl(0.17, 3.0, (0, 2.9, 1), "WHITE", bevel="XS", bottom=True, verts=8)
    for i in range(8):
        a0 = 2 * math.pi * i / 8
        color = "GOLD_LIGHT" if i % 2 == 0 else "WHITE"
        pts = [(0, 0), (3.0 * math.cos(a0), 3.0 * math.sin(a0)), (3.0 * math.cos(a0 + math.pi / 4),
                                                                   3.0 * math.sin(a0 + math.pi / 4))]
        m.prism([(x, z + 1) for x, z in pts], 0.32, (0, 5.75, 0), color, plane="XZ", bevel="XS")
    m.cyl(1.2, 0.45, (0, 5.85, 1), "GOLD_LIGHT", bevel="S", bottom=True, verts=12, radius_top=0.2)
    # a big lemon and a pitcher of lemonade with two glasses (detail)
    m.sphere(0.5, (1.2, 3.5, 0), "GOLD_LIGHT", scale=(1.25, 1, 1), segs=12, rings=8)
    m.cyl(0.42, 0.9, (-1.3, 3.0, -0.2), "GOLD_LIGHT", bevel="XS", bottom=True, verts=12, radius_top=0.36)
    m.torus(0.25, 0.08 + 0.07, (-1.75, 3.45, -0.2), "WHITE", axis="Z", segs=10, ring_segs=6)
    for x in (-0.35, 0.15):
        m.cyl(0.18, 0.4, (x, 3.0, -0.6), "WINDOW", bevel="XS", bottom=True, verts=10)


def vending_machine(m):
    m.box((3.5, 5.7, 2.5), (0, 0, 0), "RED", bevel="M", bottom=True)
    m.box((2.6, 3.7, 0.3), (-0.3, 1.9, -1.2), "WHITE", bevel="S", bottom=True)
    m.box((2.3, 3.4, 0.3), (-0.3, 2.05, -1.25), "GLOW_COOL", glow="GLOW_COOL", bevel="XS", bottom=True)
    for row in range(3):  # snacks on the lit shelves
        for col in range(3):
            c = ("GOLD", "GREEN", "PINK")[(row + col) % 3]
            m.box((0.5, 0.6, 0.3), (-1.0 + col * 0.7, 2.4 + row * 1.0, -1.38), c, bevel="XS", bottom=True)
    # coin slot and buttons on the right (detail), dispenser at the bottom
    m.box((0.6, 1.6, 0.3), (1.35, 2.6, -1.22), "CHARCOAL", bevel="XS", bottom=True)
    m.cyl(0.18, 0.3, (1.35, 3.8, -1.32), "GOLD", axis="Z", bevel="XS", verts=10)
    for y in (2.9, 3.3):
        m.cyl(0.15, 0.3, (1.35, y, -1.33), "GREEN", axis="Z", bevel="XS", verts=8)
    m.box((2.2, 0.6, 0.35), (-0.3, 0.7, -1.25), "CHARCOAL", bevel="XS", bottom=True)
    m.box((3.6, 0.5, 2.6), (0, 5.5, 0), "WHITE", bevel="S", bottom=True)


def apartment(m):
    parts.tower(m, (8, 8, 7), "TAN", 2, lit="GLOW_WARM")
    # a stone plinth around the bottom (detail; stays inside the original box)
    m.box((8.1, 0.7, 7.1), (0, 0, 0), "STONE_DARK", bevel="S", bottom=True)


def car_wash(m):
    blue = "BLUE"
    for x in (-4, 4):
        m.box((1, 6, 7), (x, 0, 0), blue, bevel="M", bottom=True)
    m.box((9, 1, 7), (0, 6, 0), blue, bevel="M", bottom=True)
    parts.sign_board(m, (0, 6.5, -3.6), 7, 0.5, "SKY", frame="WHITE", frame_w=0.2, depth=0.3, text_plane_z=-3.7,
                     bolts=False)
    m.box((7, 0.3, 7), (0, 0, 0), "WATER", glass=True, bevel="S", bottom=True)
    # two big spinning brushes (detail) and soap bubbles
    for x in (-2.7, 2.7):
        m.cyl(0.18, 5.6, (x, 0.2, 0.5), "STEEL", bevel="XS", bottom=True, verts=8)
        m.cyl(0.95, 4.2, (x, 0.9, 0.5), "PINK" if x < 0 else "GOLD_LIGHT", bevel="M", bottom=True, verts=14)
    for x, y, z, r in ((-0.6, 0.6, -1.5, 0.5), (0.5, 0.45, -0.6, 0.35), (1.4, 0.55, -2.4, 0.45),
                       (-1.2, 0.4, 1.8, 0.4)):
        m.sphere(r, (x, y, z), "WHITE", segs=10, rings=6)


def food_truck(m):
    """Props.luau foodTruck(): the 8 x 4 x 4.4 orange truck on 4 wheels with a glowing serving hatch and a sign.
    Here the front end is a lower cab with a windshield; a taco on the counter (detail)."""
    orange = "ORANGE"
    m.box((5.9, 4.0, 4.4), (-1.05, 0.9, 0), orange, bevel="L", bottom=True)  # box body (x -4 .. 1.9)
    m.box((2.2, 2.7, 4.2), (2.9, 0.9, 0), orange, bevel="L", bottom=True)  # cab (x 1.8 .. 4)
    m.box((0.3, 1.1, 3.6), (3.9, 2.3, 0), "WINDOW", bevel="XS", bottom=True)  # windshield (proud of the cab face)
    for z in (-2.05, 2.05):
        m.box((1.2, 0.9, 0.3), (2.9, 2.45, z), "WINDOW", bevel="XS", bottom=True)
        m.box((5.6, 0.4, 0.3), (-1.05, 1.35, z * 2.1 / 2.05), "WHITE", bevel="XS", bottom=True)  # side stripe
    for z in (-1.5, 1.5):
        m.cyl(0.28, 0.3, (3.95, 1.55, z), "GLOW_WARM", axis="X", glow="GLOW_WARM", bevel=None, verts=10)
    # serving hatch: dark frame, warm light, counter
    m.box((4.2, 1.7, 0.3), (-1, 2.3, -2.2), "CHARCOAL", bevel="XS", bottom=True)
    m.box((3.8, 1.3, 0.3), (-1, 2.5, -2.25), "GLOW_WARM", glow="GLOW_WARM", bevel="XS", bottom=True)
    m.box((4.4, 0.3, 0.5), (-1, 2.15, -2.38), "WHITE", bevel="S", bottom=True)
    # a taco on the counter: shell + lettuce (detail)
    m.cyl(0.42, 0.7, (-0.2, 2.87, -2.2), "GOLD_LIGHT", axis="X", bevel="XS", verts=12)
    m.box((0.5, 0.3, 0.6), (-0.2, 3.15, -2.2), "GREEN", bevel="XS")
    # the sign above the hatch (its text stays on the old part)
    parts.sign_board(m, (-1, 4.4, -2.3), 4, 0.8, "RED", frame="WHITE", frame_w=0.2, depth=0.3, text_plane_z=-2.4,
                     bolts=False)
    for x in (-2.6, 2.6):
        for z in (-2.2, 2.2):
            parts.wheel(m, (x, 0.9, z), 0.9, 0.6, axis="Z", cap="GOLD")


def toy_shop(m):
    parts.shop(m, (8, 7, 7), "PINK", "PURPLE", "GOLD_LIGHT", awning=("PINK", "WHITE"))
    # two big toy blocks by the door (detail)
    m.box((0.9, 0.9, 0.9), (3.4, 0, -4.2), "BLUE", bevel="S", bottom=True)
    m.box((0.75, 0.75, 0.75), (3.4, 0.9, -4.2), "GOLD", bevel="S", bottom=True, rot=rb_angles(0, math.radians(20), 0))


def mini_golf(m):
    m.box((8.6, 0.3, 6.6), (0, 0, 0), "GREEN", bevel="S", bottom=True)  # inside the wooden rails
    for z in (-3.3, 3.3):
        m.box((9, 0.45, 0.4), (0, 0, z), "WOOD", bevel="S", bottom=True)
    for x in (-4.3, 4.3):
        m.box((0.4, 0.45, 6.2), (x, 0, 0), "WOOD", bevel="S", bottom=True)
    m.cyl(0.5, 0.3, (2.5, 0.05, 1.5), "CHARCOAL", bevel="XS", bottom=True, verts=12)
    m.cyl(0.15, 4.0, (2.5, 0.3, 1.5), "WHITE", bevel="XS", bottom=True, verts=8)
    m.prism([(2.6, 3.2), (4.0, 3.7), (2.6, 4.2)], 0.3, (0, 0, 1.5), "RED", plane="XY", bevel="XS")
    # a little windmill as the obstacle (detail)
    m.box((2, 1.5, 2), (-2, 0.3, -1), "GOLD_LIGHT", bevel="M", bottom=True)
    m.cyl(1.25, 0.6, (-2, 1.8, -1), "RED", bevel="S", bottom=True, verts=12, radius_top=0.3)
    for a in (45, 135):
        m.box((2.0, 0.3, 0.3), (-2, 1.4, -2.15), "WHITE", bevel="XS", rot=rb_angles(0, 0, math.radians(a)))
    m.sphere(0.3, (-3.5, 0.6, 2), "WHITE", segs=10, rings=6)


def house_to_rent(m):
    m.box((8, 5, 7), (0, 0, 0), "SKY", bevel="L", bottom=True)
    roof = [(-4.2, 0), (4.2, 0), (0, 3.0)]
    m.prism([(x, y + 5) for x, y in roof], 7.4, (0, 0, 0), "RED", plane="XY", bevel="M")
    m.box((0.9, 2.0, 0.9), (2.4, 5.6, 1.2), "BRICK", bevel="S", bottom=True)  # chimney with a cap (detail)
    m.box((1.2, 0.35, 1.2), (2.4, 7.55, 1.2), "CHARCOAL", bevel="XS", bottom=True)
    # door and windows sunk a little into the wall so they stay inside the original box (roof eave z -3.7)
    parts.door(m, (0, 0, -3.4), 1.5, 2.8, color="WOOD", mat=False)
    for x in (-2.5, 2.5):
        parts.window(m, (x, 2.7, -3.35), 1.4, 1.2, frame="WHITE", pane="GLOW_WARM", sill=False, depth=0.4)


def coffee_shop(m):
    parts.shop(m, (8, 6, 7), "WOOD", "WOOD_DARK", "GLOW_WARM", awning=("CREAM", "WOOD_DARK"))
    # a coffee cup on a little table by the door (detail)
    m.cyl(0.15, 1.0, (3.3, 0, -4.2), "CHARCOAL", bevel="XS", bottom=True, verts=8)
    m.cyl(0.55, 0.3, (3.3, 1.0, -4.2), "WHITE", bevel="XS", bottom=True, verts=12)
    m.cyl(0.25, 0.4, (3.3, 1.3, -4.2), "WHITE", bevel="XS", bottom=True, verts=10)


def bowling_alley(m):
    parts.shop(m, (10, 6, 7.5), "NAVY", "PINK", "GLOW_COOL", awning=("PINK", "WHITE"))
    # a giant bowling ball and pin on the roof (detail)
    m.sphere(1.0, (3.5, 7.0, 0), "CHARCOAL", segs=14, rings=10)
    for dx, dy in ((-0.25, 0.3), (0.25, 0.3), (0, 0.6)):
        m.sphere(0.15, (3.5 + dx, 7.0 + dy, -0.9), "INK", segs=6, rings=4)
    m.capsule(0.42, 2.0, (1.6, 7.0, 0.2), "WHITE", segs=12)
    m.box((0.86, 0.3, 0.3), (1.6, 7.25, -0.18), "RED", bevel="XS")


def hotel(m):
    parts.tower(m, (8, 16, 7), "CREAM", 5, sign="HOTEL", sign_color="RED", lit="GLOW_WARM", frame="GOLD")
    # entrance canopy (detail)
    m.box((3.4, 0.35, 0.6), (0, 2.2, -3.55), "RED", bevel="S", bottom=True)


def game_studio(m):
    parts.shop(m, (9, 7, 7), "PURPLE", "NAVY", "GLOW_COOL", awning=("PURPLE", "WHITE"))
    # a giant game controller in front of the glowing shop window (detail)
    cx, cy, cz = -1.3, 2.2, -3.95
    m.capsule(0.45, 2.0, (cx, cy, cz), "CHARCOAL", axis="X", segs=12)
    m.box((0.5, 0.3, 0.3), (cx - 0.55, cy, cz - 0.4), "WHITE", bevel="XS")
    m.box((0.3, 0.5, 0.3), (cx - 0.55, cy, cz - 0.4), "WHITE", bevel="XS")
    for dx, c in ((0.4, "RED"), (0.75, "GREEN")):
        m.sphere(0.15, (cx + dx, cy + 0.05, cz - 0.38), c, segs=8, rings=5)


def shopping_mall(m):
    parts.shop(m, (10, 8, 7.5), "WHITE", "BLUE", "WINDOW", awning=("BLUE", "WHITE"), door="WINDOW")
    # three colorful banners on the facade (detail)
    for x, c in ((-4.45, "RED"), (4.45, "GREEN")):
        m.box((0.8, 1.6, 0.3), (x, 5.3, -3.9), c, bevel="XS", bottom=True)


def apartment_building(m):
    parts.tower(m, (9, 12, 7), "BRICK", 4, sign="APARTMENTS", sign_color="NAVY", lit="GLOW_WARM", frame="CREAM")


def pizza_restaurant(m):
    parts.shop(m, (9, 7, 7), "RED", "GREEN_DARK", "GLOW_WARM", awning=("GREEN", "WHITE"))
    # a giant pizza slice on the wall (the icon pizza, detail)
    sx_, sy_ = -3.95, 5.6
    m.prism([(-0.5, 0.5), (0.5, 0.5), (0, -0.85)], 0.3, (sx_, sy_, -3.65), "GOLD", plane="XY", bevel="XS")
    m.cyl(0.16, 1.05, (sx_, sy_ + 0.55, -3.7), "TAN", axis="X", bevel="XS", verts=8)
    for dx, dy in ((-0.2, 0.2), (0.2, 0.15), (0.0, -0.3)):
        m.cyl(0.15, 0.3, (sx_ + dx, sy_ + dy, -3.8), "BRICK", axis="Z", bevel="XS", verts=8)


def theme_park(m):
    m.box((9, 0.3, 7), (0, 0, 0), "GREEN", bevel="S", bottom=True)
    # A-frame legs to the hub
    for x in (-1.8, 1.8):
        for z in (-0.9, 0.9):
            m.stick((x, 0.3, z), (0, 8, z * 0.4), 0.2, "WHITE", verts=8)
    # the wheel: ring, spokes, hub, colorful gondolas (detail)
    m.torus(4.6, 0.32, (0, 8, 0), "PINK", axis="Z", segs=28, ring_segs=6)
    for k in range(6):
        a = 2 * math.pi * k / 6
        m.stick((0, 8, 0), (4.6 * math.cos(a), 8 + 4.6 * math.sin(a), 0), 0.15, "WHITE", verts=6)
    m.cyl(0.75, 1.0, (0, 8, 0), "GOLD", axis="Z", bevel="S", verts=12)
    for k, c in enumerate(("RED", "BLUE", "GOLD", "GREEN", "PURPLE", "ORANGE")):
        a = 2 * math.pi * k / 6 + math.pi / 6
        gx, gy = 4.6 * math.cos(a), 8 + 4.6 * math.sin(a)
        m.box((0.9, 0.8, 0.9), (gx, gy - 0.9, 0), c, bevel="S", bottom=True)


def card_case_color(name):
    rgb_to = {(170, 170, 180): ("STEEL", False), (70, 140, 255): ("BLUE", False), (170, 80, 255): ("PURPLE", True),
              (255, 195, 40): ("GOLD", True)}
    for c in _TEMPLATES[name]["colors"]:
        key = tuple(c[:3])
        if key in rgb_to:
            return rgb_to[key]
    return ("STEEL", False)


def pokeblox_card(m, front, shiny, template):
    """Props.luau pokeBloxCard(): a big card on a stand in a glass case, tilted back 8 degrees.
    The card is the icon card (orange card, picture window with a white ball). The title and the rarity word
    stay on the old sign parts (SurfaceGui text)."""
    case, glow = card_case_color(template)
    m.box((3.6, 0.4, 1.4), (0, 0, 0), "CHARCOAL", bevel="S", bottom=True)
    with m.at((0, 2.6, 0), pitch=-8):
        m.box((2.8, 4.0, 0.3), (0, 0, 0), "GOLD", bevel="S")
        m.box((2.4, 2.0, 0.3), (0, 0.6, -0.1), front, glow=front if front.startswith("GLOW") else None, bevel="XS")
        m.sphere(0.5, (0, 0.6, -0.33), "WHITE", segs=10, rings=6)
        m.box((2.4, 0.7, 0.3), (0, -1.1, -0.06), "WHITE", bevel="XS")  # title plate (text on the old part)
        for z in (-0.3, 0.3):
            m.box((3.2, 4.4, 0.3), (0, 0, z), "WINDOW", glass=True, bevel="XS")
        for s in (-1, 1):
            m.box((0.3, 4.6, 0.75), (s * 1.65, 0, 0), case, glow=case if glow else None, bevel="S")
            m.box((3.5, 0.3, 0.75), (0, s * 2.25, 0), case, glow=case if glow else None, bevel="S")
        m.box((3.4, 0.6, 0.3), (0, -2.75, -0.05), case, bevel="XS")  # rarity plate (word on the old part)


def gold_coin(m):
    m.box((3, 0.4, 1.4), (0, 0, 0), "CHARCOAL", bevel="S", bottom=True)
    # the icon coin: gold rim, deeper orange middle, a raised ring (the $ stays on the old sign part)
    m.cyl(1.9, 0.6, (0, 2.3, 0), "GOLD", axis="Z", bevel="L", verts=28)
    m.cyl(1.4, 0.3, (0, 2.3, -0.2), "ORANGE", axis="Z", bevel="XS", verts=24)
    m.torus(1.45, 0.1 + 0.05, (0, 2.3, -0.3), "GOLD", axis="Z", segs=24, ring_segs=6)


def gold_bar(m):
    for row in range(3):
        count = 3 - row
        for i in range(count):
            x = (i - (count + 1) / 2 + 1) * 1.6
            # icon gold bar: a frustum (wide bottom, narrow top)
            pts = [(-0.7, 0), (0.7, 0), (0.5, 0.8), (-0.5, 0.8)]
            m.prism([(px + x, py + row * 0.8) for px, py in pts], 2.6, (0, 0, 0), "GOLD", plane="XY", bevel="S")


def gold_treasure_chest(m):
    m.box((5, 2.6, 3.4), (0, 0, 0), "WOOD", bevel="M", bottom=True)
    m.box((4.6, 0.6, 3.0), (0, 2.6, 0), "GOLD", bevel="S", bottom=True)
    for x, y, z in ((-1.2, 3.25, -0.4), (0.3, 3.3, 0.5), (1.4, 3.2, -0.6), (-0.4, 3.35, 0.2)):
        m.cyl(0.42, 0.3, (x, y, z), "GOLD_LIGHT", bevel="XS", verts=12)
    # open lid (tilted back like the original), gold bands, the icon lock
    m.box((5, 0.5, 3.4), (0, 4.3, 1.6), "WOOD", bevel="M", rot=rb_angles(math.radians(-70), 0, 0))
    for x in (-2.3, 2.3):
        m.box((0.35, 2.7, 3.5), (x, 0, 0), "GOLD", bevel="S", bottom=True)
    m.box((0.7, 0.8, 0.35), (0, 1.6, -1.62), "ORANGE", bevel="S", bottom=True)


def question_mark(m, center, facing, size=1.0, color="WHITE"):
    """A chunky '?' made of bars, standing on a wall that faces `facing` (+X/-X/+Z)."""
    cx, cy, cz = center
    pts = [(-0.55, 0.55), (-0.45, 0.95), (-0.1, 1.15), (0.3, 1.1), (0.55, 0.8), (0.45, 0.45), (0.0, 0.2),
           (0.0, -0.25)]

    def to3(u, v, out=0.0):
        u, v = u * size, v * size
        if facing == "+X":
            return (cx + out, cy + v, cz - u)
        if facing == "-X":
            return (cx - out, cy + v, cz + u)
        return (cx + u, cy + v, cz + out)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):  # alternate depth: no coplanar overlaps
        out = 0.02 * (i % 2)
        m.bar(to3(*a, out=out), to3(*b, out=out), 0.3 * min(max(size, 1.0), 1.2), color, round_bar=False,
              bevel=None)
    m.box((0.3 * size, 0.3 * size, 0.36), to3(0.0, -0.7), color, bevel="XS")


def unknown_maker(m):
    m.box((6, 5, 6), (0, 0, 0), "GOLD", bevel="L", bottom=True)
    m.box((6.1, 0.4, 6.1), (0, 0, 0), "ORANGE", bevel="S", bottom=True)  # base band
    for facing, pos in (("+X", (2.9, 2.4, 0)), ("-X", (-2.9, 2.4, 0)), ("+Z", (0, 2.4, 2.9))):
        question_mark(m, pos, facing, size=1.6, color="ORANGE")
    parts.sign_board(m, (0, 2.5, -3.1), 5.5, 1.5, "WHITE", frame="GOLD_LIGHT", frame_w=0.2, depth=0.3,
                     text_plane_z=-3.2, bolts=False)


MODELS.update({
    "Maker_LemonadeStand": {"build": lemonade_stand, "export": "Lemonade Stand"},
    "Maker_VendingMachine": {"build": vending_machine, "export": "Vending Machine"},
    "Maker_MiniGolf": {"build": mini_golf, "export": "Mini Golf"},
    "Maker_ThemePark": {"build": theme_park, "export": "Theme Park", "budget": 3000},
    "Maker_GoldCoin": {"build": gold_coin, "export": "Gold Coin"},
    "Maker_GoldBar": {"build": gold_bar, "export": "Gold Bar"},
    "Maker_GoldTreasureChest": {"build": gold_treasure_chest, "export": "Gold Treasure Chest"},
    "Maker_UnknownMaker": {"build": unknown_maker, "export": "Unknown Maker"},
})
for _t, _front, _shiny, _export in (("Maker_PokeBloxCard", "SKY", False, "PokeBlox Card"),
                                    ("Maker_RarePokeBloxCard", "PURPLE", False, "Rare PokeBlox Card"),
                                    ("Maker_RarePokeBloxCard_v2", "PURPLE", False, "Rare PokeBlox Card (case 2)"),
                                    ("Maker_RarePokeBloxCard_v3", "PURPLE", False, "Rare PokeBlox Card (case 3)"),
                                    ("Maker_RarePokeBloxCard_v4", "PURPLE", False, "Rare PokeBlox Card (case 4)"),
                                    ("Maker_ShinyPokeBloxCard", "GLOW_COOL", True, "Shiny PokeBlox Card")):
    MODELS[_t] = {"build": (lambda f, s, t: (lambda m: pokeblox_card(m, f, s, t)))(_front, _shiny, _t),
                  "export": _export}

BUILDING_MAKERS = {
    "Maker_Apartment": (apartment, "Apartment"), "Maker_CarWash": (car_wash, "Car Wash"),
    "Maker_ToyShop": (toy_shop, "Toy Shop"), "Maker_HouseToRent": (house_to_rent, "House to Rent"),
    "Maker_CoffeeShop": (coffee_shop, "Coffee Shop"), "Maker_BowlingAlley": (bowling_alley, "Bowling Alley"),
    "Maker_Hotel": (hotel, "Hotel"), "Maker_GameStudio": (game_studio, "Game Studio"),
    "Maker_ShoppingMall": (shopping_mall, "Shopping Mall"), "Maker_ApartmentBuilding": (apartment_building,
                                                                                         "Apartment Building"),
    "Maker_PizzaRestaurant": (pizza_restaurant, "Pizza Restaurant"),
}
VEHICLE_MAKERS = {"Maker_FoodTruck": (food_truck, "Food Truck")}


# ----------------------------------------------------------------------------
# Furniture inside the workplaces (Themes.luau), local frames: bottom center, front = -Z (the yard)
# ----------------------------------------------------------------------------

def computer(m):
    """Themes.luau desk()+computer(): desk 4 x 2.5 x 2.5 with a monitor; a red mug (detail)."""
    m.box((4, 0.4, 2.5), (0, 2.1, 0), "WHITE", bevel="M", bottom=True)
    for x in (-1.75, 1.75):
        m.box((0.5, 2.1, 2.3), (x, 0, 0), "WHITE", bevel="S", bottom=True)
    m.box((3.0, 1.2, 0.3), (0, 0.6, 1.0), "STEEL", bevel="XS", bottom=True)  # modesty panel
    m.box((0.6, 0.35, 0.5), (0, 2.5, 0.55), "CHARCOAL", bevel="XS", bottom=True)
    m.box((2.2, 1.6, 0.35), (0, 2.5, 0.5), "CHARCOAL", bevel="S", bottom=True)
    m.box((1.9, 1.2, 0.3), (0, 2.7, 0.33), "GLOW_COOL", glow="GLOW_COOL", bevel="XS", bottom=True)
    m.box((1.8, 0.3, 0.6), (0, 2.5, -0.55), "WHITE", bevel="XS", bottom=True)
    m.cyl(0.2, 0.4, (1.45, 2.5, -0.5), "RED", bevel=None, bottom=True, verts=8)


def hospital_bed(m):
    """Themes.luau bed(): a hospital bed 4 x 2.2 x 7 (head at +Z); a red cross on the headboard (detail)."""
    for x in (-1.7, 1.7):
        for z in (-3.1, 3.1):
            m.cyl(0.22, 0.3, (x, 0, z), "STEEL", bevel=None, bottom=True, verts=8)
    m.box((4, 1.0, 7), (0, 0.3, 0), "WHITE", bevel="M", bottom=True)
    m.box((3.7, 0.4, 6.6), (0, 1.25, 0), "WHITE", bevel="M", bottom=True)
    m.box((4.05, 0.32, 4.0), (0, 1.45, -0.8), "SKY", bevel="M", bottom=True)
    m.box((3.0, 0.5, 1.3), (0, 1.62, 2.6), "WHITE", bevel="M", bottom=True)
    m.box((4.0, 0.9, 0.35), (0, 1.3, 3.32), "STEEL", bevel="S", bottom=True)
    parts.plus_sign(m, (0, 1.68, -1.4), 1.3, 0.4, "RED", plane="XZ")  # red cross on the blanket (seen from above)


def pizzeria_counter(m):
    """Themes.luau:54-58: counter 16 x 3.5 x 2.5 with a green top and a pizza; a cash register (detail)."""
    m.box((16, 3.5, 2.5), (0, 0, 0), "WHITE", bevel="M", bottom=True)
    m.box((15.6, 0.6, 0.3), (0, 1.2, -1.25), "RED", bevel="XS", bottom=True)  # stripe on the front
    m.box((15.6, 0.6, 0.3), (0, 1.8, -1.25), "GREEN", bevel="XS", bottom=True)
    m.box((16, 0.3, 2.7), (0, 3.5, 0), "GREEN", bevel="S", bottom=True)
    # the icon pizza: crust ring, cheese, pepperoni
    m.cyl(1.1, 0.3, (4, 3.65, 0), "TAN", bevel="XS", bottom=True, verts=16)
    m.cyl(0.9, 0.3, (4, 3.7, 0), "GOLD", bevel="XS", bottom=True, verts=16)
    for x, z in ((3.6, -0.35), (4.4, -0.2), (4.0, 0.45)):
        m.cyl(0.22, 0.3, (x, 3.72, z), "BRICK", bevel=None, bottom=True, verts=8)
    # a pizza box at the other end (detail)
    m.box((1.5, 0.3, 1.5), (-5, 3.65, 0.1), "WHITE", bevel="XS", bottom=True)
    m.box((0.9, 0.3, 0.3), (-5, 3.67, -0.55), "RED", bevel=None, bottom=True)


def pizzeria_oven(m):
    """Themes.luau:56-57: the pizza oven (7 x 6 x 5): a round brick dome on a stone base with fire inside;
    a little pile of logs (detail)."""
    m.box((7, 2.2, 5), (0, 0, 0.07), "STONE_DARK", bevel="M", bottom=True)
    m.dome(2.4, 3.7, (0, 2.2, 0.12), "TAN", segs=16, rings=6)  # clay dome
    m.box((3.2, 2.0, 1.2), (0, 2.2, -1.85), "BRICK", bevel="M", bottom=True)  # brick mouth arch
    m.box((2.2, 1.4, 0.3), (0, 2.4, -2.4), "ORANGE", glow="ORANGE", bevel="XS", bottom=True)
    # a little pile of logs on the base, left of the dome (detail)
    for x, y in ((-3.12, 2.47), (-2.6, 2.47), (-2.86, 2.93)):
        m.cyl(0.27, 1.4, (x, y, -1.4), "WOOD", axis="Z", bevel=None, verts=8)


def school_teacher_desk(m):
    """Themes.luau:125 desk(): teacher's desk 4 x 2.5 x 2.5 with a red apple (detail)."""
    m.box((4, 0.4, 2.5), (0, 2.1, 0), "WOOD", bevel="M", bottom=True)  # top at the original 2.5
    m.box((3.8, 2.1, 2.3), (0, 0, 0.0), "WOOD_DARK", bevel="M", bottom=True)
    # the teacher's apple as a big badge on the front panel + a stack of exercise books on top (details)
    m.sphere(0.45, (0, 1.15, -1.15), "RED", scale=(1, 1, 0.34), segs=12, rings=6)
    m.box((0.3, 0.45, 0.3), (0.12, 1.55, -1.18), "GREEN", bevel=None, rot=rb_angles(0, 0, math.radians(-30)))
    m.box((1.3, 0.3, 0.9), (-1.0, 2.33, 0.1), "BLUE", bevel="XS", bottom=True)


def school_student_desk(m):
    """Themes.luau:128: a student desk 3 x 2.2 x 2 with a pencil on it (detail)."""
    m.box((3, 0.35, 2), (0, 1.7, 0), "TAN", bevel="M", bottom=True)
    for x in (-1.25, 1.25):
        m.box((0.4, 1.7, 1.8), (x, 0, 0), "WOOD", bevel="S", bottom=True)
    m.capsule(0.15, 1.4, (0.2, 2.2, -0.2), "GOLD_LIGHT", axis="X", segs=6)


def clinic_chair(m):
    """Themes.luau:109: a dark stool by the clinic desk (2 x 3 x 2) -> a round office chair."""
    m.cyl(0.95, 0.3, (0, 0, 0), "STEEL", bevel=None, bottom=True, verts=10)
    m.cyl(0.2, 1.4, (0, 0.3, 0), "STEEL", bevel=None, bottom=True, verts=8)
    m.cyl(0.95, 0.45, (0, 1.6, 0), "CHARCOAL", bevel="M", bottom=True, verts=14)
    m.box((1.7, 1.05, 0.4), (0, 1.95, 0.75), "CHARCOAL", bevel="M", bottom=True)


def clinic_cabinet(m):
    """Themes.luau:110: a tall white medicine cabinet (4 x 8 x 2.5) with a red cross (detail)."""
    m.box((4, 8, 2.1), (0, 0, 0.2), "WHITE", bevel="M", bottom=True)
    for x in (-0.98, 0.98):
        m.box((1.85, 7.4, 0.3), (x, 0.3, -0.95), "WHITE", bevel="S", bottom=True)
        m.box((0.3, 0.9, 0.3), (x * 0.25, 3.8, -1.1), "STEEL", bevel=None, bottom=True)
    parts.plus_sign(m, (0, 6.1, -1.1), 1.4, 0.45, "RED", plane="XY")


def garage_tire_stack(m):
    """Themes.luau:180: a stack of 4 tires (3.5 wide)."""
    for i in range(4):
        m.cyl(1.75, 0.98, (0, i * 1.0, 0), "CHARCOAL", bevel=0.4, bottom=True, verts=20)
    m.cyl(0.85, 0.3, (0, 3.75, 0), "STEEL", bevel=None, bottom=True, verts=14)


def kid(m, shirt):
    """Props.kid(): a small kid (1.3 x 3.35 x 1.2): legs, shirt, big round head, hair and a face (detail)."""
    for x in (-0.27, 0.27):
        m.box((0.46, 0.9, 0.62), (x, 0, 0), "NAVY", bevel="S", bottom=True)
    m.box((1.3, 1.3, 0.8), (0, 0.9, 0), shirt, bevel="M", bottom=True)
    m.sphere(0.6, (0, 2.75, 0), "SKIN", segs=14, rings=8)
    # hair: a cap tilted back so it frames the face and fully covers the top of the head
    m.dome(0.66, 0.62, (0, 2.84, 0.05), "WOOD_DARK", segs=14, rings=5, rot=rb_angles(math.radians(22), 0, 0))
    for x in (-0.2, 0.2):  # eyes sunk into the head: small dark dots, not goggles
        m.sphere(0.15, (x, 2.7, -0.47), "INK", segs=8, rings=5)


def kid_shirt(template):
    for c in _TEMPLATES[template]["colors"]:
        rgb = tuple(c[:3])
        if rgb == (255, 90, 90):
            return "RED"
        if rgb == (90, 200, 255):
            return "SKY"
        if rgb == (255, 210, 60):
            return "GOLD_LIGHT"
        if rgb == (150, 230, 110):
            return "GREEN"
    return "RED"


# ----------------------------------------------------------------------------
# Debts (Props.luau debtBuilders) - grey/steel = debt (STYLE_GUIDE color roles)
# ----------------------------------------------------------------------------

def debt_credit_card(m):
    """A huge credit card on a stand (s = 1 here; the code scales it with the amount)."""
    m.box((3.38, 0.4, 1.4), (0, 0, 0), "CHARCOAL", bevel="S", bottom=True)
    with m.at((0, 1.8, 0), pitch=-8):
        m.box((4.42, 2.79, 0.3), (0, 0, 0), "BLUE", bevel="M")
        m.box((0.9, 0.7, 0.3), (-1.23, 0.17, -0.1), "GOLD", bevel="XS")  # chip
        m.box((4.42, 0.46, 0.3), (0, 0.79, 0.08), "CHARCOAL", bevel="XS")  # stripe on the back
        for i in range(4):  # card number dots (detail); the CREDIT word stays on the old sign part
            m.box((0.55, 0.36, 0.3), (-1.5 + i * 0.75, -0.25, -0.1), "WHITE", bevel=None)


def debt_car_loan(m):
    """A small grey car with a red LOAN tag (s = 1). Nose at -Z here (like Props.car)."""
    m.box((2.6, 1.1, 4.6), (0, 0.5, 0), "STEEL", bevel="M", bottom=True)
    m.box((2.3, 0.9, 2.4), (0, 1.6, 0.3), "STEEL", bevel="M", bottom=True)
    for x in (-1.16, 1.16):
        m.box((0.3, 0.6, 1.8), (x, 1.75, 0.3), "WINDOW", bevel="XS", bottom=True)
    m.box((1.8, 0.6, 0.3), (0, 1.75, -0.9), "WINDOW", bevel="XS", bottom=True)
    for x in (-1.35, 1.35):
        for z in (-1.5, 1.5):
            parts.wheel(m, (x, 0.5, z), 0.5, 0.4, axis="X", cap=None)
    parts.sign_board(m, (0, 1.2, -2.35), 1.8, 0.8, "RED", frame="WHITE", frame_w=0.15, depth=0.3,
                     text_plane_z=-2.4, bolts=False)


def debt_school_loan(m, books=3):
    """A stack of school books with a graduation cap (books = 2..7; more debt = taller stack)."""
    colors = ["RED", "BLUE", "GREEN", "GOLD", "PURPLE"]
    y = 0.0
    for index in range(1, books + 1):
        turn = ((index % 3) - 1) * 8
        with m.at((0, y + 0.4, 0), yaw=turn):
            m.box((3, 0.8, 2.2), (0, 0, 0), colors[(index - 1) % 5], bevel="S")
            m.box((2.85, 0.55, 0.3), (0, 0, -1.0), "WHITE", bevel=None)  # pages
        y += 0.8
    m.box((1.4, 0.4, 1.4), (0, y, 0), "CHARCOAL", bevel="S", bottom=True)
    with m.at((0, y + 0.32, 0), yaw=45):
        m.box((2.4, 0.3, 2.4), (0, 0, 0), "CHARCOAL", bevel="XS", bottom=True)
    m.box((0.3, 0.9, 0.3), (0.9, y - 0.25, 0.9), "GOLD", bevel=None, bottom=True)  # tassel
    m.cyl(0.25, 0.3, (0, y + 0.47, 0), "GOLD", bevel=None, verts=10)  # button (flat, inside the top)


def debt_bank_loan(m):
    """A grey bank vault with a round door and a gold wheel (s = 1)."""
    m.box((3.2, 3.2, 2.77), (0, 0, 0), "STEEL", bevel="M", bottom=True)
    m.cyl(1.17, 0.3, (0, 1.6, -1.44), "SLATE", axis="Z", bevel="S", verts=18)
    m.torus(0.45, 0.15, (0, 1.6, -1.6), "GOLD", axis="Z", segs=12, ring_segs=6)
    for a in (0, 60, 120):
        r = math.radians(a)
        m.bar((-0.45 * math.cos(r), 1.6 - 0.45 * math.sin(r), -1.6), (0.45 * math.cos(r), 1.6 + 0.45 * math.sin(r),
              -1.6), 0.3, "GOLD", round_bar=False, bevel=None)
    m.box((2.56, 0.64, 0.3), (0, 2.51, -1.41), "CHARCOAL", bevel="XS", bottom=True)  # BANK plate (text on old part)


def debt_other(m):
    """Props.debtCrate(): a grey crate tied with dark straps (side 2.3 for a small debt) + a padlock (detail)."""
    side = 2.3
    m.box((side - 0.1, side - 0.1, side - 0.1), (0, 0, 0), "STEEL", bevel="M", bottom=True)
    m.box((side, side, 0.4), (0, -0.05, 0), "CHARCOAL", bevel="S", bottom=True)
    m.box((0.4, side + 0.04, side + 0.04), (0, -0.07, 0), "CHARCOAL", bevel="S", bottom=True)  # not coplanar
    m.torus(0.22, 0.15, (0, 1.4, -1.12), "STEEL", axis="Z", segs=10, ring_segs=6)
    m.box((0.6, 0.5, 0.3), (0, 0.9, -1.12), "ORANGE", bevel="XS", bottom=True)


MODELS.update({
    "Computer": {"build": computer},
    "HospitalBed": {"build": hospital_bed},
    "Pizzeria_Counter": {"build": pizzeria_counter},
    "Pizzeria_Oven": {"build": pizzeria_oven},
    "School_TeacherDesk": {"build": school_teacher_desk},
    "School_StudentDesk": {"build": school_student_desk},
    "Clinic_Chair": {"build": clinic_chair},
    "Clinic_Cabinet": {"build": clinic_cabinet},
    "Garage_TireStack": {"build": garage_tire_stack},
    "Kid": {"build": lambda m: kid(m, kid_shirt("Kid")), "export": "Kid"},
    "Kid_v2": {"build": lambda m: kid(m, kid_shirt("Kid_v2")), "export": "Kid (blue)"},
    "Kid_v3": {"build": lambda m: kid(m, kid_shirt("Kid_v3")), "export": "Kid (yellow)"},
    "Debt_CreditCard": {"build": debt_credit_card, "export": "Credit Card"},
    "Debt_CarLoan": {"build": debt_car_loan, "export": "Car Loan"},
    "Debt_SchoolLoan": {"build": debt_school_loan, "export": "School Loan"},
    "Debt_BankLoan": {"build": debt_bank_loan, "export": "Bank Loan"},
    "Debt_OtherDebt": {"build": debt_other, "export": "Debt Crate"},
})
for _n in (2, 4, 5, 6, 7):
    MODELS["Debt_SchoolLoan_books%d" % _n] = {"build": (lambda k: (lambda m: debt_school_loan(m, k)))(_n),
                                              "export": "School Loan (%d books)" % _n, "template": "-"}


# ----------------------------------------------------------------------------
# Lobby, Fast Track, auction and podium props
# ----------------------------------------------------------------------------

def _star(outer, inner, cx=0.0, cy=0.0, n=5):
    return [(cx + math.sin(2 * math.pi * k / (2 * n)) * (outer if k % 2 == 0 else inner),
             cy + math.cos(2 * math.pi * k / (2 * n)) * (outer if k % 2 == 0 else inner)) for k in range(2 * n)]


def lobby_trophy(m):
    """Lobby.luau:393-398: the golden trophy on a marble pedestal (icon trophy) with a glowing star on top."""
    m.box((6, 2.7, 6), (0, 0, 0), "CREAM", bevel="L", bottom=True)
    m.box((6.1, 0.3, 6.1), (0, 2.7, 0), "GOLD", bevel="S", bottom=True)
    m.box((3.0, 0.8, 3.0), (0, 3.0, 0), "WOOD", bevel="M", bottom=True)
    m.cyl(0.42, 1.5, (0, 3.8, 0), "GOLD", bevel=None, bottom=True, verts=12)
    m.cyl(1.0, 3.0, (0, 5.25, 0), "GOLD", bevel="M", bottom=True, verts=20, radius_top=1.7)
    m.cyl(1.45, 0.3, (0, 8.0, 0), "ORANGE", bevel="XS", bottom=True, verts=20)
    for x in (-1.85, 1.85):
        m.torus(0.55, 0.18, (x, 7.0, 0), "GOLD", axis="Z", segs=12, ring_segs=6)
    m.prism(_star(0.6, 0.27, cy=6.8), 0.3, (0, 0, -1.45), "GOLD_LIGHT", plane="XY", bevel="XS")
    m.prism(_star(0.6, 0.27, cy=9.3), 0.5, (0, 0, 0), "GOLD_LIGHT", plane="XY", bevel="XS", glow="GOLD_LIGHT")


def lobby_bench(m):
    """Lobby.luau:373-375: a wooden bench (backrest on the wall side, -X here) with a gold plaque (detail)."""
    for z in (-2.3, 2.3):
        m.box((2.0, 1.5, 0.5), (0, 0, z), "CHARCOAL", bevel="S", bottom=True)
        m.box((0.5, 1.75, 0.5), (-1.0, 1.8, z), "CHARCOAL", bevel="XS", bottom=True)
    for x in (-0.55, 0.6):
        m.box((1.1, 0.4, 6), (x, 1.5, 0), "WOOD", bevel="S", bottom=True)
    for y in (2.2, 2.95):
        m.box((0.4, 0.55, 6), (-1.0, y, 0), "WOOD", bevel="S", bottom=True)
    m.box((0.3, 0.35, 1.2), (-0.78, 2.3, 0), "GOLD", bevel="XS", bottom=True)


def lux_sofa(m):
    """Themes.luau:202-203: a white sofa (back at +Z) with gold feet and a gold pillow (detail)."""
    for x in (-3.0, 3.0):
        for z in (-1.1, 1.1):
            m.cyl(0.2, 0.3, (x, 0, z), "GOLD", bevel=None, bottom=True, verts=8)
    m.box((7, 0.9, 3), (0, 0.3, -0.05), "CREAM", bevel="M", bottom=True)
    for x in (-1.65, 1.65):
        m.box((3.2, 0.45, 2.3), (x, 1.2, -0.3), "CREAM", bevel="M", bottom=True)
    m.box((7, 1.8, 0.8), (0, 1.6, 1.15), "CREAM", bevel="M", bottom=True)
    for x in (-3.15, 3.15):
        m.box((0.7, 1.0, 3), (x, 1.2, -0.05), "CREAM", bevel="M", bottom=True)
    m.box((1.0, 0.9, 0.4), (-2.0, 1.7, 0.6), "GOLD", bevel="M", bottom=True)


def lux_glass_table(m):
    """Themes.luau:205: a glass coffee table on gold legs, with a book on the shelf (detail)."""
    for x in (-2.2, 2.2):
        for z in (-1.2, 1.2):
            m.cyl(0.15, 0.9, (x, 0, z), "GOLD", bevel=None, bottom=True, verts=6)
    m.box((4.6, 0.3, 2.6), (0, 0.3, 0), "GOLD", bevel="XS", bottom=True)
    m.box((1.4, 0.3, 1.0), (0.8, 0.6, 0.2), "RED", bevel="XS", bottom=True)
    m.box((5, 0.3, 3), (0, 0.9, 0), "SKY", glass=True, bevel="S", bottom=True)


def lux_safe(m):
    """Themes.luau:207-209: the golden safe full of money (the $$$ stays on the old sign part)."""
    m.box((4, 5, 4), (0, 0, 0.12), "GOLD", bevel="L", bottom=True)
    m.box((3.2, 4.2, 0.3), (0, 0.4, -1.95), "GOLD_LIGHT", bevel="S", bottom=True)
    m.cyl(0.8, 0.3, (0, 2.8, -2.02), "CHARCOAL", axis="Z", bevel="XS", verts=16)
    m.box((1.4, 0.3, 0.3), (0, 2.8, -2.1), "STEEL", bevel=None)
    for x in (-1.35, 1.35):  # rivets (detail)
        for y in (0.8, 4.2):
            m.sphere(0.17, (x, y, -2.05), "GOLD", segs=6, rings=4)


def lux_piano(m):
    """Themes.luau:211-212: a black upright piano with white keys and gold pedals (detail)."""
    m.box((6, 3, 4), (0, 0, 0.05), "CHARCOAL", bevel="M", bottom=True)
    m.box((5.5, 0.3, 0.8), (0, 2.85, -1.65), "WHITE", bevel="XS", bottom=True)
    for i in range(9):
        if i % 7 in (2, 6):
            continue
        m.box((0.3, 0.3, 0.45), (-2.3 + i * 0.6, 3.0, -1.5), "CHARCOAL", bevel=None, bottom=True)
    for x in (-0.5, 0, 0.5):
        m.box((0.3, 0.3, 0.6), (x, 0.0, -2.0), "GOLD", bevel=None, bottom=True)


def dream_pedestal(m):
    """Plots.luau:490-491: the marble pedestal for the dream (top at 1.8, where the dream stands)."""
    m.box((15, 1.5, 15), (0, 0, 0), "CREAM", bevel="L", bottom=True)
    m.box((15.4, 0.3, 15.4), (0, 1.5, 0), "GOLD", bevel="S", bottom=True)
    for x in (-7.45, 7.45):
        for z in (-7.45, 7.45):
            m.sphere(0.35, (x, 0.75, z), "GOLD", segs=8, rings=6)


def collection_showcase(m):
    """Plots.luau:556-557: the wooden COLLECTION table (top at 2.6, where the investments stand)."""
    m.box((11, 2.4, 3), (0, 0, 0), "WOOD", bevel="M", bottom=True)
    for x in (-3.6, 0, 3.6):  # drawers with gold knobs (detail)
        m.box((3.2, 1.6, 0.3), (x, 0.4, -1.45), "WOOD_DARK", bevel="S", bottom=True)
        m.sphere(0.17, (x, 1.2, -1.62), "GOLD", segs=6, rings=4)
    m.box((11.2, 0.3, 3.2), (0, 2.3, 0), "GOLD", bevel="S", bottom=True)


def auction_stage(m):
    """AuctionRoom.luau:63-64: the stage (top at 3.0: the item for sale stands there), glowing gold edge,
    three gold stars on the front (the side the bidders look at, +Z)."""
    m.box((30.6, 2.3, 12.6), (0, 0, 0), "GOLD", glow="GOLD", bevel="S", bottom=True)
    m.box((30, 2.7, 12), (0, 0, 0.2), "BRICK", bevel="M", bottom=True)
    m.box((30, 0.3, 12), (0, 2.7, 0.2), "WOOD", bevel="S", bottom=True)
    for x in (-8, 0, 8):
        m.prism(_star(0.8, 0.36, cx=x, cy=1.35), 0.3, (0, 0, 6.3), "GOLD_LIGHT", plane="XY", bevel=None)


def auction_bidder_desk(m):
    """AuctionRoom.luau:80: a bidder's desk. The old desk turns gold Neon for the top bidder: the new desk has a
    gold glow shell (<name>_Glow_GOLD_T100, invisible by default) that the code shows instead."""
    m.box((4, 2.6, 1.5), (0, 0, 0), "WOOD_DARK", bevel="M", bottom=True)
    m.box((4, 0.4, 1.5), (0, 2.6, 0), "WOOD", bevel="S", bottom=True, rot=rb_angles(math.radians(10), 0, 0))
    m.box((3.6, 0.3, 0.3), (0, 1.0, -0.72), "GOLD", bevel=None, bottom=True)  # gold line (detail)
    m.box((4.08, 3.04, 1.58), (0, -0.02, 0), "GOLD", glow="GOLD@1.0", bevel="M", bottom=True)


def podium_blocks(m):
    """PodiumRoom.luau:79-80: the 1st/2nd/3rd blocks (tops at 9, 7 and 5.5: the winners stand on them).
    The name signs stay on the old plates (front, +Z)."""
    for x, h, color, trim in ((0, 9.0, "GOLD", "GOLD_LIGHT"), (-9, 7.0, "WHITE", "STEEL"), (9, 5.5, "TAN", "WOOD")):
        m.box((8, h, 6), (x, 0, -0.12), color, bevel="L", bottom=True)
        m.box((8.1, 0.6, 6.1), (x, 0, -0.12), trim, bevel="S", bottom=True)
        with m.at((0, 0, 0), yaw=180):  # plates face +Z
            m.box((7.6, h - 0.6, 0.3), (-x, h / 2 - (h - 0.6) / 2, -2.92), color, bevel="S", bottom=True)
        if h == 9.0:  # stars on the sides of the winner's block (detail)
            for s in (-1, 1):
                with m.at((s * 4.05, 0, 0), yaw=90 * s):
                    m.prism(_star(0.9, 0.4, cx=0.12 * s, cy=6.0), 0.3, (0, 0, 0), "GOLD_LIGHT", plane="XY", bevel=None)


MODELS.update({
    "Lobby_Trophy": {"build": lobby_trophy},
    "Lobby_Bench": {"build": lobby_bench},
    "Lux_Sofa": {"build": lux_sofa},
    "Lux_GlassTable": {"build": lux_glass_table},
    "Lux_Safe": {"build": lux_safe},
    "Lux_Piano": {"build": lux_piano},
    "Dream_Pedestal": {"build": dream_pedestal},
    "Collection_Showcase": {"build": collection_showcase},
    "AuctionRoom_Stage": {"build": auction_stage},
    "AuctionRoom_BidderDesk": {"build": auction_bidder_desk},
    "PodiumRoom_Block": {"build": podium_blocks},
})


# ----------------------------------------------------------------------------
# Dream chains and padlock (Plots.luau addChains): generated around the dream's bounding box by code.
# Kit pieces: Dream_ChainSegment (2 studs, two links, along +Z... see IMPORT_PLAN) and Dream_Padlock.
# ----------------------------------------------------------------------------

def chain_segment(m, length=2.4):
    """Two chunky oval links, one standing, one lying, along local Z from 0 to `length` (tiled by code)."""
    step = length / 2
    m.torus(0.5, 0.15, (0, 0, step * 0.5), "CHARCOAL", axis="X", segs=6, ring_segs=4, scale=(1, 1, 1.3))
    m.torus(0.5, 0.15, (0, 0, step * 1.5), "CHARCOAL", axis="Y", segs=6, ring_segs=4, scale=(1, 1, 1.3))


def padlock(m):
    """The icon lock: gold-orange body, steel shackle, dark keyhole (3 x 2.6 x 1 body like the original)."""
    m.box((3, 2.6, 1), (0, 0, 0), "ORANGE", bevel="M")
    m.torus(0.9, 0.2, (0, 1.4, 0), "STEEL", axis="Z", segs=14, ring_segs=6)
    m.cyl(0.32, 0.3, (0, 0.25, -0.5), "INK", axis="Z", bevel=None, verts=10)
    m.box((0.3, 0.6, 0.3), (0, -0.25, -0.52), "INK", bevel=None)


def _canonical_parts(template):
    """The original parts of a template in its local frame: (name, size, local 12-number CFrame)."""
    import json as _j
    root = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "data")
    t = _TEMPLATES[template]
    objs = {o["key"]: o for o in _j.load(open(_os.path.join(root, "objects.json")))}
    inst = {e["id"]: e for e in _j.load(open(_os.path.join(root, "world_instances.json")))}
    o = objs[t["canonical"]]

    def inv(a):
        ax, ay, az, *mm = a
        tt = [mm[0], mm[3], mm[6], mm[1], mm[4], mm[7], mm[2], mm[5], mm[8]]
        return [-(tt[0] * ax + tt[1] * ay + tt[2] * az), -(tt[3] * ax + tt[4] * ay + tt[5] * az),
                -(tt[6] * ax + tt[7] * ay + tt[8] * az)] + tt

    def mul(a, b):
        ax, ay, az, *am = a
        bx, by, bz, *bm = b
        mm = [sum(am[i * 3 + k] * bm[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3)]
        return [am[0] * bx + am[1] * by + am[2] * bz + ax, am[3] * bx + am[4] * by + am[5] * bz + ay,
                am[6] * bx + am[7] * by + am[8] * bz + az] + mm

    fi = inv(o["frame"])
    return [(inst[i]["name"], inst[i]["Size"], mul(fi, inst[i]["CFrame"])) for i in o["part_ids"]]


def dream_chains(m):
    """The template instance: chain segments laid along every original chain bar, and the padlock."""
    from mathutils import Matrix as _M, Vector as _V
    from kit import C as _C, CT as _CT
    for name, size, cf in _canonical_parts("Dream_Chains"):
        if name == "Chain":
            length = size[2]
            n = max(1, int(round(length / 2.4)))
            rot_rb = _M(((cf[3], cf[4], cf[5]), (cf[6], cf[7], cf[8]), (cf[9], cf[10], cf[11])))
            rot_bl = _C @ rot_rb @ _CT
            axis = _V((cf[5], cf[8], cf[11]))  # the bar's local Z in Roblox coords
            start = _V(cf[:3]) - axis * (length / 2)
            seg = length / n
            for i in range(n):
                p = start + axis * (i * seg)
                # a chain segment along the bar
                m.torus(0.5, 0.15, tuple(p + axis * (seg * 0.25)), "CHARCOAL", axis="X", segs=6, ring_segs=4,
                        rot=rot_bl, scale=(1, 1, 1.3))
                m.torus(0.5, 0.15, tuple(p + axis * (seg * 0.75)), "CHARCOAL", axis="Y", segs=6, ring_segs=4,
                        rot=rot_bl, scale=(1, 1, 1.3))
        elif name == "PadlockBody":
            with m.at(tuple(cf[:3])):
                padlock(m)


MODELS.update({
    "Dream_Chains": {"build": dream_chains, "budget": 8000},
    "Dream_ChainSegment": {"build": chain_segment, "template": "-", "export": "ChainSegment"},
    "Dream_Padlock": {"build": padlock, "template": "-", "export": "Padlock"},
})

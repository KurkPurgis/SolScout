"""
nature.py - trees, palms, island.
"""

import parts


def tree(m):
    """Props.tree (Props.luau:352-355): trunk 10 tall (d 1.2) + a round crown (d 6) at 11.5.
    Toy tree: tapered trunk, a cloud-like crown of one big and three small balls, three red apples (detail)."""
    m.cyl(0.66, 9.6, (0, 0, 0), "WOOD", bevel="S", bottom=True, verts=12, radius_top=0.42)
    m.sphere(2.95, (0, 11.55, 0), "LEAF", segs=18, rings=12)
    for x, y, z, r in ((-1.25, 10.4, 0.55, 1.75), (1.3, 10.55, -0.45, 1.75), (0.15, 10.25, 1.15, 1.6)):
        m.sphere(r, (x, y, z), "LEAF", segs=12, rings=8)
    for x, y, z in ((1.9, 11.6, -1.6), (-1.7, 12.6, -1.75), (0.6, 10.0, -2.05)):
        m.sphere(0.32, (x, y, z), "RED", segs=8, rings=6)


MODELS = {
    "Tree": {"build": tree},
}


# ----------------------------------------------------------------------------
# Dream: Private Island (PrivateIslandBuilder.luau, bbox x -25..26.35, y -0.15..14.135, z +-25)
# ----------------------------------------------------------------------------

def dream_private_island(m):
    import math
    # water rings and a fat two-tier sand island (flat top at 3, where everything stands)
    m.cyl(25, 0.6, (0, 0, 0), "WATER", bevel="M", bottom=True, verts=32)
    m.cyl(20, 0.66, (0, 0, 0), "SKY", bevel="M", bottom=True, verts=32)
    m.cyl(17, 2.0, (0, 0, 0), "SAND", bevel="XL", bottom=True, verts=28)
    m.cyl(13.5, 1.0, (0, 2.0, 0), "SAND", bevel="L", bottom=True, verts=24)
    m.cyl(8, 0.4, (-3, 3.0, 2), "GRASS", bevel="S", bottom=True, verts=24)
    for a, d in ((0, 3.5), (70, 2.4), (150, 3.0), (215, 2.2), (290, 2.8)):
        r = math.radians(a)
        m.sphere(d / 2, (math.sin(r) * 16.5, 1.6, math.cos(r) * 16.5), "STONE_DARK", scale=(1.1, 0.9, 1), segs=8,
                 rings=5)
    ground = 3.0
    # palms
    parts.palm(m, (-10, ground, -6), 9.6, lean=2.0, leaf_length=3.8, leaves=5, segs=5, leaf_steps=4, trunk_verts=8)
    parts.palm(m, (6, ground, -9), 8.8, lean=1.5, lean_dir=(-1, 0), leaf_length=3.6, leaves=5, segs=5,
               leaf_steps=4, trunk_verts=8)
    parts.palm(m, (-6, ground, 9), 10.6, lean=1.0, leaf_length=3.8, leaves=5, segs=5, leaf_steps=4, trunk_verts=8)
    # tiki hut: floor, walls, door, window, posts, thatched gable roof
    hx, hy, hz = -3, ground + 0.4, 3
    m.box((7, 0.4, 6), (hx, hy, hz), "WOOD", bevel="S", bottom=True)
    m.box((6, 3.4, 5), (hx, hy + 0.4, hz), "TAN", bevel="M", bottom=True)
    m.box((1.5, 2.4, 0.35), (hx + 0.6, hy + 0.4, hz - 2.55), "WOOD_DARK", bevel="S", bottom=True)
    m.box((1.2, 1.0, 0.35), (hx - 1.7, hy + 1.9, hz - 2.55), "WOOD_DARK", bevel="S", bottom=True)
    for x in (-3.3, 3.3):
        for z in (-2.8, 2.8):
            m.cyl(0.22, 4.1, (hx + x, hy, hz + z), "WOOD", bevel="XS", bottom=True, verts=8)
    roof = [(hz - 4.2, hy + 3.9), (hz + 4.2, hy + 3.9), (hz, hy + 6.4)]
    m.prism(roof, 8.2, (hx, 0, 0), "SAND", plane="ZY", bevel="M")
    # wooden dock with posts, a little boat at its end
    m.box((11, 0.35, 3), (20.5, 1.45, -2), "WOOD", bevel="S", bottom=True)
    for i in range(3):
        for z in (-3.4, -0.6):
            m.cyl(0.22, 2.2, (17 + i * 4, 0.0, z), "WOOD_DARK", bevel="XS", bottom=True, verts=8)
    bx, bz = 25, 2.2
    m.box((2.6, 1.0, 4), (bx, 0.4, bz + 0.5), "WHITE", bevel="M", bottom=True)
    m.prism([(bx - 1.3, bz - 1.5), (bx + 1.3, bz - 1.5), (bx, bz - 3.5)], 1.0, (0, 0.4, 0), "WHITE", plane="XZ",
            bevel="S")
    m.box((2.7, 0.3, 4.1), (bx, 0.95, bz + 0.5), "RED", bevel="XS", bottom=True)
    m.box((2.2, 0.7, 0.35), (bx, 1.4, bz - 0.6), "WINDOW", bevel="XS", bottom=True)
    # hammock between two palms, towel, umbrella
    m.stick((-9.2, ground + 2.2, -5), (-6.5, ground + 2.2, 7.5), 0.45, "PINK", verts=10)
    m.box((2, 0.3, 3.5), (5, ground - 0.15, -3), "BLUE", bevel="XS", bottom=True)
    m.cyl(0.15, 3.5, (7, ground, -3), "WHITE", bevel="XS", bottom=True, verts=8)
    m.cyl(2.25, 0.7, (7, ground + 3.3, -3), "GOLD", bevel="S", bottom=True, verts=16, radius_top=0.25)
    # the treasure chest full of gold (icon chest, detail)
    m.box((2.0, 1.2, 1.3), (8, ground, 6), "WOOD", bevel="M", bottom=True)
    m.cyl(0.65, 2.0, (8, ground + 1.2, 6), "WOOD", axis="X", bevel="S", verts=14)
    m.box((2.08, 0.3, 1.38), (8, ground + 1.05, 6), "GOLD", bevel="XS", bottom=True)
    m.box((0.4, 0.5, 0.3), (8, ground + 0.75, 5.3), "GOLD", bevel="XS", bottom=True)
    m.sphere(0.4, (8.6, ground + 1.75, 6), "GOLD", segs=10, rings=6)


MODELS["Dream_PrivateIsland"] = {"build": dream_private_island, "export": "PrivateIsland",
                                 "mesh_name": "PrivateIsland", "budget": 6000}


def lobby_potted_palm(m):
    """Lobby.luau:386-387: a terracotta pot with a palm leaning toward the hall (+X)."""
    m.cyl(1.15, 1.4, (-1.0, 0, 0), "TAN", bevel="S", bottom=True, verts=16, radius_top=1.25)
    m.cyl(1.35, 0.35, (-1.0, 1.3, 0), "WOOD", bevel="S", bottom=True, verts=16)
    m.cyl(1.05, 0.3, (-1.0, 1.4, 0), "WOOD_DARK", bevel=None, bottom=True, verts=14)
    parts.palm(m, (-1.0, 1.6, 0), 7.5, lean=1.0, leaf_length=4.65, leaves=6, segs=5, leaf_steps=5, trunk_verts=8,
               trunk_r=0.4)


MODELS["Lobby_PottedPalm"] = {"build": lobby_potted_palm}

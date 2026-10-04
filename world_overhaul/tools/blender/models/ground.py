"""
ground.py - floors, yards, lots, pads, paths. Thin originals (0.1-0.2 studs) are sunk into what is below them
so every piece is at least 0.3 thick while the TOP height (what players and objects stand on) stays the same.
"""

import parts


def workplace_yard(m, luxury=False):
    """Plots.luau:130-132: yard floor 48 x 30 in front of the building (y -1..0) + a path to the door."""
    slab = "CREAM" if luxury else "STONE_DARK"
    m.box((48, 1, 30), (0, -0.5, -9), slab, bevel="M")
    if luxury:
        # red carpet runner (top 0.1 like the original) with gold edging (detail)
        m.box((7, 0.3, 30), (0, -0.2, -9), "BRICK", bevel="S", bottom=True)
        for x in (-3.65, 3.65):
            m.box((0.3, 0.3, 30), (x, -0.2, -9), "GOLD", bevel="XS", bottom=True)
    else:
        # stepping stones instead of a flat stripe (detail): 8 rounded tiles, top at 0.1
        n, gap = 8, 0.5
        length = (30 - gap * (n - 1)) / n
        for i in range(n):
            z = -24 + i * (length + gap) + length / 2
            m.box((7, 0.3, length), (0, -0.2, z), "STONE", bevel="M", bottom=True)


def maker_lot(m):
    """Plots.luau:176: the lot where a Money Maker stands (11 x 9.5, top at 1.0 in its own frame)."""
    m.box((11, 1, 9.5), (0, 0, 0), "SAND", bevel="M", bottom=True)
    # a little gold coin plaque on the side that faces the plot (detail)
    m.cyl(0.38, 0.3, (0, 0.5, -4.72), "GOLD", axis="Z", bevel="XS", verts=14)
    m.cyl(0.2, 0.32, (0, 0.5, -4.74), "GOLD_LIGHT", axis="Z", bevel="XS", verts=10)


def debt_pad(m):
    """Plots.luau:218: grey pad where the debts stand (12 x 10, top at 0.2)."""
    m.box((12, 0.3, 10), (0, -0.1, 0), "STEEL", bevel="M", bottom=True)
    m.box((11, 0.3, 9), (0, -0.08, 0), "SLATE", bevel="S", bottom=True)


MODELS = {
    "Workplace_Yard_v2": {"build": lambda m: workplace_yard(m, False)},
    "Workplace_Yard": {"build": lambda m: workplace_yard(m, True)},
    "Workplace_MakerLot": {"build": maker_lot},
    "Workplace_DebtPad": {"build": debt_pad},
}


def plaza_disc(m):
    """Plaza.luau:52: the round stone plaza (90 wide, 0.4 tall). Darker outer ring + lighter inner disc
    (0.04 higher, so the two never fight), with a ring of small gold studs (detail: coins set in the stone)."""
    import math
    m.cyl(45, 0.36, (0, 0, 0), "STONE_DARK", bevel="M", bottom=True, verts=64)
    m.cyl(42.6, 0.4, (0, 0, 0), "STONE", bevel="S", bottom=True, verts=64)
    for i in range(16):
        a = 2 * math.pi * (i + 0.5) / 16
        m.cyl(0.6, 0.3, (math.cos(a) * 43.8, 0.08, math.sin(a) * 43.8), "GOLD", bevel="XS", bottom=True, verts=12)


def plaza_path(m):
    """Plaza.luau:58: a stone path from the plaza to a workplace (10 x 0.4 x 48): big rounded paving
    tiles on a darker bed."""
    m.box((10, 0.3, 48), (0, 0, 0), "STONE_DARK", bevel="S", bottom=True)
    n, gap = 8, 0.45
    length = (48 - gap * (n + 1)) / n
    for i in range(n):
        z = -24 + gap + i * (length + gap) + length / 2
        m.box((9.1, 0.3, length), (0, 0.1, z), "STONE", bevel="M", bottom=True)


def city_ground(m):
    """Plaza.luau:35: the grass ground of a city (366 x 2 x 366, top at 0)."""
    m.box((366, 2, 366), (0, -2, 0), "GRASS", bevel="L", bottom=True)


MODELS["Plaza_Disc"] = {"build": plaza_disc, "budget": 6000}
MODELS["Plaza_Path"] = {"build": plaza_path}
MODELS["City_Ground"] = {"build": city_ground}


def lobby_floor(m):
    """Lobby.luau:332: the marble floor (148 x 100, top at 1). Checkerboard of cream and stone tiles."""
    m.box((148, 1, 100), (0, 0, 0), "CREAM", bevel="M", bottom=True)
    size = 10.0
    for i in range(14):
        for j in range(10):
            if (i + j) % 2:
                continue
            x = -70 + i * size + size / 2
            z = -50 + j * size + size / 2
            m.box((size - 0.4, 0.3, size - 0.4), (x, 0.73, z), "STONE", bevel="XS", bottom=True)


def lobby_carpet(m):
    """Lobby.luau:333-334: the red carpets (top at 1.1) with gold edges (detail)."""
    for (x, z, sx, sz) in ((0, 8, 8, 56), (0, -20, 132, 6)):
        m.box((sx, 0.3, sz), (x, 0.8, z), "BRICK", bevel="S", bottom=True)
    for x in (-3.85, 3.85):
        m.box((0.3, 0.3, 50), (x, 0.82, 11.0), "GOLD", bevel=None, bottom=True)
    for z in (-22.85, -17.15):
        m.box((131.4, 0.3, 0.3), (0, 0.82, z), "GOLD", bevel=None, bottom=True)


def lobby_spawn(m):
    """Lobby.luau:406-414: the spawn pad (10 x 1 x 10). The SpawnLocation part stays (invisible).
    A round marble pad with a gold ring and a gold star (detail)."""
    m.cyl(5.0, 1.0, (0, 0, 0), "CREAM", bevel="M", bottom=True, verts=28)
    m.torus(4.2, 0.2, (0, 0.95, 0), "GOLD", axis="Y", segs=28, ring_segs=6)
    star = [(math.sin(2 * math.pi * k / 10) * (2.2 if k % 2 == 0 else 1.0),
             math.cos(2 * math.pi * k / 10) * (2.2 if k % 2 == 0 else 1.0)) for k in range(10)]
    m.prism(star, 0.3, (0, 0.82, 0), "GOLD", plane="XZ", bevel=None)


def auction_bidder_pad(m):
    """AuctionRoom.luau:81: the floor pad where a bidder stands."""
    m.box((4.5, 0.4, 4), (0, 0, 0), "GOLD", bevel="M", bottom=True)
    m.box((4.0, 0.42, 3.5), (0, 0, 0), "WOOD_DARK", bevel="S", bottom=True)


def baseplate(m):
    """default.project.json: the 512 x 20 x 512 grass Baseplate under the lobby (scripts raycast it by name;
    the old part stays)."""
    m.box((512, 20, 512), (0, -20, 0), "GRASS", bevel="L", bottom=True)


import math  # noqa: E402

MODELS["Lobby_Floor"] = {"build": lobby_floor, "budget": 6000}
MODELS["Lobby_Carpet"] = {"build": lobby_carpet}
MODELS["Lobby_Spawn"] = {"build": lobby_spawn}
MODELS["AuctionRoom_BidderPad"] = {"build": auction_bidder_pad}
MODELS["Baseplate"] = {"build": baseplate}

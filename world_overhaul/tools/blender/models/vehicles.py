"""
vehicles.py - cars, bus, trucks, the dream yacht and jet. Toy proportions like the icon car/bus/yacht/jet:
short, tall, chunky, big wheels, rounded everything.
"""

import math

import parts
from kit import rb_angles


# ----------------------------------------------------------------------------
# Dream: Supercar  (SupercarBuilder.luau, bbox x +-2.8, y 0..3.455, z -6.5..5.7, front = -Z)
# ----------------------------------------------------------------------------

def dream_supercar(m):
    red = "RED"
    # body: one fat side profile (z, y) extruded across the width, nose low, tail high
    body = [(-6.2, 0.5), (5.2, 0.5), (5.3, 1.9), (2.6, 2.1), (-2.2, 2.0), (-5.2, 1.6), (-6.5, 1.2), (-6.45, 0.75)]
    m.prism(body, 4.8, (0, 0, 0), red, plane="ZY", bevel="M")
    m.box((4.4, 0.4, 10.6), (0, 0.55, -0.4), "CHARCOAL", bevel="S")  # chassis under the body
    # cabin: shiny glass bubble with a red roof
    cabin = [(-2.25, 1.95), (3.9, 2.0), (2.3, 3.15), (-0.5, 3.15)]
    m.prism(cabin, 3.8, (0, 0, 0), "WINDOW", plane="ZY", bevel="S")
    m.box((3.4, 0.3, 2.6), (0, 3.15, 0.9), red, bevel="S")
    for x in (-0.55, 0.55):  # racing stripes on the roof and the hood (detail 1)
        m.box((0.45, 0.3, 2.5), (x, 3.18, 0.9), "WHITE", bevel="XS")
        m.box((0.45, 0.3, 3.2), (x, 1.66, -3.75), "WHITE", bevel="XS", rot=rb_angles(math.radians(-7), 0, 0))
    # spoiler on two struts
    for x in (-1.3, 1.3):
        m.box((0.3, 0.95, 0.5), (x, 2.0, 4.5), "CHARCOAL", bevel="XS", bottom=True)
    m.box((4.9, 0.3, 1.0), (0, 2.95, 4.5), red, bevel="S", bottom=True)
    # lights, mirrors, side intakes, exhausts, number plate (the DREAM text stays on the old plate part)
    for s in (-1, 1):
        m.box((1.1, 0.35, 0.4), (s * 1.45, 1.3, -6.25), "GLOW_WARM", glow="GLOW_WARM", bevel="S")
        m.box((1.2, 0.3, 0.3), (s * 1.45, 1.55, 5.2), "BRICK", bevel="XS")
        m.box((0.45, 0.3, 0.4), (s * 2.2, 2.35, -1.6), red, bevel="XS")
        m.box((0.3, 0.55, 1.3), (s * 2.35, 1.2, 2.0), "CHARCOAL", bevel="XS")
        m.cyl(0.24, 0.5, (s * 0.7, 0.95, 5.45), "STEEL", axis="Z", bevel="XS", verts=10)
    m.box((1.4, 0.45, 0.3), (0, 0.95, 5.17), "WHITE", bevel="XS")
    # big toy wheels with gold caps (detail 2)
    for z in (-3.4, 3.3):
        for s in (-1, 1):
            parts.wheel(m, (s * 2.15, 1.0, z), 1.0, 0.8, axis="X", cap="GOLD")


# ----------------------------------------------------------------------------
# Dream: Yacht (YachtBuilder.luau, bbox x -5.675..5.6, y -0.5..14.3, z -20.05..22.55)
# ----------------------------------------------------------------------------

def hull_outline(half_width, stern_z, straight_z, tip_z, scale=1.0):
    """Top view of a hull (x, z): straight sides, then a round pointed bow."""
    right = [(half_width, stern_z), (half_width, straight_z)]
    steps = 6
    for i in range(1, steps):
        t = i / steps
        x = half_width * math.cos(t * math.pi / 2) ** 0.8
        z = straight_z + (tip_z - straight_z) * math.sin(t * math.pi / 2)
        right.append((x, z))
    right.append((0.0, tip_z))
    left = [(-x, z) for x, z in reversed(right[:-1])]
    pts = right + left
    return [(x * scale, z) for x, z in pts]


def dream_yacht(m):
    hw = 5.45  # the hull side stays 0.05 inside the old hull face, so the DREAMER name never flickers
    m.prism(hull_outline(hw, 20.0, -7.0, -19.95), 1.5, (0, 0, 0), "NAVY", plane="XZ", bevel="M")
    m.prism(hull_outline(hw, 20.0, -7.0, -19.95), 3.55, (0, 1.45, 0), "WHITE", plane="XZ", bevel="M")
    m.prism(hull_outline(hw + 0.06, 19.9, -7.0, -19.7), 0.5, (0, 3.45, 0), "NAVY", plane="XZ", bevel="XS")
    m.prism(hull_outline(hw - 0.35, 19.6, -7.0, -18.9), 0.32, (0, 4.95, 0), "TAN", plane="XZ", bevel="XS")
    for s in (-1, 1):
        for i in range(5):
            m.cyl(0.38, 0.3, (s * 5.42, 2.45, -5 + i * 3.2), "SKY", axis="X", bevel=None, verts=10)
    floor = 5.25
    # main cabin with a sloped windshield and a navy window band
    m.box((8, 3.4, 14), (0, floor, 6), "WHITE", bevel="M", bottom=True)
    m.prism([(-4.1, floor), (-1.0, floor), (-1.0, floor + 3.3)], 8, (0, 0, 0), "WINDOW", plane="ZY", bevel="S")
    for s in (-1, 1):
        m.box((0.35, 1.2, 12), (s * 3.95, floor + 1.6, 6), "NAVY", bevel="XS", bottom=True)
    m.box((3.0, 2.6, 0.35), (0, floor, 13.05), "WINDOW", bevel="XS", bottom=True)
    # flybridge: floor, little windshield, console, wheel, seat
    bridge = floor + 3.4
    m.box((8, 0.3, 13), (0, bridge, 5.5), "WHITE", bevel="S", bottom=True)
    m.prism([(-1.1, bridge + 0.3), (0.3, bridge + 0.3), (0.3, bridge + 1.3)], 7.5, (0, 0, 0), "WINDOW", plane="ZY",
            bevel="XS")
    m.box((2.6, 1.4, 1.4), (0, bridge + 0.3, 1.2), "WHITE", bevel="S", bottom=True)
    m.torus(0.45, 0.15, (0, bridge + 1.95, 2.0), "STEEL", axis="Z", segs=12, ring_segs=6)
    m.box((3.0, 0.8, 1.2), (0, bridge + 0.3, 3.8), "WHITE", bevel="S", bottom=True)
    m.box((3.0, 1.2, 0.45), (0, bridge + 1.1, 4.4), "WHITE", bevel="S", bottom=True)
    # hard top on four poles, radar, antenna with a red tip
    top = bridge + 3.0
    for x in (-2.6, 2.6):
        for z in (2.5, 9.0):
            m.cyl(0.17, 2.7, (x, bridge + 0.3, z), "STEEL", bevel="XS", bottom=True, verts=8)
    m.box((7.5, 0.35, 9.5), (0, top, 5.7), "WHITE", bevel="S", bottom=True)
    m.sphere(0.6, (0, top + 0.85, 7.0), "WHITE", segs=12, rings=8)
    m.cyl(0.65, 0.3, (0, top + 0.35, 7.0), "CHARCOAL", bevel="XS", bottom=True, verts=12)
    m.cyl(0.15, 1.9, (1.5, top + 0.35, 8.0), "STEEL", bevel="XS", bottom=True, verts=8)
    m.sphere(0.2, (1.5, top + 2.3, 8.0), "RED", segs=8, rings=5)
    # railings: chunky posts and a round top rail along both sides and around the bow
    rail_y = floor + 1.25
    for s in (-1, 1):
        x = s * 4.95
        for i in range(7):
            z = -7 + i * 4.3
            m.cyl(0.15, 1.25, (x, floor, z), "STEEL", bevel="XS", bottom=True, verts=8)
        m.stick((x, rail_y, -7.0), (x, rail_y, 18.8), 0.17, "STEEL", verts=8)
        bow = [(x, -7.0), (s * 4.2, -11.5), (s * 2.6, -15.5), (s * 0.9, -18.2)]
        for (x0, z0), (x1, z1) in zip(bow, bow[1:]):
            m.stick((x0, rail_y, z0), (x1, rail_y, z1), 0.17, "STEEL", verts=8)
            m.cyl(0.15, 1.25, (x1, floor - 0.05, z1), "STEEL", bevel="XS", bottom=True, verts=8)
    # sunbeds on the front deck
    for s in (-1, 1):
        m.box((2, 0.45, 4), (s * 1.5, floor, -9.0), "WHITE", bevel="XS", bottom=True)
        m.box((2, 0.45, 0.85), (s * 1.5, floor + 0.45, -10.6), "BLUE", bevel="XS", bottom=True)
    # back deck: sofa with pillows, table, flag
    m.box((8, 0.8, 1.4), (0, floor, 18.4), "WHITE", bevel="S", bottom=True)
    m.box((8, 1.0, 0.45), (0, floor + 0.8, 18.9), "WHITE", bevel="S", bottom=True)
    for x in (-2.4, 0, 2.4):
        m.box((1.6, 0.6, 0.4), (x, floor + 0.8, 18.55), "BLUE", bevel="XS", bottom=True)
    m.cyl(0.18, 0.9, (0, floor, 16.0), "STEEL", bevel="XS", bottom=True, verts=8)
    m.box((2.5, 0.3, 1.5), (0, floor + 0.9, 16.0), "TAN", bevel="S", bottom=True)
    m.cyl(0.15, 3.6, (0, floor, 19.75), "STEEL", bevel="XS", bottom=True, verts=8)
    m.box((0.3, 1.0, 1.6), (0, floor + 2.5, 20.6), "RED", bevel="XS", bottom=True)
    # life ring on the back of the cabin (detail)
    m.torus(0.62, 0.2, (2.4, floor + 1.6, 13.2), "RED", axis="Z", segs=16, ring_segs=6)
    for a in (0, 90, 180, 270):
        r = math.radians(a)
        m.box((0.3, 0.3, 0.45), (2.4 + 0.62 * math.cos(r), floor + 1.6 + 0.62 * math.sin(r), 13.2), "WHITE", bevel="XS")
    # swim platform and ladder at the back
    m.box((10, 0.4, 2.5), (0, 1.2, 21.25), "TAN", bevel="S", bottom=True)
    for x in (-0.6, 0.6):
        m.cyl(0.15, 2.0, (x, -0.5, 22.25), "STEEL", bevel="XS", bottom=True, verts=8)
    for i in range(3):
        m.box((1.5, 0.3, 0.3), (0, -0.4 + i * 0.6, 22.25), "STEEL", bevel="XS", bottom=True)
    # anchor on the left of the bow
    ax = -(hw + 0.12)
    m.box((0.3, 1.6, 0.3), (ax, 2.6, -6.0), "CHARCOAL", bevel="XS", bottom=True)
    m.box((0.3, 0.3, 1.0), (ax, 4.05, -6.0), "CHARCOAL", bevel="XS", bottom=True)
    m.torus(0.55, 0.15, (ax, 2.95, -6.0), "CHARCOAL", axis="X", segs=12, ring_segs=6)


# ----------------------------------------------------------------------------
# Dream: Private Jet (PrivateJetBuilder.luau, bbox x +-14.316, y 0..12.46, z -14..19.1)
# ----------------------------------------------------------------------------

def dream_private_jet(m):
    by, r = 4.6, 2.1
    white = "WHITE"
    # fat toy body: tube + long round nose + tail cone that rises a little
    m.cyl(r, 22.0, (0, by, 0), white, axis="Z", bevel=None, verts=24)
    m.sphere(r, (0, by, -11.0), white, scale=(1, 1, 1.4), segs=20, rings=12)
    m.stick((0, by, 10.9), (0, by + 0.9, 18.0), r, white, radius_b=1.0, verts=24, bevel=None)
    m.sphere(1.0, (0, by + 0.9, 18.1), white, segs=12, rings=8)
    # windshield and round windows (icon jet)
    m.sphere(1.25, (0, by + 1.05, -11.8), "NAVY", scale=(1.25, 0.55, 1.0), segs=14, rings=8)
    for s in (-1, 1):
        for i in range(7):
            m.cyl(0.38, 0.3, (s * 2.0, by + 0.55, -6.0 + i * 2.1), "NAVY", axis="X", bevel=None, verts=10)
        # blue and gold stripes along the body
        m.box((0.35, 0.5, 21.0), (s * 1.97, by - 0.45, -0.3), "BLUE", bevel="XS")
        m.box((0.35, 0.3, 21.0), (s * 1.9, by - 0.95, -0.3), "GOLD", bevel="XS")
    # swept wings with gold winglets
    for s in (-1, 1):
        wing = [(s * 1.6, -1.3), (s * 1.6, 3.3), (s * 14.0, 7.9), (s * 14.0, 5.4)]
        if s < 0:
            wing = list(reversed(wing))
        m.prism(wing, 0.45, (0, by - 1.65, 0), "STEEL", plane="XZ", bevel="S")
        m.box((0.3, 1.9, 2.0), (s * 14.15, by - 1.65, 6.5), "GOLD", bevel="S", bottom=True,
              rot=rb_angles(0, 0, math.radians(-8 * s)))
        # engines on the back of the body
        x = s * (r + 1.3)
        m.box((1.6, 0.45, 2.4), (s * (r + 0.45), by + 0.75, 8.5), white, bevel="S", bottom=True)
        m.capsule(0.95, 5.0, (x, by + 1.0, 8.5), white, axis="Z", segs=14)
        m.cyl(0.75, 0.3, (x, by + 1.0, 5.95), "CHARCOAL", axis="Z", bevel="XS", verts=14)
        m.cyl(0.6, 0.3, (x, by + 1.0, 11.05), "CHARCOAL", axis="Z", bevel="XS", verts=14)
    # tail fin (blue like the icon jet) with a gold star (detail) and the T-tail
    fin_bottom = by + 1.4
    m.prism([(13.6, fin_bottom), (17.6, fin_bottom), (19.0, 12.1), (17.1, 12.1)], 0.5, (0, 0, 0), "BLUE",
            plane="ZY", bevel="S")
    star = [(math.sin(2 * math.pi * k / 10) * (0.65 if k % 2 == 0 else 0.28),
             math.cos(2 * math.pi * k / 10) * (0.65 if k % 2 == 0 else 0.28)) for k in range(10)]
    m.prism([(z + 16.9, y + 9.3) for z, y in star], 0.62, (0, 0, 0), "GOLD", plane="ZY", bevel="XS")
    m.box((10, 0.32, 2.4), (0, 12.12, 17.9), white, bevel="S", bottom=True)
    m.box((10.1, 0.34, 0.45), (0, 12.11, 19.1 - 0.25), "GOLD", bevel="XS", bottom=True)
    # landing gear
    for x, z, d in ((0, -9.5, 1.2), (-1.8, 3.5, 1.5), (1.8, 3.5, 1.5)):
        m.cyl(0.17, by - r - d / 2 + 0.4, (x, d / 2, z), "STEEL", bevel="XS", bottom=True, verts=8)
        parts.wheel(m, (x, d / 2, z), d / 2, 0.6, axis="X", cap=None)
    # open door with stairs on the left (detail)
    dz = -8.5
    m.box((0.35, 2.6, 1.5), (-(r - 0.05), by - 1.6, dz), "CREAM", bevel="XS", bottom=True)
    for i in range(4):
        m.box((0.8, 0.35, 1.5), (-(r + 0.5 + i * 0.75), by - 1.75 - i * 0.8, dz), white, bevel="XS")
    m.stick((-(r + 0.3), by - 0.2, dz + 0.75), (-(r + 3.2), 1.2, dz + 0.75), 0.15, "GOLD", verts=8)


MODELS = {
    "Dream_Supercar": {"build": dream_supercar, "export": "Supercar", "mesh_name": "Supercar"},
    "Dream_Yacht": {"build": dream_yacht, "export": "Yacht", "mesh_name": "Yacht"},
    "Dream_PrivateJet": {"build": dream_private_jet, "export": "PrivateJet", "mesh_name": "PrivateJet"},
}


from models.props import VEHICLE_MAKERS  # noqa: E402

for _t, (_fn, _export) in VEHICLE_MAKERS.items():
    MODELS[_t] = {"build": _fn, "export": _export}


# ----------------------------------------------------------------------------
# Job vehicles (Themes.luau). Length along X, nose at -X, the long side faces the yard (-Z).
# ----------------------------------------------------------------------------

def depot_bus(m):
    """Themes.luau:70-79: the yellow city bus in the bus depot (20 x 7 x 6). Icon bus."""
    m.box((20, 5.8, 5), (0, 1.2, 0), "GOLD", bevel="L", bottom=True)
    m.box((19.6, 0.6, 5.2), (0, 1.0, 0), "CHARCOAL", bevel="S", bottom=True)  # bumper band
    for s in (-1, 1):  # window rows on both long sides
        for i in range(6):
            x = -6.4 + i * 2.75
            m.box((2.3, 1.7, 0.3), (x, 4.05, s * 2.52), "WINDOW", bevel="S", bottom=True)
        m.box((16.6, 0.35, 0.3), (0.4, 3.7, s * 2.55), "WHITE", bevel="XS", bottom=True)
    m.box((0.3, 2.2, 4.0), (-9.95, 3.6, 0), "WINDOW", bevel="S", bottom=True)  # windshield
    m.box((0.35, 0.7, 3.2), (-9.9, 6.0, 0), "GLOW_WARM", glow="GLOW_WARM", bevel="XS", bottom=True)  # route sign
    for z in (-1.6, 1.6):
        m.box((0.3, 0.55, 0.8), (-9.95, 2.2, z), "GLOW_WARM", glow="GLOW_WARM", bevel="XS", bottom=True)
        m.box((0.3, 0.55, 0.8), (9.95, 2.2, z), "RED", bevel="XS", bottom=True)
    # folding door on the yard side (detail)
    m.box((1.9, 3.6, 0.3), (-7.6, 1.5, -2.6), "WINDOW", bevel="S", bottom=True)
    m.box((0.3, 3.6, 0.32), (-7.6, 1.5, -2.62), "WHITE", bevel="XS", bottom=True)
    for x in (-6.5, 6.5):
        for z in (-2.6, 2.6):
            parts.wheel(m, (x, 1.1, z), 1.1, 0.8, axis="Z", cap="STEEL")


def toy_car(m, body, cabin_shift=0.5, y0=0.0):
    """Props.car(): a toy car (icon car) 8 long along X, nose at -X. y0 = how high it stands."""
    m.box((8, 1.8, 4), (0, y0 + 0.6, 0), body, bevel="L", bottom=True)
    m.box((4, 1.5, 3.6), (cabin_shift, y0 + 2.4, 0), body, bevel="L", bottom=True)
    for s in (-1, 1):
        m.box((3.0, 0.9, 0.3), (cabin_shift, y0 + 2.7, s * 1.82), "WINDOW", bevel="S", bottom=True)
    m.box((0.3, 0.9, 2.8), (cabin_shift - 2.0, y0 + 2.7, 0), "WINDOW", bevel="S", bottom=True)
    m.box((0.3, 0.9, 2.8), (cabin_shift + 2.0, y0 + 2.7, 0), "WINDOW", bevel="S", bottom=True)
    for z in (-1.3, 1.3):
        m.box((0.3, 0.45, 0.8), (-3.97, y0 + 1.5, z), "GLOW_WARM", glow="GLOW_WARM", bevel="XS")
        m.box((0.3, 0.45, 0.8), (3.97, y0 + 1.5, z), "RED", bevel="XS")
    for x in (-2.6, 2.6):
        for z in (-2.05, 2.05):
            parts.wheel(m, (x, y0 + 0.8, z), 0.8, 0.7, axis="Z", cap=None)


def police_car(m):
    """Themes.luau:142-145: white police car with red and blue lights (8 x 4.4 x 4.8)."""
    toy_car(m, "WHITE")
    for s in (-1, 1):  # navy doors with a gold star (detail)
        m.box((3.6, 1.1, 0.3), (0.3, 0.95, s * 2.0), "NAVY", bevel="S", bottom=True)
        m.cyl(0.32, 0.3, (0.3, 1.5, s * 2.12), "GOLD", axis="Z", bevel=None, verts=10)
    m.box((1.2, 0.3, 2.6), (0.5, 3.9, 0), "CHARCOAL", bevel="XS", bottom=True)
    m.box((0.8, 0.5, 0.8), (0.5, 3.95, 0.8), "RED", glow="RED", bevel="S", bottom=True)
    m.box((0.8, 0.5, 0.8), (0.5, 3.95, -0.8), "BLUE", glow="BLUE", bevel="S", bottom=True)


def garage_car_lift(m):
    """Themes.luau:175-177: a red car up on a two-post lift (9 x 6.9 x 4.8)."""
    for x in (-4, 4):
        m.box((1, 4, 1), (x, 0, 0), "CHARCOAL", bevel="S", bottom=True)
        for y in (0.6, 1.8, 3.0):  # hazard stripes (detail)
            m.box((1.04, 0.5, 1.04), (x, y, 0), "GOLD", bevel="XS", bottom=True)
        m.box((1.6, 0.3, 4.4), (x * 0.75, 3.55, 0), "STEEL", bevel="XS", bottom=True)
    toy_car(m, "RED", y0=3.0)


MODELS["Depot_Bus"] = {"build": depot_bus}
MODELS["Police_Car"] = {"build": police_car}
MODELS["Garage_CarLift"] = {"build": garage_car_lift}

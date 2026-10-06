"""Blocky R6-style player for the thumbnail (built, not a game asset).

R6 proportions in studs: legs 1x1x2, torso 2x1x2, arms 1x1x2, rounded head ~1.25.
Work clothes (orange shirt, dark trousers, boots, belt), tired posture, head tilted
back to look up, right arm reaching toward `reach_dir` with an open hand.
Local frame: he faces +Y, his right is +X.
"""
import math
from mathutils import Vector, Matrix
from sceneutil import mat, mesh_box, empty, parent_keep, rot


def build(L, coll, reach_dir_world, look_up=28.0, slouch=-5.0):
    shirt = mat("Char_Shirt", L["shirt"], rough=0.8)
    pants = mat("Char_Trousers", L["trousers"], rough=0.8)
    skin = mat("Char_Skin", L["skin"], rough=0.55)
    hair = mat("Char_Hair", L["hair"], rough=0.7)
    dark = mat("Char_Boots", (0.08, 0.06, 0.05), rough=0.6)
    face = mat("Char_Face", (0.06, 0.05, 0.05), rough=0.5)

    root_m = Matrix.Translation(L["loc"]) @ rot(z=L["yaw"])
    root = empty("Character", coll, root_m)
    parts = {}

    def add(name, size, center, material, pivot=None, bevel=0.0):
        """Box in character-local space, child of `pivot` (an empty) or root."""
        o = mesh_box(name, size, material=material, bevel=bevel, coll=coll)
        o.matrix_world = (pivot.matrix_world if pivot else root.matrix_world) @ Matrix.Translation(center)
        parent_keep(o, pivot or root)
        parts[name] = o
        return o

    def pivot(name, local_pos, local_rot, parent=None):
        p = empty(name, coll, (parent.matrix_world if parent else root.matrix_world)
                  @ Matrix.Translation(local_pos) @ local_rot)
        parent_keep(p, parent or root)
        return p

    # legs, boots
    for side, x in (("L", -0.5), ("R", 0.5)):
        add(f"Leg{side}", (0.98, 1.0, 1.75), (x, 0, 1.125), pants)
        add(f"Boot{side}", (1.0, 1.2, 0.3), (x, 0.08, 0.15), dark)
    # torso on a hip pivot: slight forward slouch
    hip = pivot("Hip", (0, 0, 2.0), rot(x=slouch))
    add("Torso", (2.0, 1.0, 1.75), (0, 0, 1.125), shirt, hip)
    add("Belt", (2.04, 1.04, 0.25), (0, 0, 0.125), dark, hip)
    add("Collar", (0.9, 0.3, 0.12), (0, 0.42, 1.98), shirt, hip)

    # left arm hanging, a little forward and out (tired)
    shL = pivot("ShoulderL", (-1.5, 0, 1.75), rot(x=-8, y=-6), hip)
    add("ArmL", (1.0, 1.0, 1.55), (0, 0, -0.525), shirt, shL)
    add("HandL", (0.92, 0.92, 0.45), (0, 0, -1.525), skin, shL)

    # right arm reaching: shoulder pivot whose -Z points along reach_dir_world
    hip_world = hip.matrix_world
    sh_world_pos = hip_world @ Vector((1.5, 0, 1.75))
    d = Vector(reach_dir_world).normalized()
    q = d.to_track_quat('-Z', 'Y').to_matrix().to_4x4()
    shR = empty("ShoulderR", coll, Matrix.Translation(sh_world_pos) @ q)
    parent_keep(shR, hip)
    add("ArmR", (1.0, 1.0, 1.55), (0, 0, -0.525), shirt, shR)
    # open hand: palm + four spread fingers + thumb
    add("PalmR", (0.92, 0.42, 0.5), (0, 0, -1.55), skin, shR)
    for i, (fx, spread) in enumerate(((-0.33, -14), (-0.11, -5), (0.11, 5), (0.33, 14))):
        fp = pivot(f"FingerPivR{i}", (fx, 0, -1.78), rot(y=spread), shR)
        add(f"FingerR{i}", (0.19, 0.3, 0.55), (0, 0, -0.27), skin, fp)
    tp = pivot("ThumbPivR", (-0.46, 0.05, -1.5), rot(y=-55), shR)
    add("ThumbR", (0.2, 0.3, 0.45), (0, 0, -0.2), skin, tp)

    # head on a neck pivot, tilted back to look up at the dream
    neck = pivot("Neck", (0, 0, 2.0), rot(x=look_up, z=-6), hip)
    head = add("Head", (1.22, 1.18, 1.18), (0, 0, 0.62), skin, neck, bevel=0.32)
    add("HairTop", (1.28, 1.24, 0.3), (0, -0.04, 1.12), hair, neck, bevel=0.12)
    add("HairBack", (1.28, 0.3, 0.6), (0, -0.5, 0.86), hair, neck, bevel=0.12)
    # simple face (front, +Y): eyes, tired brows, small mouth
    for x in (-0.24, 0.24):
        add("Eye", (0.13, 0.06, 0.2), (x, 0.6, 0.72), face, neck)
        add("Brow", (0.26, 0.06, 0.06), (x, 0.6, 0.9), face, neck)
    add("Mouth", (0.34, 0.06, 0.07), (0, 0.6, 0.38), face, neck)

    return root, parts

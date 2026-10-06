"""Rags to Riches thumbnail - step 1 composition blockout (boxes only).

Run: python blockout.py <out_dir>
Renders blockout_480.png and blockout_256x144.png with Workbench (flat colours).
"""
import math, sys, os
import bpy
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view

ARGS = sys.argv[1:]
PROJECT_ONLY = "--project" in ARGS
OUT = [a for a in ARGS if not a.startswith("--")][0] if ARGS else "."
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---------------------------------------------------------------- layout
# Shared with the final scene: every real model replaces the box at the same spot.
LAYOUT = {
    "camera":    dict(loc=(0.0, -0.5, 0.45), target=(5.0, 30.0, 8.5), lens=18),
    "character": dict(loc=(-1.55, 4.1, 0.0), yaw=-32, height=2.0),
    "yacht":     dict(loc=(24.0, 36.0, 19.5), size=(9.0, 34.0, 9.0), yaw=-64, roll=-4),
    "glow":      dict(loc=(28.0, 52.0, 23.0), radius=19.0),
    "pizzeria":  dict(loc=(3.5, 30.0, 0.0), size=(9.0, 7.0, 5.5), yaw=-10),
    "plaza":     dict(loc=(5.0, 22.0, 0.0), size=(22.0, 14.0, 0.15)),
    "shops":     [((13.0, 33.0, 0.0), (6.0, 6.0, 4.0)), ((-26.0, 44.0, 0.0), (7.0, 6.0, 3.0)),
                  ((19.0, 29.0, 0.0), (5.0, 5.0, 3.0)), ((-3.5, 36.0, 0.0), (5.0, 5.0, 3.5))],
    "supercar":  dict(loc=(40.0, 80.0, 0.0), size=(2.0, 4.5, 1.2)),
    "jet":       dict(loc=(-75.0, 160.0, 75.0), size=(14.0, 4.0, 2.5)),
    "clouds":    [(-75.0, 120.0, 42.0, 9.0), (-12.0, 140.0, 55.0, 7.0), (55.0, 120.0, 52.0, 10.0),
                  (48.0, 90.0, 14.0, 6.0)],
}

COLORS = {
    "char": (0.35, 0.45, 0.6, 1), "skin": (0.95, 0.8, 0.45, 1), "iron": (0.12, 0.12, 0.13, 1),
    "bill": (0.35, 0.75, 0.35, 1), "card": (0.8, 0.15, 0.15, 1),
    "yacht": (0.97, 0.97, 0.97, 1), "gold": (1.0, 0.72, 0.1, 1), "glow": (1.0, 0.85, 0.45, 1),
    "build": (0.55, 0.5, 0.48, 1), "pizza": (0.62, 0.38, 0.3, 1), "plaza": (0.45, 0.45, 0.45, 1),
    "ground": (0.38, 0.5, 0.33, 1), "cloud": (1, 1, 1, 1), "car": (0.95, 0.2, 0.1, 1),
    "jet": (0.85, 0.85, 0.9, 1),
}

def col(obj, c):
    obj.color = COLORS[c]
    return obj

def box(name, loc, size, c, rot=(0, 0, 0), origin_bottom=True):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    o.rotation_euler = [math.radians(a) for a in rot]
    x, y, z = loc
    o.location = (x, y, z + (size[2] / 2 if origin_bottom else 0))
    return col(o, c)

def sphere(name, loc, r, c, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.active_object
    o.name = name
    bpy.ops.object.shade_smooth()
    return col(o, c)

def cyl(name, p0, p1, r, c):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(p0 + p1) / 2)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return col(o, c)

def parent_all(objs, parent):
    for o in objs:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()

# ---------------------------------------------------------------- ground
box("Ground", (0, 60, -0.05), (400, 400, 0.1), "ground", origin_bottom=False)

# ---------------------------------------------------------------- character (R6, studs -> metres)
L = LAYOUT["character"]
s = L["height"] / 5.2          # 1 stud
root = bpy.data.objects.new("Character", None)
scn.collection.objects.link(root)
parts = []
# legs (2 studs), torso (2x2x1), arms (1x2x1), head ~1.2
parts.append(box("LegL", (-0.5 * s, 0, 0), (1 * s, 1 * s, 2 * s), "char"))
parts.append(box("LegR", (0.5 * s, 0, 0), (1 * s, 1 * s, 2 * s), "char"))
torso = box("Torso", (0, 0.08 * s, 2 * s), (2 * s, 1 * s, 2 * s), "char", rot=(-8, 0, 0))
parts.append(torso)
parts.append(box("ArmL", (-1.5 * s, 0.1 * s, 1.95 * s), (1 * s, 1 * s, 2 * s), "char", rot=(-4, 0, 3)))
parts.append(box("ArmR", (1.5 * s, 0.1 * s, 1.95 * s), (1 * s, 1 * s, 2 * s), "char", rot=(-4, 0, -3)))
head = sphere("Head", (0, -0.12 * s, 4.6 * s), 0.64 * s, "skin")
head.scale = (1.0, 1.0, 0.95)
head.rotation_euler = (math.radians(28), 0, 0)
parts.append(head)
parent_all(parts, root)
root.location = L["loc"]
root.rotation_euler = (0, 0, math.radians(L["yaw"]))

# ball and chain on left ankle, ball trailing behind (towards camera)
cx, cy, _ = L["loc"]
bpy.context.view_layer.update()
ankle = root.matrix_world @ Vector((-0.5 * s, 0, 0.25 * s))
ball_pos = Vector((cx - 0.62, cy + 0.2, 0.24))
cyl("Chain", ankle, ball_pos + Vector((0.15, 0.15, 0.05)), 0.045, "iron")
sphere("Ball", ball_pos, 0.24, "iron")

# bills + credit card debt at his feet
for i, (dx, dy, h) in enumerate([(0.55, -0.35, 0.18), (0.85, -0.05, 0.12), (0.4, 0.1, 0.1)]):
    box(f"Bills{i}", (cx + dx, cy + dy, 0), (0.45, 0.3, h), "bill", rot=(0, 0, 20 * i))
box("DebtCard", (cx + 0.95, cy - 0.55, 0.0), (0.55, 0.06, 0.36), "card", rot=(-12, 0, 35))

# ---------------------------------------------------------------- yacht in the sky
Y = LAYOUT["yacht"]
yroot = bpy.data.objects.new("Yacht", None)
scn.collection.objects.link(yroot)
w, l, h = Y["size"]
yp = []
hull = box("Hull", (0, 0, -h * 0.5), (w, l, h * 0.45), "yacht", origin_bottom=False)
yp.append(hull)
yp.append(box("Bow", (0, l * 0.55, -h * 0.4), (w * 0.7, l * 0.25, h * 0.3), "yacht", rot=(0, 0, 0), origin_bottom=False))
yp.append(box("Deck1", (0, -l * 0.08, 0), (w * 0.8, l * 0.55, h * 0.25), "yacht"))
yp.append(box("Deck2", (0, -l * 0.15, h * 0.25), (w * 0.6, l * 0.33, h * 0.22), "yacht"))
# gold chains wrapping the hull (rings around Y axis) + crossing straps
for k, t in enumerate((-0.32, 0.0, 0.3)):
    bpy.ops.mesh.primitive_torus_add(major_radius=w * 0.62, minor_radius=0.45,
                                     location=(0, l * t, -h * 0.25), rotation=(math.radians(90), 0, 0))
    o = bpy.context.active_object; o.name = f"ChainRing{k}"; o.scale = (1.0, 1.0, 1.0); col(o, "gold"); yp.append(o)
yp.append(cyl("ChainDiag", (w * 0.55, -l * 0.42, -h * 0.6), (w * 0.55, l * 0.42, h * 0.35), 0.45, "gold"))
# big padlock hanging from the side facing camera
yp.append(box("LockBody", (-w * 0.62, -l * 0.02, -h * 1.05), (1.4, 6.0, 5.0), "gold", origin_bottom=False))
bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.55, location=(-w * 0.62, -l * 0.02, -h * 0.62),
                                 rotation=(0, math.radians(90), 0))
o = bpy.context.active_object; o.name = "LockShackle"; col(o, "gold"); yp.append(o)
parent_all(yp, yroot)
yroot.location = Y["loc"]
yroot.rotation_euler = (0, math.radians(Y["roll"]), math.radians(Y["yaw"]))

# glow disc behind yacht (stand-in for the warm light)
G = LAYOUT["glow"]
glow = sphere("Glow", G["loc"], G["radius"], "glow")
glow.scale = (1, 0.15, 1)

# falling coins
yl = Vector(Y["loc"])
for i, (dx, dz) in enumerate([(-3, -9), (2, -12), (6, -7), (-1, -16), (4, -19)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=0.25, location=(yl.x + dx, yl.y - 4, yl.z + dz),
                                        rotation=(math.radians(70), math.radians(20 * i), 0))
    col(bpy.context.active_object, "gold").name = f"Coin{i}"

# ---------------------------------------------------------------- middle ground
P = LAYOUT["pizzeria"]
box("Pizzeria", P["loc"], P["size"], "pizza", rot=(0, 0, P["yaw"]))
PL = LAYOUT["plaza"]
box("Plaza", PL["loc"], PL["size"], "plaza")
for i, (loc, size) in enumerate(LAYOUT["shops"]):
    box(f"Shop{i}", loc, size, "build")

# ---------------------------------------------------------------- background
C = LAYOUT["supercar"]
box("Supercar", C["loc"], C["size"], "car", rot=(0, 0, 70))
J = LAYOUT["jet"]
box("Jet", J["loc"], J["size"], "jet", rot=(0, 8, -10), origin_bottom=False)
box("JetWing", J["loc"], (4.0, 12.0, 0.5), "jet", rot=(0, 8, -10), origin_bottom=False)
for i, (x, y, z, r) in enumerate(LAYOUT["clouds"]):
    for j, (ox, oz, rr) in enumerate([(0, 0, 1.0), (r * 0.9, -r * 0.2, 0.75), (-r * 0.9, -r * 0.25, 0.7)]):
        b = box(f"Cloud{i}_{j}", (x + ox, y, z + oz), (r * 1.6 * rr, r * 1.2 * rr, r * 1.1 * rr), "cloud",
                origin_bottom=False)

# ---------------------------------------------------------------- camera
CA = LAYOUT["camera"]
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = CA["lens"]
cam_data.sensor_width = 36
cam = bpy.data.objects.new("Camera", cam_data)
scn.collection.objects.link(cam)
cam.location = CA["loc"]
d = Vector(CA["target"]) - Vector(CA["loc"])
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
scn.camera = cam

# ---------------------------------------------------------------- report frame positions
bpy.context.view_layer.update()
scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
def report(name):
    o = bpy.data.objects[name]
    pts = []
    for ob in [o] + list(o.children_recursive):
        if ob.type == 'MESH':
            pts += [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    if not pts:
        pts = [o.matrix_world.translation]
    uv = [world_to_camera_view(scn, cam, p) for p in pts]
    xs = [u.x for u in uv]; ys = [u.y for u in uv]
    print(f"{name:12s} x {min(xs):.2f}-{max(xs):.2f}  y {min(ys):.2f}-{max(ys):.2f}")
for n in ["Character", "Ball", "DebtCard", "Yacht", "Glow", "Pizzeria", "Plaza", "Supercar", "Jet"]:
    report(n)

# ---------------------------------------------------------------- render (Cycles CPU, flat colour materials)
if PROJECT_ONLY:
    sys.exit(0)
mats = {}
for ob in scn.objects:
    if ob.type != 'MESH':
        continue
    key = tuple(round(v, 3) for v in ob.color)
    if key not in mats:
        m = bpy.data.materials.new(f"flat_{len(mats)}")
        m.use_nodes = True
        bsdf = m.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = ob.color
        bsdf.inputs["Roughness"].default_value = 0.9
        if ob.name == "Glow":
            bsdf.inputs["Emission Color"].default_value = ob.color
            bsdf.inputs["Emission Strength"].default_value = 1.5
        mats[key] = m
    ob.data.materials.clear()
    ob.data.materials.append(mats[key])

world = bpy.data.worlds.new("Sky"); scn.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.6, 0.95, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
scn.collection.objects.link(sun)
sun.data.energy = 3.0
sun.rotation_euler = Euler((math.radians(50), 0, math.radians(200)))

scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = 24
scn.cycles.use_denoising = True
scn.view_settings.view_transform = 'Standard'
scn.render.image_settings.file_format = 'PNG'

def render(w, h, fn):
    scn.render.resolution_x, scn.render.resolution_y = w, h
    scn.render.resolution_percentage = 100
    scn.render.filepath = os.path.join(OUT, fn)
    bpy.ops.render.render(write_still=True)

render(480, 270, "blockout_480.png")
render(256, 144, "blockout_256x144.png")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "blockout.blend"))

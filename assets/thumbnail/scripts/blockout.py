"""Rags to Riches thumbnail - composition blockout (boxes only, real-model sizes).

Run: python blockout.py <out_dir> [--project]
Renders blockout_960.png and blockout_256x144.png (Cycles CPU) and saves blockout.blend.
--project only prints where each element lands in the frame (0..1, safe area 0.08..0.92).
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

import layout as LY
import character
from sceneutil import (mat, mesh_box, mesh_sphere, mesh_cylinder, bar, empty, parent_keep,
                       rot, collection, world_bounds)

ARGS = sys.argv[1:]
PROJECT_ONLY = "--project" in ARGS
OUT = next((a for a in ARGS if not a.startswith("--")), ".")
CROP = next((tuple(map(float, a[7:].split(","))) for a in ARGS if a.startswith("--crop=")), None)
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.resolution_x, scn.render.resolution_y = 1920, 1080

# ------------------------------------------------------------------ camera
C = LY.CAMERA
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
scn.collection.objects.link(cam)
cam.data.lens, cam.data.sensor_width = C["lens"], C["sensor"]
cam.data.clip_end = 5000
cam.location = C["loc"]
cam.rotation_euler = (math.radians(90 + C["pitch"]), 0, math.radians(C["yaw"]))
scn.camera = cam
bpy.context.view_layer.update()
cam_fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
cam_right = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
cam_up = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))

# ------------------------------------------------------------------ ground
fg = collection("Foreground")
mg = collection("Middleground")
bg = collection("Background")
dream = collection("Dream")
mesh_box("Ground", (6000, 6000, 1), (0, 0, -0.5), mat("Grass", (0.32, 0.52, 0.28), rough=0.9), coll=bg)

# ------------------------------------------------------------------ yacht (blockout of Dream_Yacht)
Y = LY.YACHT
ymat = Matrix.Translation(Y["loc"]) @ rot(z=Y["yaw"], y=Y["bank"], x=Y["pitch"]) @ Matrix.Scale(Y["scale"], 4)
yroot = empty("Yacht", dream, ymat)
white = mat("YachtWhite", (0.95, 0.95, 0.97), rough=0.35)
navy = mat("YachtNavy", (0.12, 0.2, 0.42), rough=0.4)
wood = mat("YachtWood", (0.7, 0.45, 0.25), rough=0.6)
glass = mat("YachtGlass", (0.15, 0.25, 0.4), rough=0.15)

def ypart(o):
    o.matrix_world = yroot.matrix_world @ o.matrix_world
    parent_keep(o, yroot)
    return o

def hull_mesh(name):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    top = [(-5.6, -20), (-5.6, 8), (-3.4, 15), (0, 20), (3.4, 15), (5.6, 8), (5.6, -20)]
    bot = [(-3.6, -18.5), (-3.6, 6), (-2.0, 11), (0, 14), (2.0, 11), (3.6, 6), (3.6, -18.5)]
    vt = [bm.verts.new((x, y, 5.5)) for x, y in top]
    vb = [bm.verts.new((x, y, -0.5)) for x, y in bot]
    n = len(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bm.faces.new(list(reversed(vt)))
    bm.faces.new(vb)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); dream.objects.link(o)
    me.materials.append(white)
    return o

ypart(hull_mesh("Hull"))
ypart(mesh_box("BootStripe", (11.4, 27.0, 0.9), (0, -6.5, 1.6), navy, coll=dream))
ypart(mesh_box("Cabin", (8.6, 17.0, 3.6), (0, -4.5, 7.3), white, coll=dream))
ypart(mesh_box("CabinWindows", (8.8, 14.0, 1.1), (0, -4.0, 7.6), glass, coll=dream))
ypart(mesh_box("Flybridge", (7.0, 9.0, 2.2), (0, -7.0, 10.2), white, coll=dream))
ypart(mesh_box("FlyWindows", (7.2, 7.0, 0.8), (0, -6.0, 10.4), glass, coll=dream))
ypart(mesh_box("Roof", (9.6, 12.5, 0.45), (0, -7.5, 12.9), white, coll=dream))
for x in (-4.2, 4.2):
    for yy in (-12.5, -2.5):
        ypart(mesh_box("RoofPost", (0.35, 0.35, 1.6), (x, yy, 11.9), white, coll=dream))
ypart(mesh_box("Mast", (0.5, 0.5, 1.6), (0, -6.0, 13.9), white, coll=dream))
ypart(mesh_box("SwimPlatform", (9.6, 2.6, 0.5), (0, -21.2, 1.0), wood, coll=dream))
ypart(mesh_box("Deck", (10.4, 26.0, 0.2), (0, -6.0, 5.55), wood, coll=dream))

# chain loops hugging the hull + padlock (gold in the blockout)
gold = mat("ChainGold", (1.0, 0.68, 0.12), rough=0.3, metal=0.6)
chain_bars = []
for name, axis, v, pts in LY.CHAIN_LOOPS:
    cx_ = sum(a for a, _ in pts) / len(pts); cy_ = sum(b for _, b in pts) / len(pts)
    padded = []
    for a, b in pts:
        d = Vector((a - cx_, b - cy_)); d = d.normalized() * LY.CHAIN_PAD
        padded.append((a + d.x, b + d.y))
    for i in range(len(padded)):
        (a0, b0), (a1, b1) = padded[i], padded[(i + 1) % len(padded)]
        if axis == "y":
            pa, pb = Vector((a0, v, b0)), Vector((a1, v, b1))
        else:
            pa, pb = Vector((a0, b0, v)), Vector((a1, b1, v))
        chain_bars.append((pa, pb))
        ypart(bar(f"Chain{name}{i}", pa, pb, 1.1, gold, coll=dream))
P = LY.PADLOCK
ps = P["scale"]
lock = empty("Padlock", dream, yroot.matrix_world @ Matrix.Translation(P["local"]) @ rot(z=90))
orange = mat("PadlockBody", (0.95, 0.55, 0.12), rough=0.35, metal=0.3)
steel = mat("PadlockShackle", (0.55, 0.57, 0.62), rough=0.3, metal=0.8)
for nm, size, ctr, m_ in (("LockBody", (3.0, 1.2, 2.5), (0, 0, -1.6), orange),
                          ("LockShackleL", (0.45, 0.45, 1.6), (-0.95, 0, 0.0), steel),
                          ("LockShackleR", (0.45, 0.45, 1.6), (0.95, 0, 0.0), steel),
                          ("LockShackleT", (2.35, 0.45, 0.45), (0, 0, 0.85), steel)):
    o = mesh_box(nm, [s * ps for s in size], [c_ * ps for c_ in ctr], m_, bevel=0.15 * ps, coll=dream)
    o.matrix_world = lock.matrix_world @ o.matrix_world
    parent_keep(o, lock)
parent_keep(lock, yroot)

# glow card behind the yacht, facing the camera (radial falloff)
G = LY.GLOW
bpy.context.view_layer.update()
_yp = world_bounds([o for o in dream.objects if o.type == 'MESH'])
yc = sum(_yp, Vector()) / len(_yp)      # centre of the yacht + chains + padlock
to_y = (yc - cam.location).normalized()
gpos = yc + to_y * G["back"]
bpy.ops.mesh.primitive_plane_add(size=2 * G["radius"])
glow = bpy.context.active_object; glow.name = "Glow"
for c_ in glow.users_collection: c_.objects.unlink(glow)
dream.objects.link(glow)
glow.matrix_world = Matrix.Translation(gpos) @ (-to_y).to_track_quat('Z', 'Y').to_matrix().to_4x4()
gm = bpy.data.materials.new("GlowCard"); gm.use_nodes = True
nt = gm.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord"); grad = nt.nodes.new("ShaderNodeTexGradient")
grad.gradient_type = 'SPHERICAL'
mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / G["radius"],) * 3
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
ramp.color_ramp.elements[1].position = 0.9; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
ramp.color_ramp.interpolation = 'EASE'
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.42, 0.08, 1)
em.inputs["Strength"].default_value = 1.6
tr = nt.nodes.new("ShaderNodeBsdfTransparent")
mix = nt.nodes.new("ShaderNodeMixShader"); out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], grad.inputs["Vector"])
nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], mix.inputs["Fac"])
nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs["Surface"])
glow.data.materials.append(gm)
glow.visible_shadow = False

# falling coins (blockout discs; Maker_GoldCoin in the final)
for i, (dx, dz, tilt) in enumerate([(-14, -30, 60), (6, -40, 20), (20, -26, 75), (-4, -52, 40), (14, -60, 10)]):
    cpos = Vector(Y["loc"]) + cam_right * dx + Vector((0, 0, dz))
    o = mesh_cylinder(f"Coin{i}", 3.0, 0.7, material=gold, coll=dream)
    o.matrix_world = Matrix.Translation(cpos) @ rot(x=tilt, z=30 * i)

# ------------------------------------------------------------------ character
fc = collection("Character", fg)
shoulder_guess = Vector(LY.CHARACTER["loc"]) + Vector((0, 0, 3.8))
def to_cam(p):
    v = world_to_camera_view(scn, cam, Vector(p)); return Vector((v.x, v.y))
ang = math.radians(50)   # on-screen angle of the reaching arm (up and right, toward the dream)
reach = (cam_right * math.cos(ang) + cam_up * math.sin(ang) + cam_fwd * 0.5).normalized()
char_root, parts = character.build(LY.CHARACTER, fc, reach)

# ball and chain
iron = mat("Iron", (0.09, 0.09, 0.1), rough=0.45, metal=0.7)
B = LY.BALL
ball = mesh_sphere("Ball", B["radius"], (0, 0, 0), iron, coll=fg)
ball.location = Vector(B["loc"]) + Vector((0, 0, B["radius"]))
bpy.context.view_layer.update()
ankle = parts["LegL"].matrix_world @ Vector((0, 0, -0.55))
cuff = mesh_cylinder("AnkleCuff", 0.62, 0.3, material=iron, coll=fg)
cuff.matrix_world = parts["LegL"].matrix_world @ Matrix.Translation((0, 0, -0.55))
chain_end = ball.location + (ankle - ball.location).normalized() * B["radius"]
mid = (ankle + chain_end) / 2 + Vector((0, 0, -0.25))
mid.z = max(mid.z, 0.1)
bar("BallChain1", ankle, mid, 0.22, iron, coll=fg)
bar("BallChain2", mid, chain_end, 0.22, iron, coll=fg)

# pile of debt props + bills
pile_cols = {"Debt_CreditCard": (0.2, 0.42, 0.9), "Debt_OtherDebt": (0.45, 0.48, 0.58),
             "Debt_SchoolLoan": (0.2, 0.6, 0.3), "Debt_BankLoan": (0.38, 0.4, 0.5)}
for name, size, loc, yaw in LY.PILE:
    c_ = pile_cols.get(name, (0.35, 0.68, 0.32))
    size = [v * LY.PILE_SCALE for v in size]
    o = mesh_box(name, size, (0, 0, size[2] / 2), mat(name, c_), bevel=0.05, coll=fg)
    o.matrix_world = Matrix.Translation(loc) @ rot(z=yaw)

# ------------------------------------------------------------------ middle ground (dull)
PZ = LY.PIZZERIA
sx, sy, sz = [v * PZ["scale"] for v in PZ["size"]]
o = mesh_box("Pizzeria", (sx, sy, sz), (0, 0, sz / 2), mat("PizzeriaRed", (0.62, 0.2, 0.17)), coll=mg)
o.matrix_world = Matrix.Translation(PZ["loc"]) @ rot(z=PZ["yaw"])
PL = LY.PLAZA
o = mesh_cylinder("PlazaDisc", PL["radius"] * 1.8, 0.3, (0, 0, 0.15), mat("Plaza", (0.6, 0.58, 0.55)), coll=mg)
o.location = PL["loc"]
o = mesh_cylinder("Fountain", PL["radius"], 3.0, (0, 0, 1.5), mat("Stone", (0.7, 0.7, 0.72)), coll=mg)
o.location = PL["loc"]
trunk, leaves = mat("Trunk", (0.45, 0.28, 0.15)), mat("Leaves", (0.25, 0.55, 0.25))
for i, (x, y) in enumerate(LY.TREES):
    mesh_cylinder(f"Trunk{i}", 0.6, 8, (x, y, 4), trunk, coll=mg)
    mesh_sphere(f"Leaves{i}", 3.2, (x, y, 11), leaves, coll=mg)
pole = mat("Pole", (0.35, 0.38, 0.45))
for i, (x, y) in enumerate(LY.LAMPS):
    mesh_cylinder(f"Lamp{i}", 0.3, 7.5, (x, y, 3.75), pole, coll=mg)
    mesh_sphere(f"LampHead{i}", 0.6, (x, y, 7.5), mat("LampBulb", (1, 0.9, 0.7), emit=2.0), coll=mg)
for i, ((x, y), size) in enumerate(LY.SHOPS):
    mesh_box(f"Shop{i}", size, (x, y, size[2] / 2), mat("Shop", (0.62, 0.55, 0.5)), coll=mg)

# ------------------------------------------------------------------ background
SC = LY.SUPERCAR
o = mesh_box("Supercar", (5.4, 12.2, 3.3), (0, 0, 1.65), mat("CarRed", (0.85, 0.12, 0.1)), coll=bg)
o.matrix_world = Matrix.Translation(SC["loc"]) @ rot(z=SC["yaw"])
J = LY.JET
jm = mat("JetWhite", (0.92, 0.92, 0.95))
jet = empty("Jet", bg, Matrix.Translation(J["loc"]) @ rot(z=J["yaw"], y=J["roll"]))
for nm, size, ctr in (("Fuselage", (4.0, 30.0, 4.0), (0, 0, 0)), ("Wing", (28.0, 6.0, 0.6), (0, -2, -0.8)),
                      ("Tail", (0.6, 4.0, 7.0), (0, -13.5, 3.5)), ("Stab", (10, 3, 0.5), (0, -14, 1))):
    o = mesh_box(nm, size, ctr, jm, coll=bg); o.matrix_world = jet.matrix_world @ o.matrix_world
cloud = mat("Cloud", (1, 1, 1), rough=1.0)
for i, (x, y, z, r) in enumerate(LY.CLOUDS):
    for j, (ox, oz, k) in enumerate(((0, 0, 1.0), (0.95, -0.25, 0.72), (-0.95, -0.3, 0.68), (0.35, 0.45, 0.6))):
        mesh_box(f"Cloud{i}_{j}", (r * 1.7 * k, r * 1.1 * k, r * 1.0 * k), (x + ox * r, y, z + oz * r),
                 cloud, bevel=r * 0.18 * k, coll=bg)

# ------------------------------------------------------------------ frame report
bpy.context.view_layer.update()
def frame_box(objs):
    pts = world_bounds(objs)
    uv = [world_to_camera_view(scn, cam, p) for p in pts]
    uv = [u for u in uv if u.z > 0]
    return (min(u.x for u in uv), max(u.x for u in uv), min(u.y for u in uv), max(u.y for u in uv))
def coll_objs(c): return [o for o in c.all_objects if o.type == 'MESH']
groups = {
    "character": coll_objs(fc),
    "raised hand": [parts["PalmR"]] + [o for o in fc.all_objects if o.name.startswith(("FingerR", "ThumbR"))],
    "head": [o for o in fc.all_objects if o.name.startswith(("Head", "Hair"))],
    "ball+chain": [ball] + [o for o in fg.objects if o.name.startswith("BallChain")],
    "credit card": [bpy.data.objects["Debt_CreditCard"]],
    "debt pile": [o for o in fg.objects if o.name.startswith(("Debt_", "Bills"))],
    "yacht+chains": [o for o in dream.objects if o.type == 'MESH' and o.name != "Glow" and not o.name.startswith("Coin")],
    "padlock": [o for o in dream.objects if o.name.startswith("Lock")],
    "glow": [glow],
    "pizzeria": [bpy.data.objects["Pizzeria"]],
    "middle ground": coll_objs(mg),
    "supercar": [bpy.data.objects["Supercar"]],
    "jet": [o for o in bg.objects if o.name.startswith(("Fuselage", "Wing", "Tail", "Stab"))],
}
print("FRAME (x0 x1 y0 y1), safe area %.2f..%.2f" % (LY.SAFE, 1 - LY.SAFE))
for k, objs in groups.items():
    b = frame_box(objs)
    flag = "" if (b[0] >= LY.SAFE and b[1] <= 1 - LY.SAFE and b[2] >= LY.SAFE and b[3] <= 1 - LY.SAFE) else "  <-- outside safe area"
    print(f"  {k:14s} x {b[0]:.2f}-{b[1]:.2f}  y {b[2]:.2f}-{b[3]:.2f}{flag}")
horizon = world_to_camera_view(scn, cam, cam.location + Vector((math.sin(-math.radians(C['yaw'])), math.cos(math.radians(C['yaw'])), 0)) * 4000)
print(f"  horizon y {horizon.y:.2f}")
if PROJECT_ONLY:
    sys.exit(0)

# ------------------------------------------------------------------ lighting
world = bpy.data.worlds.new("Sky"); scn.world = world; world.use_nodes = True
wn = world.node_tree; bgn = wn.nodes["Background"]
wtc = wn.nodes.new("ShaderNodeTexCoord"); sep = wn.nodes.new("ShaderNodeSeparateXYZ")
wr = wn.nodes.new("ShaderNodeValToRGB")
wr.color_ramp.elements[0].position = 0.0; wr.color_ramp.elements[0].color = (0.55, 0.75, 1.0, 1)
wr.color_ramp.elements[1].position = 0.6; wr.color_ramp.elements[1].color = (0.12, 0.35, 0.85, 1)
wn.links.new(wtc.outputs["Generated"], sep.inputs[0]); wn.links.new(sep.outputs["Z"], wr.inputs["Fac"])
wn.links.new(wr.outputs["Color"], bgn.inputs["Color"]); bgn.inputs["Strength"].default_value = 1.0

sun = bpy.data.objects.new("CoolSun", bpy.data.lights.new("CoolSun", 'SUN')); scn.collection.objects.link(sun)
sun.data.energy = 2.2; sun.data.color = (0.85, 0.9, 1.0); sun.data.angle = math.radians(3)
sun.rotation_euler = (math.radians(55), 0, math.radians(150))

def area(name, pos, target, energy, color, size, receivers=None):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'AREA')); scn.collection.objects.link(l)
    l.data.energy, l.data.color, l.data.size = energy, color, size
    l.location = pos
    l.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    if receivers is not None:
        l.light_linking.receiver_collection = receivers
    return l
# warm key on the yacht from below-front
area("YachtWarmKey", Vector(Y["loc"]) + Vector((-40, -70, -45)), Y["loc"], 6e5, (1.0, 0.72, 0.38), 60)
# rim light on the character's head and shoulders, from the dream's side, character only
char_head = parts["Head"].matrix_world.translation
area("CharRim", char_head + Vector((4.5, 7.0, 4.0)), char_head, 1400, (1.0, 0.7, 0.35), 3.0, receivers=fc)

scn.render.engine = 'CYCLES'; scn.cycles.device = 'CPU'
scn.cycles.samples = 48; scn.cycles.use_denoising = True
scn.view_settings.view_transform = 'Standard'
scn.render.image_settings.file_format = 'PNG'

def render(w, h, fn):
    scn.render.resolution_x, scn.render.resolution_y = w, h
    scn.render.filepath = os.path.join(OUT, fn)
    bpy.ops.render.render(write_still=True)

if CROP:
    scn.render.use_border = True; scn.render.use_crop_to_border = True
    scn.render.border_min_x, scn.render.border_max_x, scn.render.border_min_y, scn.render.border_max_y = CROP
    render(1920, 1080, "crop.png"); sys.exit(0)
render(960, 540, "blockout_960.png")
render(256, 144, "blockout_256x144.png")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "blockout.blend"))

"""Rags to Riches thumbnail - final scene: real game models, the player's avatar, the two numbers.

Run (Blender as a Python module, `pip install bpy`):
    git archive origin/claude/rags-to-riches-visual-overhaul-dey2rr world_overhaul | tar -x -C /tmp/wo
    python build_thumbnail.py --wo /tmp/wo/world_overhaul --out <dir> [--quick] [--no-render]

Writes <dir>/thumbnail.blend (everything packed) and EXR passes for finish.py:
    main_beauty.exr  main_matte.exr  main_depth.exr  main_near.exr
    iconA_beauty.exr iconA_matte.exr iconA_depth.exr   (his head in the corner)
    iconB_beauty.exr iconB_matte.exr iconB_depth.exr   (the dream alone, centred)
The title of the text version is drawn flat by finish.py.
"""
import argparse
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
import bmesh
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

import layout as LY
import avatar as AV
from models import (Library, set_material, tile_chain, convex_hull_2d, offset_polygon, simplify_polygon)

ap = argparse.ArgumentParser()
ap.add_argument("--wo", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--quick", action="store_true")
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--only", default="")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
A = ap.parse_args(argv)
os.makedirs(A.out, exist_ok=True)
ASSETS = os.path.normpath(os.path.join(HERE, ".."))
AVATAR_OBJ = os.path.join(ASSETS, "thumbnail", "avatar.obj")
FONT = os.path.join(HERE, "fonts", "Fredoka-Bold.ttf")
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
lib = Library(A.wo)
import kit                                                      # the game's model kit (world_overhaul)
KM = kit.Materials()
PAL = kit.COLORS


def srgb(name):
    return kit.lin(PAL[name]["rgb"])


def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or scn.collection).children.link(c)
    return c


C_CHAR, C_DREAM, C_NUM = coll("Character"), coll("Dream"), coll("Numbers")
C_FG, C_MG, C_BG = coll("Foreground"), coll("Middleground"), coll("Background")
C_SKY, C_NEAR, C_GROUND = coll("SkyGlow"), coll("NearCoins"), coll("Ground")
C_COINS = coll("Coins")
C_CLOUDS = coll("Clouds")
C_LIGHTS = coll("Lights")


def rot(x=0.0, y=0.0, z=0.0):
    return (Matrix.Rotation(math.radians(z), 4, 'Z') @ Matrix.Rotation(math.radians(y), 4, 'Y')
            @ Matrix.Rotation(math.radians(x), 4, 'X'))


def kit_build(model, collection):
    return model.build(collection, KM)


def bounds(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        if o.type in ('MESH', 'FONT', 'CURVE'):
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            pts += [ev.matrix_world @ v.co for v in me.vertices]
            ev.to_mesh_clear()
    return pts


# ====================================================================== camera
def make_camera(name, C):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    scn.collection.objects.link(cam)
    cam.data.lens, cam.data.sensor_width = C["lens"], C["sensor"]
    cam.data.clip_start, cam.data.clip_end = 0.05, 8000
    cam.matrix_world = (Matrix.Translation(C["loc"]) @ Matrix.Rotation(math.radians(C["yaw"]), 4, 'Z')
                        @ Matrix.Rotation(math.radians(90 + C["pitch"]), 4, 'X')
                        @ Matrix.Rotation(math.radians(C.get("roll", 0.0)), 4, 'Z'))
    return cam


cam = make_camera("Camera", LY.F_CAMERA)
scn.camera = cam
scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
bpy.context.view_layer.update()
CR = cam.matrix_world.to_3x3()
cam_right, cam_up, cam_fwd = CR @ Vector((1, 0, 0)), CR @ Vector((0, 1, 0)), CR @ Vector((0, 0, -1))
ground_side = Vector((cam_right.x, cam_right.y, 0)).normalized()        # screen right, on the ground


def screen(p, c=None):
    return world_to_camera_view(scn, c or cam, Vector(p))


def ray(sx, sy, d, c=None):
    """World point on the camera ray through screen point (sx, sy), at camera depth d."""
    c = c or cam
    tx = (c.data.sensor_width / 2) / c.data.lens
    ty = tx * scn.render.resolution_y / scn.render.resolution_x
    v = Vector(((sx - 0.5) * 2 * tx, (sy - 0.5) * 2 * ty, -1.0))
    return c.matrix_world @ (v * d)


def face_camera(pos, tilt=0.0, c=None):
    """Rotation whose +Z looks at the camera and +Y is the camera's up (text reads upright)."""
    c = c or cam
    up = c.matrix_world.to_3x3() @ Vector((0, 1, 0))
    z = (c.matrix_world.translation - Vector(pos)).normalized()
    x = up.cross(z).normalized()
    y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_4x4() @ Matrix.Rotation(math.radians(tilt), 4, 'Z')


def depth_of(p, c=None):
    c = c or cam
    return -(c.matrix_world.inverted() @ Vector(p)).z


def frame_h(p, c=None):
    """Frame height in studs at the depth of point p."""
    c = c or cam
    return 2 * depth_of(p, c) * (c.data.sensor_width / 2 / c.data.lens) * scn.render.resolution_y / scn.render.resolution_x


def on_ground(sx, sy, h=0.0, c=None):
    """Where the camera ray through screen point (sx, sy) meets the plane z = h."""
    c = c or cam
    o = c.matrix_world.translation
    d = ray(sx, sy, 1.0, c) - o
    if d.z >= 0:
        raise ValueError(f"screen point {(sx, sy)} is above the horizon")
    return o + d * ((h - o.z) / d.z)


def ground_at(sx, dist, c=None):
    """Point on the ground in screen column sx, `dist` studs from the camera (horizontally)."""
    c = c or cam
    o = c.matrix_world.translation
    g_ = on_ground(sx, 0.02, 0.0, c)
    d_ = Vector((g_.x - o.x, g_.y - o.y, 0)).normalized()
    return Vector((o.x, o.y, 0)) + d_ * dist


def facing_camera_yaw(p, c=None):
    """Yaw (deg) that turns a model's front (+Y) toward the camera."""
    c = c or cam
    v = c.matrix_world.translation - Vector(p)
    return math.degrees(math.atan2(-v.x, v.y))


def frame_box(objs, c=None):
    """Screen bounds (x0, x1, y0, y1) of objects, as fractions of the frame."""
    uv = [screen(p, c) for p in bounds(objs)]
    uv = [u for u in uv if u.z > 0]
    return (min(u.x for u in uv), max(u.x for u in uv), min(u.y for u in uv), max(u.y for u in uv))


def flat_material(name, rgb255):
    """Unlit flat colour (emission only): reads the same everywhere on the object."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.lin(rgb255)
    em.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def text_obj(name, body, size, colour, collection, extrude=0.11, bevel=0.035, emit=0.35, align=('CENTER', 'CENTER')):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    cu.size = size
    cu.align_x, cu.align_y = align
    cu.extrude = size * extrude
    cu.bevel_depth = size * bevel
    cu.bevel_resolution = 3
    cu.space_character = 1.04
    o = bpy.data.objects.new(name, cu)
    collection.objects.link(o)
    m = bpy.data.materials.new(name + "_mat")
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = colour
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Emission Color"].default_value = colour
    b.inputs["Emission Strength"].default_value = emit
    cu.materials.append(m)
    return o


def local_box(o):
    """Object-space bounds (x0, x1, y0, y1) of a text object's glyphs."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    ev.to_mesh_clear()
    return min(xs), max(xs), min(ys), max(ys)


_probe = text_obj("_capprobe", "0", 1.0, (1, 1, 1, 1), scn.collection, bevel=0.0)
_b = local_box(_probe)
CAP = _b[3] - _b[2]                    # height of a digit (cap height) at size 1
bpy.data.objects.remove(_probe)


def size_for_cap(cap_frac, p):
    """Font size whose digits are cap_frac of the frame height at point p."""
    return cap_frac * frame_h(p) / CAP


# ====================================================================== ground + middle ground
g = lib.place("ground", "City_Ground", C_GROUND, Matrix.Diagonal((16, 16, 1, 1)))
gp = bounds(g)
top = max(p.z for p in gp)
for o in g:
    o.matrix_world = Matrix.Translation((0, 1500, -top)) @ o.matrix_world

mg_objs = []
P = LY.F_PIZZERIA
pz = ground_at(P["screen_x"], P["distance"])
mg_objs += lib.place("buildings", "Workplace_Building_PIZZERIA", C_MG,
                     Matrix.Translation(pz) @ rot(z=facing_camera_yaw(pz) + P["turn"]) @ Matrix.Scale(P["scale"], 4))
PL = LY.F_PLAZA
plz = ground_at(PL["screen_x"], PL["distance"])
mg_objs += lib.place("ground", "Plaza_Disc", C_MG, Matrix.Translation(plz) @ Matrix.Scale(PL["scale"], 4))
mg_objs += lib.place("decoration", "Plaza_Fountain", C_MG,
                     Matrix.Translation(plz + Vector((0, 0, 0.1))) @ Matrix.Scale(PL["scale"] * 1.4, 4))
for sx, dist, sc in LY.F_TREES:
    mg_objs += lib.place("nature", "Tree", C_MG, Matrix.Translation(ground_at(sx, dist))
                         @ rot(z=random.uniform(0, 360)) @ Matrix.Scale(sc, 4))
for sx, dist in LY.F_LAMPS:
    lp = ground_at(sx, dist)
    mg_objs += lib.place("decoration", "Workplace_LampPost", C_MG, Matrix.Translation(lp) @ rot(z=facing_camera_yaw(lp)))
for name, (x, y), yaw in LY.F_SHOPS:
    mg_objs += lib.place("buildings", name, C_MG, Matrix.Translation((x, y, 0)) @ rot(z=180 + yaw))
set_material(mg_objs, "WO_Palette", lib.distant_palette(sat=0.9, value=1.0, mix=0.17))

# background dreams
S = LY.F_SUPERCAR
car_p = ground_at(S["screen_x"], S["distance"])
lib.place("vehicles", "Supercar", C_BG, Matrix.Translation(car_p) @ rot(z=S["yaw"]))
J = LY.F_JET
lib.place("vehicles", "PrivateJet", C_BG, Matrix.Translation(J["loc"]) @ rot(z=J["yaw"], y=J["roll"]))
cloud_mat = bpy.data.materials.new("CloudWhite")
_cb = cloud_mat.node_tree.nodes["Principled BSDF"]
_cb.inputs["Base Color"].default_value = srgb("WHITE")
_cb.inputs["Roughness"].default_value = 0.9
_cb.inputs["Emission Color"].default_value = srgb("WHITE")
_cb.inputs["Emission Strength"].default_value = 0.55
# chunky clouds (the game has no cloud model): rounded kit spheres in the palette's WHITE
for i, (x, y, z, r) in enumerate(LY.F_CLOUDS):
    m = kit.Model(f"Cloud{i}")
    for ox, oy, k in ((0, 0, 1.0), (0.95, -0.22, 0.74), (-0.95, -0.28, 0.7), (0.4, 0.42, 0.62), (-0.5, 0.3, 0.55)):
        m.sphere(r * k, (ox * r, oy * r, 0), "WHITE", scale=(1.25, 0.95, 0.9), segs=20, rings=12)
    for o in kit_build(m, C_CLOUDS):
        o.matrix_world = Matrix.Translation((x, y, z)) @ o.matrix_world
        o.data.materials.clear()
        o.data.materials.append(cloud_mat)

# ====================================================================== the dream: yacht, chains, padlock, tag
Y = LY.F_YACHT
ymat = Matrix.Translation(Y["loc"]) @ rot(z=Y["yaw"], y=Y["bank"], x=Y["pitch"]) @ Matrix.Scale(Y["scale"], 4)
yacht = lib.place("vehicles", "Yacht", C_DREAM, ymat)
yv = [v.co.copy() for v in lib.template("vehicles", "Yacht")[0].data.vertices]   # yacht-local
seg_mesh = lib.template("props", "Dream_ChainSegment")[0].data
CH = LY.F_CHAINS
link = CH["link_scale"] * Y["scale"]
loops = {}
for k, y0 in enumerate(CH["cross"]):
    sec = [(v.x, v.z) for v in yv if abs(v.y - y0) < 1.6 and v.z < CH["clip_top"]]
    hull = simplify_polygon(convex_hull_2d(sec), 0.9)
    poly = offset_polygon(hull, CH["pad"] + 0.65 * CH["link_scale"])
    loops[f"X{k}"] = [Vector((p.x, y0, p.y)) for p in poly]
for k, z0 in enumerate(CH["along"]):
    sec = [(v.x, v.y) for v in yv if abs(v.z - z0) < 1.2]
    hull = simplify_polygon(convex_hull_2d(sec), 1.2)
    poly = offset_polygon(hull, CH["pad"] + 0.65 * CH["link_scale"])
    loops[f"Z{k}"] = [Vector((p.x, p.y, z0)) for p in poly]
chain_objs = []
for name, pts in loops.items():
    wpts = [ymat @ p for p in pts]
    centre = sum(wpts, Vector()) / len(wpts)
    chain_objs += tile_chain(seg_mesh, wpts, True, C_DREAM, link, lambda p, t, c=centre: p - c, name="Chain" + name)
chain_mat = bpy.data.materials.new("ChainGold")
b = chain_mat.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = srgb("GOLD")
b.inputs["Metallic"].default_value = 0.85
b.inputs["Roughness"].default_value = 0.28
seg_mesh.materials.clear()
seg_mesh.materials.append(chain_mat)

# padlock where the lengthwise loop passes the middle of the camera side, hanging straight down
zl = loops["Z0"]
mid_y = sum(CH["cross"]) / 2
side_pts = [p for p in zl if p.x > 0]
anchor_local = Vector((max(p.x for p in side_pts), mid_y, zl[0].z))
anchor = ymat @ anchor_local
PD = LY.F_PADLOCK
ps = PD["scale"] * Y["scale"]
to_cam_flat = cam.matrix_world.translation - anchor
to_cam_flat.z = 0
to_cam_flat.normalize()
lx = to_cam_flat.cross(Vector((0, 0, 1))).normalized()             # padlock front (+Y) faces the camera
lock_rot = Matrix((lx, to_cam_flat, Vector((0, 0, 1)))).transposed().to_4x4()
lock_mat = Matrix.Translation(anchor - Vector((0, 0, 2.15 * ps))) @ lock_rot @ Matrix.Scale(ps, 4)
padlock = lib.place("props", "Dream_Padlock", C_DREAM, lock_mat)
lock_bottom = lock_mat @ Vector((0, 0, -1.3))

# price tag: rounded gold tag (palette GOLD) on a string from the padlock, "$2,000,000" in INK
T = LY.F_TAG
tag_centre = ray(T["screen"][0], T["screen"][1], depth_of(lock_bottom))
fh = frame_h(tag_centre)
tw = T["width"] * fh * scn.render.resolution_x / scn.render.resolution_y
th = tw * T["aspect"]
td = th * 0.16
tag_frame = Matrix.Translation(tag_centre) @ face_camera(tag_centre, T["swing"])


def tag_mesh(name, w, h, d):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    n = h * 0.42
    outline = [(-w / 2, 0), (-w / 2 + n, h / 2), (w / 2, h / 2), (w / 2, -h / 2), (-w / 2 + n, -h / 2)]
    vb = [bm.verts.new((x, y, -d / 2)) for x, y in outline]
    vf = [bm.verts.new((x, y, d / 2)) for x, y in outline]
    bm.faces.new(vf)
    bm.faces.new(list(reversed(vb)))
    for i in range(len(outline)):
        j = (i + 1) % len(outline)
        bm.faces.new((vb[i], vb[j], vf[j], vf[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(d * 0.45, h * 0.08), segments=3, affect='EDGES',
                    clamp_overlap=True)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            l[uv].uv = PAL["GOLD"]["uv"]
    bm.to_mesh(me)
    bm.free()
    return me


tag = bpy.data.objects.new("PriceTag", tag_mesh("PriceTag", tw, th, td))
C_DREAM.objects.link(tag)
tag.data.materials.append(lib.palette())
tag.matrix_world = tag_frame
hole_local = Vector((-tw / 2 + th * 0.3, 0, 0))
eyelet = kit.Model("PriceTagEyelet")
eyelet.torus(th * 0.11, th * 0.035, (0, 0, 0), "INK", axis="Y")   # ring lies flat on the tag, facing the camera
for o in kit_build(eyelet, C_DREAM):
    o.matrix_world = tag_frame @ Matrix.Translation(hole_local + Vector((0, 0, td * 0.5))) @ o.matrix_world
hole = tag_frame @ hole_local
# string: a thin rod from the padlock's bottom to the eyelet
sm = kit.Model("PriceTagString")
sm.stick((0, 0, 0), (0, 1, 0), 0.5, "INK")
for o in kit_build(sm, C_DREAM):
    d = hole - lock_bottom
    o.matrix_world = (Matrix.Translation(lock_bottom) @ Vector((0, 0, 1)).rotation_difference(d.normalized())
                      .to_matrix().to_4x4() @ Matrix.Diagonal((td * 0.22, td * 0.22, d.length, 1)))
tag_size = size_for_cap(T["cap"], tag_centre)
tag_text = text_obj("PriceTagText", T["text"], tag_size, srgb("INK"), C_DREAM, extrude=0.05, bevel=0.015, emit=0.0)
tag_text.data.materials[0] = flat_material("PriceTagDigits", T["colour"])
x0, x1, y0, y1 = local_box(tag_text)
room = tw - th * 0.55                     # right of the hole
if x1 - x0 > room * 0.9:                  # never wider than the tag
    tag_text.data.size *= room * 0.9 / (x1 - x0)
    print("price tag text shrunk to fit:", round(room * 0.9 / (x1 - x0), 2))
    x0, x1, y0, y1 = local_box(tag_text)
tag_text.matrix_world = tag_frame @ Matrix.Translation((th * 0.275 - (x0 + x1) / 2, -(y0 + y1) / 2,
                                                         td * 0.5 + tag_text.data.extrude + th * 0.01))

# glow card behind the dream + light rays
bpy.context.view_layer.update()
dpts = bounds([o for o in C_DREAM.objects if o.type == 'MESH'])
dc = sum(dpts, Vector()) / len(dpts)
GL = LY.F_GLOW
to_d = (dc - cam.matrix_world.translation).normalized()
gpos = dc + to_d * GL["back"]


def radial_emission(name, colour, strength, radius, falloff_pos, alpha_peak=1.0):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / radius,) * 3
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = 'SPHERICAL'
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.interpolation = 'EASE'
    rp.color_ramp.elements[0].position, rp.color_ramp.elements[0].color = 0.0, (0, 0, 0, 1)
    rp.color_ramp.elements[1].position, rp.color_ramp.elements[1].color = falloff_pos, (alpha_peak,) * 3 + (1,)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = colour
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    L = nt.links.new
    L(tc.outputs["Object"], mp.inputs["Vector"]); L(mp.outputs["Vector"], gr.inputs["Vector"])
    L(gr.outputs["Fac"], rp.inputs["Fac"]); L(rp.outputs["Color"], mx.inputs["Fac"])
    L(tr.outputs[0], mx.inputs[1]); L(em.outputs[0], mx.inputs[2]); L(mx.outputs[0], out.inputs["Surface"])
    return m


face = (-to_d).to_track_quat('Z', 'Y').to_matrix().to_4x4()
gme = bpy.data.meshes.new("Glow")
R0 = GL["radius"]
gme.from_pydata([(-R0, -R0, 0), (R0, -R0, 0), (R0, R0, 0), (-R0, R0, 0)], [], [(0, 1, 2, 3)])
glow = bpy.data.objects.new("Glow", gme)
C_SKY.objects.link(glow)
glow.matrix_world = Matrix.Translation(gpos) @ face
gme.materials.append(radial_emission("GlowCard", (1.0, 0.46, 0.07, 1), 1.9, R0, 0.95))
# rays: thin wedges fanning out of the glow (in front of the glow card, behind the dream)
rme = bpy.data.meshes.new("LightRays")
bm = bmesh.new()
n = GL["rays"]
for i in range(n):
    a = 2 * math.pi * (i + random.uniform(-0.3, 0.3)) / n
    w = math.radians(random.uniform(1.6, 3.4))
    L = R0 * random.uniform(1.15, 1.75)
    c0 = bm.verts.new((0, 0, 0))
    c1 = bm.verts.new((math.cos(a - w) * L, math.sin(a - w) * L, 0))
    c2 = bm.verts.new((math.cos(a + w) * L, math.sin(a + w) * L, 0))
    bm.faces.new((c0, c1, c2))
bm.to_mesh(rme)
bm.free()
rays = bpy.data.objects.new("LightRays", rme)
C_SKY.objects.link(rays)
rays.matrix_world = Matrix.Translation(gpos - to_d * 8) @ face
rme.materials.append(radial_emission("Rays", (1.0, 0.72, 0.32, 1), 2.0, R0 * 1.75, 1.0, alpha_peak=0.22))
for o in (glow, rays):
    o.visible_shadow = False
    o.visible_diffuse = False
    o.visible_glossy = False

# falling coins: the real Gold Coin without its display stand
coin_me = lib.mesh_without_part("props", "Maker_GoldCoin", "GoldCoin_Falling",
                                drop=lambda comp: max(v.co.z for v in comp) < 0.45)
coin_me.materials.clear()
coin_me.materials.append(lib.palette())
for i, (sx, sy, d, s) in enumerate(LY.F_COINS):
    o = bpy.data.objects.new(f"Coin{i:02d}", coin_me)
    C_COINS.objects.link(o)
    o.matrix_world = (Matrix.Translation(ray(sx, sy, d)) @ rot(x=random.uniform(-70, 70), y=random.uniform(-40, 40),
                      z=random.uniform(0, 360)) @ Matrix.Scale(s, 4))
for i, (sx, sy, d, s, tilt) in enumerate(LY.F_NEAR):
    o = bpy.data.objects.new(f"NearCoin{i}", coin_me)
    C_NEAR.objects.link(o)
    p = ray(sx, sy, d)
    o.matrix_world = Matrix.Translation(p) @ face_camera(p) @ rot(x=90 + tilt, z=20 * i) @ Matrix.Scale(s, 4)

# ====================================================================== the player
AVL = LY.F_AVATAR
parts, front = AV.import_avatar(AVATAR_OBJ, C_CHAR)
rig = AV.Rig(parts, C_CHAR)
loc = Vector(AVL["loc"])
to_cam = cam.matrix_world.translation - loc
to_cam.z = 0
to_cam.normalize()
t = math.radians(AVL["body_turn"])
rig.place(loc, to_cam * math.cos(t) + ground_side * math.sin(t))
rig.rot("Waist", *AVL["waist"])
hc0 = rig.centre("Head")
_d2h = screen(dc) - screen(hc0)
_ah = max(math.atan2(_d2h.y * 9, _d2h.x * 16), math.radians(AVL["look_min_up"]))
rig.aim_head(cam_right * math.cos(_ah) + cam_up * math.sin(_ah) - cam_fwd * AVL["face_cam"])
rig.rot("RightHip", 0, -5, 0)
rig.rot("LeftHip", 5, 6, 0)
# reaching arm (his left, screen right): toward the dream on screen, at least reach_min_angle up
S0 = rig.world("LeftShoulder")
d2 = screen(dc) - screen(S0)
ang = math.atan2(d2.y * 9, d2.x * 16)
ang = max(ang, math.radians(AVL["reach_min_angle"]))
reach = (cam_right * math.cos(ang) + cam_up * math.sin(ang) + cam_fwd * AVL["reach_depth"]).normalized()
L = (rig.rest["LeftElbow"] - rig.rest["LeftShoulder"]).length + (rig.rest["LeftWrist"] - rig.rest["LeftElbow"]).length
rig.ik_arm("Left", S0 + reach * L * 0.96, pole=Vector((0, 0, -1)) - cam_fwd * 0.4)
rig.aim_part("LeftWrist", "LeftHand", rig.world("LeftWrist") + reach * 3)
# other hand on his head (disbelief)
hair = parts["Hair"]
hp = [hair.matrix_world @ v.co for v in hair.data.vertices]
nm = rig.j["Neck"].matrix_world.to_3x3()
his_right, his_up, his_front = nm @ Vector((1, 0, 0)), nm @ Vector((0, 0, 1)), nm @ Vector((0, 1, 0))
hc = sum(hp, Vector()) / len(hp)
crown = max(hp, key=lambda p: (p - hc).dot(his_up))
on_head = crown + his_right * 0.3 - his_front * 0.15
rig.ik_arm("Right", on_head + his_right * 0.75 + his_up * 0.05, pole=his_right + his_up * 0.9 - his_front * 0.4)
rig.aim_part("RightWrist", "RightHand", on_head - his_right * 0.4)
bpy.context.view_layer.update()

# ball and chain on his right ankle (screen left)
BL = LY.F_BALL
ankle = rig.world("RightAnkle")
ball_c = ground_at(BL["screen_x"], BL["distance"])
ball_c.z = BL["radius"]
bm_ = kit.Model("IronBall")
bm_.sphere(BL["radius"], (0, 0, 0), "CHARCOAL", segs=28, rings=16)
ball_objs = kit_build(bm_, C_FG)
face_dir = math.degrees(math.atan2(-(ankle - ball_c).x, (ankle - ball_c).y))
for o in ball_objs:
    o.matrix_world = Matrix.Translation(ball_c) @ rot(z=face_dir) @ o.matrix_world
cuff = kit.Model("AnkleCuff")
cuff.torus(0.47, 0.15, (0, 0, 0), "CHARCOAL", axis="Y")
leg_axis = (rig.world("RightKnee") - rig.world("RightAnkle")).normalized()
for o in kit_build(cuff, C_FG):
    o.matrix_world = (Matrix.Translation(ankle + leg_axis * 0.05) @ Vector((0, 0, 1)).rotation_difference(leg_axis)
                      .to_matrix().to_4x4() @ o.matrix_world)
to_ankle = Vector(((ankle - ball_c).x, (ankle - ball_c).y, 0)).normalized()
ring = ball_c + to_ankle * (BL["radius"] * 0.92)            # the chain ends on the ball's side
ring.z = BL["radius"] * 0.75
# slack: the chain drapes on the ground in an arc toward the camera, so it shows
mid1 = ankle.lerp(ring, 0.3) + to_cam * 0.35
mid1.z = 0.12
mid2 = ankle.lerp(ring, 0.72) + to_cam * 0.35
mid2.z = 0.12
small_seg = seg_mesh.copy()
small_seg.name = "BallChainSegment"
small_seg.materials.clear()
iron = bpy.data.materials.new("ChainIron")
b = iron.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = srgb("STEEL")
b.inputs["Metallic"].default_value = 0.8
b.inputs["Roughness"].default_value = 0.35
small_seg.materials.append(iron)
ball_chain = tile_chain(small_seg, [ankle + leg_axis * 0.05, mid1, mid2, ring], False, C_FG, 0.28,
                        lambda p, t: Vector((0, 0, 1)), name="BallChain")

# "-$20,000" above the ball and chain, clear of the character (sized to fit beside him)
DT = LY.F_DEBT_TEXT
ball_top = screen(ball_c + Vector((0, 0, BL["radius"])))
ball_mid = screen(ball_c)
d_depth = depth_of(ball_c) * DT["depth"]
char_uv = [screen(p) for p in rig.bounds()]


def char_left(y0, y1):
    xs = [u.x for u in char_uv if y0 <= u.y <= y1]
    return min(xs) if xs else 1.0


debt_text = text_obj("DebtText", DT["text"], 1.0, srgb("RED"), C_NUM, extrude=0.012, bevel=0.0)
debt_text.data.materials[0] = flat_material("DebtDigits", PAL["RED"]["rgb"])   # the palette red, unlit
debt_text.data.space_character = DT["spacing"]


def place_debt(cap):
    p = ray(ball_mid.x, ball_top.y + 0.08, d_depth)
    debt_text.data.size = size_for_cap(cap, p)
    debt_text.matrix_world = Matrix.Translation(p) @ face_camera(p, DT["tilt"])
    for _ in range(8):
        bpy.context.view_layer.update()
        x0, x1, y0, y1 = frame_box([debt_text])
        want_x0 = max(LY.SAFE + 0.006, min(ball_mid.x - (x1 - x0) / 2, char_left(y0 - 0.03, y1 + 0.03) - DT["gap"] - (x1 - x0)))
        dx, dy = want_x0 - x0, (ball_top.y + DT["dy"]) - y0
        if abs(dx) < 5e-4 and abs(dy) < 5e-4:
            break
        q = screen(p)
        p = ray(q.x + dx * 0.9, q.y + dy * 0.9, d_depth)
        debt_text.matrix_world = Matrix.Translation(p) @ face_camera(p, DT["tilt"])
    bpy.context.view_layer.update()
    b_ = frame_box([debt_text])
    return b_, char_left(b_[2] - 0.03, b_[3] + 0.03) - DT["gap"]


cap = DT["cap"]
while True:
    b_, limit = place_debt(cap)
    if b_[1] <= limit or cap <= DT["min_cap"]:
        break
    cap -= 0.002
print(f"debt number: cap {cap:.3f}, x {b_[0]:.3f}-{b_[1]:.3f}, character starts at {limit + DT['gap']:.3f}")

# debt pile right of his feet: real Credit Card debt + cash stacks built with the game's kit
lfoot = rig.world("LeftAnkle")
pile = []
for kind, side, toward, yaw, s in LY.F_PILE:
    p = lfoot + ground_side * side + to_cam * toward
    p.z = 0.0
    base = Matrix.Translation(p) @ rot(z=math.degrees(math.atan2(-to_cam.x, to_cam.y)) + yaw)
    if kind == "card":
        pile += lib.place("props", "Debt_CreditCard", C_FG, base @ Matrix.Scale(s, 4))
    else:
        m = kit.Model("CashStack")
        hgt = 0.0
        for k in range(random.choice((3, 4, 5))):
            with m.at((random.uniform(-0.12, 0.12), hgt, random.uniform(-0.1, 0.1)), yaw=random.uniform(-14, 14)):
                m.box((2.6, 0.5, 1.25), (0, 0.25, 0), "GREEN", bevel="S")
                m.box((0.62, 0.56, 1.31), (0, 0.25, 0), "CREAM", bevel="XS")
            hgt += 0.5
        objs = kit_build(m, C_FG)
        for o in objs:
            o.matrix_world = base @ Matrix.Scale(s, 4) @ o.matrix_world
        pile += objs

# ====================================================================== lights
world = bpy.data.worlds.new("Sky")
scn.world = world
wn = world.node_tree
bgn = wn.nodes["Background"]
tcn, sep, wr = wn.nodes.new("ShaderNodeTexCoord"), wn.nodes.new("ShaderNodeSeparateXYZ"), wn.nodes.new("ShaderNodeValToRGB")
wr.color_ramp.elements[0].position, wr.color_ramp.elements[0].color = 0.0, (*srgb("WINDOW")[:3], 1)
wr.color_ramp.elements[1].position, wr.color_ramp.elements[1].color = 0.55, (0.06, 0.26, 0.8, 1)
wn.links.new(tcn.outputs["Generated"], sep.inputs[0])
wn.links.new(sep.outputs["Z"], wr.inputs["Fac"])
wn.links.new(wr.outputs["Color"], bgn.inputs["Color"])
bgn.inputs["Strength"].default_value = 1.0


def light(name, kind, energy, colour, pos=None, target=None, size=1.0, receivers=None, rot_euler=None):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
    C_LIGHTS.objects.link(l)
    l.data.energy, l.data.color = energy, colour
    if kind == 'AREA':
        l.data.size = size
    if pos is not None:
        l.location = pos
    if target is not None:
        l.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    if rot_euler is not None:
        l.rotation_euler = rot_euler
    if receivers is not None:
        l.light_linking.receiver_collection = receivers
    return l


lit_fg = bpy.data.collections.new("SunLit")          # the sun lights only the foreground layer
for c_ in (C_CHAR, C_FG, C_NUM, C_NEAR, C_COINS, C_CLOUDS, C_GROUND, C_MG):
    lit_fg.children.link(c_)
lit_dream = bpy.data.collections.new("DreamLit")     # the warm dream lights: yacht group and coins
for c_ in (C_DREAM, C_COINS):
    lit_dream.children.link(c_)
sun = light("Sun", 'SUN', 3.2, (1.0, 0.97, 0.94), receivers=lit_fg,
            rot_euler=(math.radians(52), 0, math.radians(-150)))
sun.data.angle = math.radians(4)
head_c = rig.centre("Head")
light("RimWarm", 'AREA', 16000, (1.0, 0.72, 0.36), pos=head_c + Vector((6.0, 5.0, 2.5)), target=head_c + Vector((0, 0, -0.6)),
      size=3.0, receivers=C_CHAR)
chest = rig.centre("UpperTorso")
light("RimWarmBody", 'AREA', 11000, (1.0, 0.7, 0.32), pos=chest + Vector((5.5, 5.5, 0.5)), target=chest,
      size=3.0, receivers=C_CHAR)
light("FaceFill", 'AREA', 260, (1.0, 0.86, 0.66), pos=head_c + Vector((3.0, -5.0, 1.5)), target=head_c, size=3.0,
      receivers=C_CHAR)
light("DreamWarmKey", 'AREA', 9.0e5, (1.0, 0.74, 0.4), pos=dc + Vector((-55, -90, -60)), target=dc, size=80,
      receivers=lit_dream)
for o in C_NEAR.objects:                                    # the near coin: bright gold
    p_ = o.matrix_world.translation
    light("NearCoinKey_" + o.name, 'AREA', 160, (1.0, 0.86, 0.6),
          pos=p_ - cam_right * 1.2 + cam_up * 1.4 - cam_fwd * 1.6, target=p_, size=1.5, receivers=C_NEAR)
light("DreamTop", 'AREA', 2.5e5, (1.0, 0.85, 0.6), pos=dc + Vector((0, -40, 90)), target=dc, size=80, receivers=lit_dream)

# ====================================================================== icon cameras
def square_view(c, points, at, lens=None, fill=None, iters=8):
    """Aim camera c (fixed position) so `points` centre at screen `at` on a square frame; with
    `fill`, also set the lens so they span that fraction of the frame."""
    keep_res = (scn.render.resolution_x, scn.render.resolution_y)
    scn.render.resolution_x = scn.render.resolution_y = 512
    pos = c.matrix_world.translation.copy()
    look = sum(points, Vector()) / len(points)
    if lens:
        c.data.lens = lens
    for _ in range(iters):
        fwd = (look - pos).normalized()
        c.matrix_world = (Matrix.Translation(pos) @ fwd.to_track_quat('-Z', 'Y').to_matrix().to_4x4()
                          @ Matrix.Rotation(math.radians(c["roll"]), 4, 'Z'))
        bpy.context.view_layer.update()
        uv = [world_to_camera_view(scn, c, p) for p in points]
        x0, x1 = min(u.x for u in uv), max(u.x for u in uv)
        y0, y1 = min(u.y for u in uv), max(u.y for u in uv)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        R_ = c.matrix_world.to_3x3()
        tan = (c.data.sensor_width / 2) / c.data.lens
        dist = (look - pos).length
        look = look + (R_ @ Vector(((cx - at[0]) * 2 * tan, (cy - at[1]) * 2 * tan, 0))) * dist
        if fill:
            c.data.lens = min(max(c.data.lens * fill / max(x1 - x0, y1 - y0), 12.0), 400.0)
    scn.render.resolution_x, scn.render.resolution_y = keep_res


def new_camera(name, pos, roll):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    scn.collection.objects.link(c)
    c.data.sensor_width, c.data.sensor_fit = 36.0, 'HORIZONTAL'
    c.data.clip_start, c.data.clip_end = 0.05, 8000
    c.matrix_world = Matrix.Translation(pos)
    c["roll"] = roll
    return c


dream_pts = bounds([o for o in C_DREAM.objects if o.type in ('MESH', 'FONT')])
IC = LY.F_ICON                    # A: his whole head in the bottom-left corner, the dream up right
icam = new_camera("IconCamera", cam.matrix_world.translation + Vector((0, 0, IC["lift"])) + ground_side * IC["side"],
                  IC["roll"])
square_view(icam, [dc], IC["yacht_at"], lens=IC["lens"])
IB = LY.F_ICON_B                  # B: no character, the yacht, padlock and tag centred
icam_b = new_camera("IconCameraB", cam.matrix_world.translation + Vector((0, 0, IB["lift"])), IB["roll"])
square_view(icam_b, dream_pts, (0.5, 0.5), lens=40.0, fill=IB["fill"])

# ====================================================================== render settings
r = scn.render
scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = 28 if A.quick else 128
scn.cycles.use_denoising = True
scn.cycles.max_bounces = 4
scn.cycles.transparent_max_bounces = 16
scn.cycles.sample_clamp_indirect = 8.0
scn.view_settings.view_transform = 'Standard'
r.resolution_x, r.resolution_y = (960, 540) if A.quick else (1920, 1080)


# ====================================================================== report
def frame(objs, c=None):
    pts = bounds(objs)
    uv = [screen(p, c) for p in pts]
    uv = [u for u in uv if u.z > 0]
    return (min(u.x for u in uv), max(u.x for u in uv), min(u.y for u in uv), max(u.y for u in uv))


bpy.context.view_layer.update()
report = {
    "character": list(parts.values()), "head": [parts["Head"]], "hair": [parts["Hair"]],
    "yacht+chains": [o for o in C_DREAM.objects if o.type == 'MESH' and not o.name.startswith("PriceTag")],
    "padlock": padlock, "price tag": [tag, tag_text], "debt text": [debt_text],
    "ball": ball_objs, "debt pile": pile, "pizzeria": [o for o in C_MG.objects if "PIZZERIA" in o.name],
    "supercar": [o for o in C_BG.objects if o.get("model") == "Supercar"],
    "jet": [o for o in C_BG.objects if o.get("model") == "PrivateJet"],
}
print("FRAME (x0 x1 y0 y1)")
for k, v in report.items():
    b_ = frame(v)
    print(f"  {k:13s} x {b_[0]:.2f}-{b_[1]:.2f}  y {b_[2]:.2f}-{b_[3]:.2f}")

keep_res = (scn.render.resolution_x, scn.render.resolution_y)
scn.render.resolution_x = scn.render.resolution_y = 512
for label, c_ in (("ICON A FRAME", icam), ("ICON B FRAME", icam_b)):
    print(label)
    for k in ("head", "hair", "yacht+chains", "padlock", "price tag"):
        try:
            b_ = frame(report[k], c_)
            print(f"  {k:13s} x {b_[0]:.2f}-{b_[1]:.2f}  y {b_[2]:.2f}-{b_[3]:.2f}")
        except ValueError:
            print(f"  {k:13s} (out of view)")
scn.render.resolution_x, scn.render.resolution_y = keep_res

# ====================================================================== save + passes
# one copy of each palette image (every model library brought its own), then drop orphans
for base in ("palette_color.png", "palette_roughness.png"):
    imgs = sorted((i for i in bpy.data.images if i.name.split(".png")[0] + ".png" == base), key=lambda i: i.name)
    for dup in imgs[1:]:
        dup.user_remap(imgs[0])
        bpy.data.images.remove(dup)
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(A.out, "thumbnail.blend"))
if A.no_render:
    sys.exit(0)

GROUPS = {C_CHAR: (1, 0, 0, 1), C_DREAM: (0, 1, 0, 1), C_NUM: (0, 0, 1, 1)}


ALL = (C_CHAR, C_DREAM, C_NUM, C_FG, C_MG, C_BG, C_GROUND, C_SKY, C_COINS, C_CLOUDS, C_NEAR)


def set_visible(hide):
    for c_ in ALL:
        c_.hide_render = c_ in hide


def override(kind):
    m = bpy.data.materials.get("_" + kind) or bpy.data.materials.new("_" + kind)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    if kind == "matte":
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        nt.links.new(oi.outputs["Color"], em.inputs["Color"])
    else:
        cd = nt.nodes.new("ShaderNodeCameraData")
        nt.links.new(cd.outputs["View Z Depth"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def render(path, kind, c, extra_hide=()):
    scn.camera = c
    vl = bpy.context.view_layer
    r.film_transparent = kind == "near"
    r.image_settings.file_format = 'OPEN_EXR'
    r.image_settings.color_depth = '32'
    r.image_settings.color_mode = 'RGBA'
    keep = (scn.cycles.samples, scn.cycles.use_denoising, scn.world)
    if kind in ("matte", "depth"):
        for o in scn.objects:
            o.color = (0, 0, 0, 1)
        for c_, col in GROUPS.items():
            for o in c_.all_objects:
                o.color = col
        vl.material_override = override(kind)
        scn.cycles.samples, scn.cycles.use_denoising = (24 if kind == "matte" else 4), False
        scn.world = None
        set_visible({C_NEAR, C_SKY} | set(extra_hide))
    elif kind == "beauty":
        set_visible({C_NEAR} | set(extra_hide))
    elif kind == "near":
        set_visible(set(ALL) - {C_NEAR})
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    vl.material_override = None
    scn.cycles.samples, scn.cycles.use_denoising, scn.world = keep
    set_visible(set())


only = set(A.only.split(",")) if A.only else None
main_res = (r.resolution_x, r.resolution_y)
for kind in ("beauty", "matte", "depth", "near"):
    if only and kind not in only and "main" not in only:
        continue
    r.resolution_x, r.resolution_y = main_res
    render(os.path.join(A.out, f"main_{kind}.exr"), kind, cam)
for prefix, c_, hide in (("iconA", icam, ()), ("iconB", icam_b, (C_CHAR, C_FG, C_NUM))):
    if only and prefix not in only:
        continue
    for kind in ("beauty", "matte", "depth"):
        r.resolution_x = r.resolution_y = 512 if A.quick else IC["res"]
        render(os.path.join(A.out, f"{prefix}_{kind}.exr"), kind, c_, hide)
r.resolution_x, r.resolution_y = main_res
scn.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(A.out, "thumbnail.blend"))

"""
wo.py - shared Blender helpers for the world overhaul (Blender 5.x, background mode).

Coordinates
-----------
Roblox: Y is up, the FRONT of a model is -Z.   Blender: Z is up.
We convert Roblox (X, Y, Z) -> Blender (X, -Z, Y). This is a proper rotation (no mirroring), and it is
exactly what Blender's FBX exporter undoes with its default axes (Forward -Z, Up Y), so a model built
here in "Roblox local space converted to Blender" drops into Roblox with the same orientation.
=> In Blender, the FRONT of every model faces +Y.   1 Blender unit = 1 stud.
"""

import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

C = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))  # Roblox -> Blender
CT = C.transposed()


def rb_vec(v):
    """Roblox point/vector -> Blender."""
    return Vector((v[0], -v[2], v[1]))


def rb_rot(cf):
    m = cf[3:]
    return Matrix(((m[0], m[1], m[2]), (m[3], m[4], m[5]), (m[6], m[7], m[8])))


def rb_matrix(cf):
    """Roblox CFrame (12 numbers) -> Blender 4x4 world matrix."""
    rot = C @ rb_rot(cf) @ CT
    mat = rot.to_4x4()
    mat.translation = rb_vec(cf[:3])
    return mat


def cf_inv(a):
    ax, ay, az, *m = a
    t = [m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]]
    x = -(t[0] * ax + t[1] * ay + t[2] * az)
    y = -(t[3] * ax + t[4] * ay + t[5] * az)
    z = -(t[6] * ax + t[7] * ay + t[8] * az)
    return [x, y, z] + t


def cf_mul(a, b):
    ax, ay, az, *am = a
    bx, by, bz, *bm = b
    m = [0.0] * 9
    for i in range(3):
        for j in range(3):
            m[i * 3 + j] = sum(am[i * 3 + k] * bm[k * 3 + j] for k in range(3))
    x = am[0] * bx + am[1] * by + am[2] * bz + ax
    y = am[3] * bx + am[4] * by + am[5] * bz + ay
    z = am[6] * bx + am[7] * by + am[8] * bz + az
    return [x, y, z] + m


def lin(rgb):
    """sRGB 0-255 -> linear 0-1 RGBA."""

    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (ch(rgb[0]), ch(rgb[1]), ch(rgb[2]), 1.0)


# ----------------------------------------------------------------------------
# Scene
# ----------------------------------------------------------------------------


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0


def setup_render(width=1600, height=900, samples=48, transparent=False):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except TypeError:
        pass
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 4
    scene.cycles.transparent_max_bounces = 8
    scene.cycles.use_adaptive_sampling = True
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = transparent
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    # "Standard" keeps colors bright and saturated (same choice as the icon renders)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.render.threads_mode = "AUTO"


def setup_lighting(sun_strength=3.2, sky_strength=0.85, sky_rgb=(150, 190, 240), sun_direction=None):
    """Sunny afternoon like the game (Lighting.ClockTime 14.5): warm sun + light blue sky fill."""
    scene = bpy.context.scene
    world = bpy.data.worlds.get("Sky") or bpy.data.worlds.new("Sky")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = lin(sky_rgb)
    bg.inputs["Strength"].default_value = sky_strength
    sun = bpy.data.objects.get("Sun")
    if sun is None:
        data = bpy.data.lights.new("Sun", "SUN")
        sun = bpy.data.objects.new("Sun", data)
        scene.collection.objects.link(sun)
    sun.data.energy = sun_strength
    sun.data.angle = math.radians(6)
    sun.data.color = lin((255, 246, 228))[:3]
    # world shots: fixed angle (BEFORE and AFTER use the same). Studio: from the upper left front, like the
    # icon key light (models face +Y in Blender).
    if sun_direction is None:
        sun.rotation_euler = (math.radians(48), math.radians(0), math.radians(-38))
    else:
        sun.rotation_euler = Vector(sun_direction).to_track_quat("-Z", "Y").to_euler()
    return sun


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, lens=35.0, ortho_scale=None):
    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    if ortho_scale:
        data.type = "ORTHO"
        data.ortho_scale = ortho_scale
    else:
        data.type = "PERSP"
        data.lens = lens
    data.clip_start = 0.5
    data.clip_end = 20000
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(location)
    look_at(cam, target)
    return cam


def render(path, cam=None):
    scene = bpy.context.scene
    if cam is not None:
        scene.camera = cam
    os.makedirs(os.path.dirname(path), exist_ok=True)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


# ----------------------------------------------------------------------------
# Roblox-look materials (for the BEFORE blockout)
# ----------------------------------------------------------------------------

ROUGH = {"SmoothPlastic": 0.45, "Plastic": 0.6, "Metal": 0.35, "Marble": 0.3, "Glass": 0.05, "Neon": 0.5,
         "ForceField": 0.3}
_mats = {}


def roblox_material(color, material, transparency):
    key = (tuple(int(round(c)) for c in color), material, round(transparency, 2))
    if key in _mats:
        return _mats[key]
    mat = bpy.data.materials.new("RB_%s_%d_%d_%d_%d" % (material, key[0][0], key[0][1], key[0][2], int(transparency * 100)))
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = lin(key[0])
    bsdf.inputs["Roughness"].default_value = ROUGH.get(material, 0.85)
    if material == "Metal":
        bsdf.inputs["Metallic"].default_value = 0.6
    if material == "Neon":
        bsdf.inputs["Emission Color"].default_value = lin(key[0])
        bsdf.inputs["Emission Strength"].default_value = 2.5
    alpha = 1.0 - transparency
    if material == "Glass":
        alpha = min(alpha, 0.6)
    if material == "ForceField":
        alpha = min(alpha, 0.45)
    if alpha < 0.999:
        bsdf.inputs["Alpha"].default_value = alpha
    _mats[key] = mat
    return mat


# ----------------------------------------------------------------------------
# Roblox primitive parts as mesh data (in the part's own Roblox local space)
# ----------------------------------------------------------------------------


def _box_verts(sx, sy, sz):
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
         (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 4, 7, 3)]
    return v, f, False


def _wedge_verts(sx, sy, sz):
    # Roblox WedgePart: flat bottom, full-height face at +Z (back), slope down to the front (-Z)
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (-hx, hy, hz), (hx, hy, hz)]
    f = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 4, 5, 1), (0, 3, 4), (1, 5, 2)]
    return v, f, False


def _corner_wedge_verts(sx, sy, sz):
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (hx, hy, -hz)]
    f = [(0, 1, 2, 3), (1, 4, 2), (2, 4, 3), (3, 4, 0), (0, 4, 1)]
    return v, f, False


def _cylinder_verts(sx, sy, sz, segments=24):
    r = min(sy, sz) / 2
    hx = sx / 2
    v, f = [], []
    for side in (-hx, hx):
        for i in range(segments):
            a = 2 * math.pi * i / segments
            v.append((side, r * math.cos(a), r * math.sin(a)))
    n = segments
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    f.append(tuple(reversed(range(n))))
    f.append(tuple(range(n, 2 * n)))
    return v, f, "sides"


def _ball_verts(sx, sy, sz, rings=10, segments=20):
    r = min(sx, sy, sz) / 2
    v = [(0, -r, 0)]
    for i in range(1, rings):
        phi = math.pi * i / rings - math.pi / 2
        for j in range(segments):
            t = 2 * math.pi * j / segments
            v.append((r * math.cos(phi) * math.cos(t), r * math.sin(phi), r * math.cos(phi) * math.sin(t)))
    v.append((0, r, 0))
    f = []
    for j in range(segments):
        f.append((0, 1 + (j + 1) % segments, 1 + j))
    for i in range(rings - 2):
        for j in range(segments):
            a = 1 + i * segments + j
            b = 1 + i * segments + (j + 1) % segments
            f.append((a, b, b + segments, a + segments))
    top = len(v) - 1
    base = 1 + (rings - 2) * segments
    for j in range(segments):
        f.append((base + j, base + (j + 1) % segments, top))
    return v, f, True


def part_geometry(part):
    sx, sy, sz = part["Size"]
    cls, shape = part["class"], part.get("Shape", "Block")
    if cls == "WedgePart":
        return _wedge_verts(sx, sy, sz)
    if cls == "CornerWedgePart":
        return _corner_wedge_verts(sx, sy, sz)
    if shape == "Cylinder":
        return _cylinder_verts(sx, sy, sz)
    if shape == "Ball":
        return _ball_verts(sx, sy, sz)
    return _box_verts(sx, sy, sz)


def blockout_object(name, parts, frame_cf, col, scale=1.0):
    """One Blender object made of Roblox parts. Its origin is `frame_cf` (a Roblox CFrame)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    inv = cf_inv(frame_cf)
    slots = []
    for part in parts:
        local = cf_mul(inv, part["CFrame"])
        rot = C @ rb_rot(local) @ CT
        pos = rb_vec(local[:3])
        verts, faces, smooth = part_geometry(part)
        mat = roblox_material(part["Color"], part["Material"], part.get("Transparency", 0))
        if mat not in slots:
            slots.append(mat)
        index = slots.index(mat)
        bverts = [bm.verts.new((rot @ rb_vec(v) + pos) / scale) for v in verts]
        for face in faces:
            try:
                bf = bm.faces.new([bverts[i] for i in face])
            except ValueError:
                continue
            bf.material_index = index
            bf.smooth = bool(smooth) and not (smooth == "sides" and len(face) > 4)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    for mat in slots:
        mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.matrix_world = rb_matrix(frame_cf)
    if scale != 1.0:
        obj.scale = (scale, scale, scale)
    return obj


# ----------------------------------------------------------------------------
# The 5-stud player dummy (for scale)
# ----------------------------------------------------------------------------


def player_dummy(col, location=(0, 0, 0), facing=0.0, name="PlayerDummy_5studs"):
    """A classic blocky 5-stud-tall Roblox player: legs 2, torso 2, head 1 (+ arms)."""
    skin = roblox_material((245, 205, 160), "SmoothPlastic", 0)
    shirt = roblox_material((60, 120, 220), "SmoothPlastic", 0)
    pants = roblox_material((50, 60, 90), "SmoothPlastic", 0)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    pieces = [  # (center x, y, z in Blender), size, material
        ((-0.5, 0, 1.0), (0.95, 1.0, 2.0), pants), ((0.5, 0, 1.0), (0.95, 1.0, 2.0), pants),
        ((0, 0, 3.0), (2.0, 1.0, 2.0), shirt),
        ((-1.5, 0, 3.0), (0.95, 1.0, 2.0), skin), ((1.5, 0, 3.0), (0.95, 1.0, 2.0), skin),
        ((0, 0, 4.5), (1.2, 1.0, 1.0), skin),
    ]
    mats = [pants, shirt, skin]
    for (cx, cy, cz), (sx, sy, sz), mat in pieces:
        verts, faces, _ = _box_verts(sx, sy, sz)
        bv = [bm.verts.new((v[0] + cx, v[1] + cy, v[2] + cz)) for v in verts]
        for face in faces:
            f = bm.faces.new([bv[i] for i in face])
            f.material_index = mats.index(mat)
    bm.to_mesh(mesh)
    bm.free()
    for m in mats:
        mesh.materials.append(m)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (0, 0, facing)
    return obj


def text_label(col, body, location, size=1.0, color=(40, 26, 58), name=None):
    curve = bpy.data.curves.new(name or ("Label_" + body), "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.02
    obj = bpy.data.objects.new(name or ("Label_" + body), curve)
    col.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, math.radians(180))  # readable from +Y (the front)
    mat = bpy.data.materials.get("LabelInk") or bpy.data.materials.new("LabelInk")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = lin(color)
    bsdf.inputs["Roughness"].default_value = 0.6
    curve.materials.append(mat)
    return obj

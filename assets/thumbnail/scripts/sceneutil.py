"""Small Blender helpers shared by the thumbnail scripts."""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

_mats = {}


def srgb(c):
    """sRGB 0..1 -> linear (Blender colour inputs are linear)."""
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c[:3])


def mat(name, color, rough=0.6, emit=0.0, metal=0.0):
    """Flat palette-style material (one colour, given in sRGB like the game palette)."""
    color = srgb(color)
    key = (name, tuple(round(c, 3) for c in color), rough, emit, metal)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color[:3], 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*color[:3], 1)
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*color[:3], 1)
    _mats[key] = m
    return m


def link(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def mesh_box(name, size, center=(0, 0, 0), material=None, bevel=0.0, coll=None):
    """Box mesh with its centre at `center` in object space (object origin at 0)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    if material:
        me.materials.append(material)
    if bevel:
        m = o.modifiers.new("Bevel", 'BEVEL')
        m.width = bevel
        m.segments = 3
        m.limit_method = 'NONE'
        for p in me.polygons:
            p.use_smooth = True
    return o


def mesh_sphere(name, radius, center=(0, 0, 0), material=None, coll=None, seg=32):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=radius)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    if material:
        me.materials.append(material)
    return o


def mesh_cylinder(name, radius, depth, center=(0, 0, 0), material=None, coll=None, seg=32):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=radius, radius2=radius, depth=depth)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    if material:
        me.materials.append(material)
    return o


def bar(name, p0, p1, thickness, material=None, coll=None):
    """Square bar from p0 to p1 (world space)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = mesh_box(name, (thickness, thickness, d.length), material=material, coll=coll)
    o.matrix_world = Matrix.Translation((p0 + p1) / 2) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    return o


def empty(name, coll=None, matrix=None):
    e = bpy.data.objects.new(name, None)
    (coll or bpy.context.scene.collection).objects.link(e)
    if matrix is not None:
        e.matrix_world = matrix
    return e


def parent_keep(child, parent):
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = mw


def rot(x=0.0, y=0.0, z=0.0):
    """Degrees -> rotation matrix applied Z, then Y, then X in local terms (R = Rz Ry Rx)."""
    return (Matrix.Rotation(math.radians(z), 4, 'Z') @ Matrix.Rotation(math.radians(y), 4, 'Y')
            @ Matrix.Rotation(math.radians(x), 4, 'X'))


def world_bounds(objs):
    pts = []
    for o in objs:
        if o.type == 'MESH':
            dg = bpy.context.evaluated_depsgraph_get()
            ev = o.evaluated_get(dg)
            pts += [ev.matrix_world @ v.co for v in ev.data.vertices]
    return pts

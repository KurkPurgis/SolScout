"""
outline_compare.py - ONE comparison: a workplace building without and with an inverted-hull outline
(the icon outline color INK). Output: renders/outline_comparison.png (left: no outline = the default,
right: with outline). From the in-game turn camera angle and from 50 studs.

Inverted hull: a copy of the mesh pushed outward (Solidify, flipped normals) that only shows its far
side, so it peeks out around the silhouette as a dark line. In Roblox this would be a second MeshPart
per model (double triangles) with front-face culling... which Roblox does not offer: the hull would need
its normals flipped in the mesh itself. See STYLE_GUIDE section 8.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import kit  # noqa: E402
import review  # noqa: E402
import wo  # noqa: E402

NAME = "Workplace_Building_PIZZERIA"
THICKNESS = 0.14


def ink_material():
    mat = bpy.data.materials.new("WO_OutlineInk")
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    mix = nodes.new("ShaderNodeMixShader")
    geo = nodes.new("ShaderNodeNewGeometry")
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = kit.lin(kit.COLORS["INK"]["rgb"])
    transp = nodes.new("ShaderNodeBsdfTransparent")
    # reversed hull: its near side looks away from the camera (backfacing) -> invisible;
    # its far side, peeking out around the silhouette, faces the camera -> ink
    links.new(geo.outputs["Backfacing"], mix.inputs["Fac"])
    links.new(emit.outputs["Emission"], mix.inputs[1])
    links.new(transp.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])
    mat.use_backface_culling = True
    return mat


def main():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "blend", "buildings.blend"))
    col = bpy.data.collections["NEW_" + NAME]
    for c in bpy.data.collections["Models"].children:
        c.hide_render = c is not col
    objs = [o for o in col.objects if o.type == "MESH"]
    review.studio()
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 960, 600
    ground = bpy.data.objects.get("StudioGround")
    ground.location.z = -1.02
    # in-game turn camera: base * (0, 28, -58) looking at base * (0, 6, 2)  (Roblox) -> Blender
    cam = wo.camera("CAM_turn", (0, 58, 28), (0, -2, 6), lens=35)
    far = wo.camera("CAM_far", (30, 62, 22), (0, -12, 6), lens=50)
    out_dir = os.path.join(ROOT, "renders", "outline")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    wo.render(os.path.join(out_dir, "no_outline_turncam.png"), cam)
    paths.append(os.path.join(out_dir, "no_outline_turncam.png"))
    ink = ink_material()
    import bmesh
    for o in objs:
        # inverted hull: a copy pushed outward along the normals, with its faces turned inside out
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.normal_update()
        for v in bm.verts:
            v.co += v.normal * THICKNESS
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        me = bpy.data.meshes.new(o.name + "_Hull")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(ink)
        hull = bpy.data.objects.new(o.name + "_Hull", me)
        col.objects.link(hull)
        hull.matrix_world = o.matrix_world
        # the hull is only seen by the camera: it must not shadow or tint the model inside it
        hull.visible_shadow = False
        hull.visible_diffuse = False
        hull.visible_glossy = False
        hull.visible_transmission = False
        hull.visible_volume_scatter = False
    wo.render(os.path.join(out_dir, "outline_turncam.png"), cam)
    paths.append(os.path.join(out_dir, "outline_turncam.png"))
    tris = sum(len(o.data.polygons) for o in objs)
    review.strip(paths, os.path.join(ROOT, "renders", "outline_comparison.png"))
    print("outline comparison done; hull doubles the mesh (%d polygons -> %d)" % (tris, tris * 2))


if __name__ == "__main__":
    main()

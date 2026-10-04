"""
lineups.py - one picture per category (and page): every object type side by side, true scale,
with a 5-stud player dummy and name labels. Used for BEFORE and AFTER (same layout, same cameras).

    bvenv/bin/python tools/blender/lineups.py before <blend> <out dir>
    bvenv/bin/python tools/blender/lineups.py after  <blend> <out dir>

before: the source of a template is the blockout object of its canonical instance.
after:  the source is the collection NEW_<template> (falls back to the blockout if not modelled yet).
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import shots  # noqa: E402
import wo  # noqa: E402


def source_objects(templates, name, phase):
    if phase == "after":
        col = bpy.data.collections.get("NEW_" + name)
        if col is not None and col.all_objects:
            return list(col.all_objects), True
    obj = bpy.data.objects.get(templates[name]["canonical"])
    return ([obj] if obj else []), False


def build_page(templates, names, phase, page_col):
    placed = shots.lineup_layout(templates, names)
    made = []
    for name, pos in placed:
        sources, is_new = source_objects(templates, name, phase)
        for src in sources:
            if src.type not in ("MESH", "FONT", "CURVE"):
                continue
            copy = src.copy()
            page_col.objects.link(copy)
            # sources live at their own spot: keep only their offset from the template origin
            local = src.get("template_local")
            m = Matrix(local) if local is not None else Matrix.Identity(4)
            copy.parent = None
            copy.matrix_world = Matrix.Translation(pos) @ m
            made.append(copy)
        t = templates[name]
        front = -t["bbox_min"][2]  # Roblox -Z (front) -> Blender +Y
        label = wo.text_label(page_col, name, pos + Vector(((t["bbox_min"][0] + t["bbox_max"][0]) / 2, front + 1.2, 0.03)),
                              size=max(0.7, min(2.5, t["size"][0] / 7)), name="L_" + name)
        label.rotation_euler = (0, 0, math.radians(180))
    # ground and a dummy for scale, left of the first object
    xs = [pos.x + templates[n]["bbox_min"][0] for n, pos in placed]
    left = min(xs) - 3
    wo.player_dummy(page_col, location=(left, shots.LINEUP_ORIGIN.y, 0), facing=0, name="Dummy_" + page_col.name)
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(shots.LINEUP_ORIGIN.x, shots.LINEUP_ORIGIN.y, -0.01))
    ground = bpy.context.active_object
    for c in ground.users_collection:
        c.objects.unlink(ground)
    page_col.objects.link(ground)
    ground.data.materials.append(wo.roblox_material((205, 210, 215), "SmoothPlastic", 0))
    return placed


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    phase, blend, out_dir = args[0], args[1], args[2]
    only = args[3:]
    bpy.ops.wm.open_mainfile(filepath=blend)
    templates = json.load(open(os.path.join(ROOT, "data", "templates.json")))
    pages = shots.lineup_templates(templates)
    lineup = wo.collection("Lineup")
    for col in list(bpy.context.scene.collection.children):
        if col.name != "Lineup":
            col.hide_render = True
    scene = bpy.context.scene
    scene.cycles.samples = 32
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    for cat, chunks in pages.items():
        for index, names in enumerate(chunks):
            page = "%s_%d" % (cat, index + 1)
            if only and page not in only:
                continue
            page_col = wo.collection("Page_" + page, lineup)
            placed = build_page(templates, names, phase, page_col)
            for other in lineup.children:
                other.hide_render = other is not page_col
            cam = shots.lineup_camera(templates, placed, page)
            wo.render(os.path.join(out_dir, "lineup_%s.png" % page), cam)
            print("rendered lineup", page, names)
            # drop the page again (keeps the file small)
            for obj in list(page_col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(page_col)


if __name__ == "__main__":
    main()

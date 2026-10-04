"""
lineups.py - one picture per category (and page): every object type side by side, true scale,
with a 5-stud player dummy and name labels. Used for BEFORE and AFTER (same layout, same cameras).

    bvenv/bin/python tools/blender/lineups.py before <blend> <out dir>
    bvenv/bin/python tools/blender/lineups.py after  <blend> <out dir>

before: the source of a template is the blockout object of its canonical instance.
after:  the source is the new model from the category blends (falls back to the blockout if not modelled).
The camera is fitted exactly around all objects, labels and the dummy (shots.lineup_camera).
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


MODELS = {}


def source_objects(templates, name, phase):
    if phase == "after" and MODELS.get(name):
        return [o for o in MODELS[name] if not o.hide_render], True
    obj = bpy.data.objects.get(templates[name]["canonical"])
    return ([obj] if obj else []), False


def build_page(templates, names, phase, page_col):
    placed = shots.lineup_layout(templates, names)
    made = []
    extra = []
    for name, pos in placed:
        t = templates[name]
        sources, is_new = source_objects(templates, name, phase)
        # the sign text (SurfaceGui) stays on the old parts in both looks: it is copied next to the model
        texts = []
        canon = bpy.data.objects.get(t["canonical"])
        if canon is not None:
            # matrix_basis, not matrix_world: in after.blend the old blockouts are hidden, and Blender does not
            # re-evaluate matrix_world for hidden objects when the file is opened (it reads as identity)
            inv = canon.matrix_basis.inverted()
            for pid in t.get("canonical_part_ids", []):
                text = bpy.data.objects.get("Text_%d" % pid)
                if text is not None:
                    texts.append((text, inv @ text.matrix_basis))
        # text on the back (Roblox +Z = Blender -Y): turn the object around its box center to face the camera
        flip = Matrix.Identity(4)
        if texts and all(rel.translation.y < -0.01 for _, rel in texts):
            lo, hi = t["bbox_min"], t["bbox_max"]
            c = Vector(((lo[0] + hi[0]) / 2, -(lo[2] + hi[2]) / 2, 0))
            flip = Matrix.Translation(c) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-c)
        for src in sources:
            if src.type not in ("MESH", "FONT", "CURVE"):
                continue
            copy = src.copy()
            page_col.objects.link(copy)
            # blockouts live at their own spot in the world: keep only their offset from the template origin;
            # new models were built at the origin already
            if is_new:
                m = src.matrix_world.copy()
            else:
                local = src.get("template_local")
                m = Matrix(local) if local is not None else Matrix.Identity(4)
            copy.parent = None
            copy.matrix_world = Matrix.Translation(pos) @ flip @ m
            made.append(copy)
        for text, rel in texts:
            copy = text.copy()
            page_col.objects.link(copy)
            copy.hide_render = False
            copy.matrix_world = Matrix.Translation(pos) @ flip @ rel
        front = -t["bbox_min"][2]  # Roblox -Z (front) -> Blender +Y
        size = max(0.7, min(2.5, t["size"][0] / 7))
        lpos = pos + Vector(((t["bbox_min"][0] + t["bbox_max"][0]) / 2, front + 1.2, 0.03))
        label = wo.text_label(page_col, name, lpos, size=size, name="L_" + name)
        label.rotation_euler = (0, 0, math.radians(180))
        half = len(name) * size * 0.32
        extra.extend([lpos + Vector((-half, 0, 0)), lpos + Vector((half, 0, 0)), lpos + Vector((0, size, 0))])
    # ground and a dummy for scale, left of the first object
    xs = [pos.x + templates[n]["bbox_min"][0] for n, pos in placed]
    left = min(xs) - 3
    wo.player_dummy(page_col, location=(left, shots.LINEUP_ORIGIN.y, 0), facing=0, name="Dummy_" + page_col.name)
    extra.extend([Vector((left - 1.5, shots.LINEUP_ORIGIN.y, 0)), Vector((left - 1.5, shots.LINEUP_ORIGIN.y, 5.2))])
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(shots.LINEUP_ORIGIN.x, shots.LINEUP_ORIGIN.y, -0.01))
    ground = bpy.context.active_object
    for c in ground.users_collection:
        c.objects.unlink(ground)
    page_col.objects.link(ground)
    ground.data.materials.append(wo.roblox_material((205, 210, 215), "SmoothPlastic", 0))
    return placed, extra


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    phase, blend, out_dir = args[0], args[1], args[2]
    only = args[3:]
    bpy.ops.wm.open_mainfile(filepath=blend)
    templates = json.load(open(os.path.join(ROOT, "data", "templates.json")))
    if phase == "after":
        import build_after
        MODELS.update(build_after.load_models(json.load(open(os.path.join(ROOT, "data", "model_status.json")))))
    pages = shots.lineup_templates(templates)
    lineup = wo.collection("Lineup")
    for col in list(bpy.context.scene.collection.children):
        if col.name != "Lineup":
            col.hide_render = True
    scene = bpy.context.scene
    scene.cycles.samples = int(os.environ.get("WO_SAMPLES", "32"))
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    for cat, chunks in pages.items():
        for index, names in enumerate(chunks):
            page = "%s_%d" % (cat, index + 1)
            if only and page not in only:
                continue
            page_col = wo.collection("Page_" + page, lineup)
            placed, extra = build_page(templates, names, phase, page_col)
            for other in lineup.children:
                other.hide_render = other is not page_col
            cam = shots.lineup_camera(templates, placed, page, extra_points=extra)
            wo.render(os.path.join(out_dir, "lineup_%s.png" % page), cam)
            print("rendered lineup", page, names)
            # drop the page again (keeps the file small)
            for obj in list(page_col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(page_col)


if __name__ == "__main__":
    main()

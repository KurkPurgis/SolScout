"""
build_after.py - the "after" scene: the BEFORE scene with every remodelled object swapped in.

    bvenv/bin/python tools/blender/build_after.py            (build + save blend/after.blend)
    bvenv/bin/python tools/blender/build_after.py --render   (also render renders/after/*.png, same cameras)

How the swap works (the same steps IMPORT_PLAN.md describes for Roblox):
  * every object in data/objects.json has a frame (the original position + rotation). The new model was built
    with its origin on that frame, so it is placed with the frame's matrix and nothing else;
  * copies the game shows at another size (mini copies, floating dreams) get the copy's `scale`;
  * debts that grow with the amount reuse the model of their base template, stretched from the base box to
    the copy's box (data/plan.json "aliases"); the School Loan picks the model with the right number of books;
  * FOR SALE copies ("ghost") use the same mesh with see-through materials (the game's ForceField look);
  * the old blockout of a replaced object is hidden; its sign text stays (in Roblox the old part keeps it);
  * objects without a new model keep their blockout, so the picture never has holes.
Nothing that players interact with moves: no frame is changed.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import shots  # noqa: E402
import wo  # noqa: E402

CATEGORIES = ["buildings", "vehicles", "props", "nature", "ground", "decoration", "signs"]
GHOST_ALPHA = 0.5


def load_json(*parts):
    return json.load(open(os.path.join(ROOT, *parts)))


def load_models(status):
    """template -> list of mesh objects (appended from the category blends, not linked to the scene)."""
    by_blend = {}
    for name, entry in status.items():
        by_blend.setdefault(entry["category"], set()).add("NEW_" + name)
    models = {}
    for category, wanted in sorted(by_blend.items()):
        path = os.path.join(ROOT, "blend", category + ".blend")
        if not os.path.exists(path):
            continue
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            dst.collections = [c for c in src.collections if c in wanted]
        for col in dst.collections:
            if col is None:
                continue
            models[col.name[4:]] = [o for o in col.all_objects if o.type == "MESH"]
    return models


def bl_box(t):
    """Template bbox in Blender axes: (min, size)."""
    lo, hi = t["bbox_min"], t["bbox_max"]
    mn = Vector((lo[0], -hi[2], lo[1]))
    size = Vector((hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]))
    return mn, size


def box_map(src, dst):
    """Matrix that stretches the box of template `src` onto the box of template `dst` (Blender axes)."""
    smin, ssize = bl_box(src)
    dmin, dsize = bl_box(dst)
    ratio = [d / s if s > 1e-6 else 1.0 for d, s in zip(dsize, ssize)]
    return Matrix.Translation(dmin) @ Matrix.Diagonal((ratio[0], ratio[1], ratio[2], 1.0)) @ Matrix.Translation(-smin)


def resolve(template, templates, aliases, models):
    """-> (model name, extra local matrix) or (None, None)."""
    if template.startswith("Debt_SchoolLoan"):
        books = int(round((templates[template]["size"][1] - 0.62) / 0.8))
        name = "Debt_SchoolLoan" if books == 3 else "Debt_SchoolLoan_books%d" % books
        if name in models:
            return name, Matrix.Identity(4)
    if template in models:
        return template, Matrix.Identity(4)
    base = aliases.get(template)
    if base and base in models:
        return base, box_map(templates[base], templates[template])
    return None, None


_ghosts = {}


def ghost_material(mat):
    if mat.name in _ghosts:
        return _ghosts[mat.name]
    g = mat.copy()
    g.name = "GHOST_" + mat.name
    bsdf = g.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Alpha"].default_value = min(bsdf.inputs["Alpha"].default_value, GHOST_ALPHA)
    _ghosts[mat.name] = g
    return g


def build():
    status = load_json("data", "model_status.json")
    objects = load_json("data", "objects.json")
    templates = load_json("data", "templates.json")
    aliases = load_json("data", "plan.json")["aliases"]

    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "blend", "before.blend"))
    models = load_models(status)
    print("models loaded:", len(models))

    world = bpy.data.collections["World"]
    catalog = bpy.data.collections["Catalog"]
    new_cols = {}

    def target(area, category):
        key = ("C_" if area.startswith("Catalog") else "W_") + "new_" + category
        if key not in new_cols:
            new_cols[key] = wo.collection(key, catalog if key.startswith("C_") else world)
        return new_cols[key]

    swapped, kept, instances = 0, [], 0
    report = []
    for o in objects:
        name, extra = resolve(o["template"], templates, aliases, models)
        blk = bpy.data.objects.get(o["key"])
        if name is None:
            kept.append(o["key"])
            continue
        frame = wo.rb_matrix(o["frame"])
        scale = o.get("scale", 1.0)
        place = frame @ Matrix.Diagonal((scale, scale, scale, 1.0)) @ extra
        col = target(o["area"], o["category"])
        for src in models[name]:
            obj = bpy.data.objects.new("NEW_" + o["key"] + "|" + src.name, src.data)
            col.objects.link(obj)
            obj.matrix_world = place @ src.matrix_world
            obj.hide_render = src.hide_render
            if o["mode"] == "ghost":
                for slot in obj.material_slots:
                    slot.link = "OBJECT"
                for i, mat in enumerate(src.data.materials):
                    obj.material_slots[i].material = ghost_material(mat)
            instances += 1
        if blk is not None:
            blk.hide_render = True
            blk.hide_viewport = True
        swapped += 1
        report.append((o["key"], o["template"], name, o["mode"], scale))

    print("swapped %d objects (%d mesh instances); kept blockouts: %d" % (swapped, instances, len(kept)))
    for k in kept:
        print("  kept:", k)
    out = {"swapped": len(report), "kept_blockout": kept,
           "swaps": [{"key": k, "template": t, "model": m, "mode": md, "scale": s} for k, t, m, md, s in report]}
    json.dump(out, open(os.path.join(ROOT, "data", "after_assembly.json"), "w"), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blend", "after.blend"))


if __name__ == "__main__":
    build()
    if "--render" in sys.argv:
        samples = 48
        for a in sys.argv:
            if a.startswith("--samples="):
                samples = int(a.split("=")[1])
        shots.render_world_shots(os.path.join(ROOT, "renders", "after"), samples=samples)

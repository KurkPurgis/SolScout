"""
make_models.py - Phase 3 pipeline for one category: build -> check -> render 3 views -> export FBX -> save.

    bvenv/bin/python tools/blender/make_models.py <category> [template ...] [--no-render] [--no-export]

For every template:
  1. builds the model from the shared kit (tools/blender/models/<category>.py)
  2. checks: triangles vs budget, bounding box vs the original (tolerance 0.15 studs per side),
     palette-only colors, thin parts (warnings from the kit)
  3. renders front 3/4, back 3/4 and eye level with the 5-stud dummy (renders/objects/<template>/)
     and a strip of all three (renders/objects/strips/<template>.png)
  4. exports export/<category>/<name>.fbx (origin = the original object's frame)
  5. saves blend/<category>.blend (after EVERY model) and data/model_status.json
"""

import importlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import kit  # noqa: E402
import review  # noqa: E402
import wo  # noqa: E402

BUDGET = {"props": 1500, "vehicles": 4000, "buildings": 6000, "nature": 1500, "ground": 1500,
          "decoration": 1500, "signs": 1500}
TOLERANCE = 0.15
STATUS_PATH = os.path.join(ROOT, "data", "model_status.json")


def load_status():
    if os.path.exists(STATUS_PATH):
        return json.load(open(STATUS_PATH))
    return {}


def save_status(status):
    json.dump(status, open(STATUS_PATH, "w"), indent=1, sort_keys=True)


def to_jpg(paths, quality=88):
    """PNG renders -> JPG (a tenth of the size, so the repo stays small); returns the new paths."""
    from PIL import Image
    out = []
    for p in paths:
        q = os.path.splitext(p)[0] + ".jpg"
        Image.open(p).convert("RGB").save(q, quality=quality, optimize=True)
        os.remove(p)
        out.append(q)
    return out


def roblox_bounds(objs):
    """Bounding box of Blender objects in Roblox local coordinates (x, y, z)."""
    lo, hi = review.world_bounds(objs)
    # Blender (x, y, z) -> Roblox (x, z, -y)
    rlo = (lo.x, lo.z, -hi.y)
    rhi = (hi.x, hi.z, -lo.y)
    return rlo, rhi


def open_category_blend(category):
    path = os.path.join(ROOT, "blend", category + ".blend")
    if os.path.exists(path):
        bpy.ops.wm.open_mainfile(filepath=path)
    else:
        wo.reset()
        review.studio()
        wo.collection("Models")
        wo.player_dummy(bpy.context.scene.collection, name="PlayerDummy_5studs").hide_render = True
    return path


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    flags = {a for a in args if a.startswith("--")}
    args = [a for a in args if not a.startswith("--")]
    category, names = args[0], args[1:]
    templates = json.load(open(os.path.join(ROOT, "data", "templates.json")))
    module = importlib.import_module("models." + category)
    registry = module.MODELS
    if not names:
        names = list(registry)
    path = open_category_blend(category)
    review.studio()  # (re)apply render settings
    models_col = wo.collection("Models")
    mats = kit.Materials()
    dummy = bpy.data.objects.get("PlayerDummy_5studs")
    status = load_status()

    for name in names:
        spec = registry[name]
        t0 = time.time()
        col_name = "NEW_" + name
        old = bpy.data.collections.get(col_name)
        if old is not None:
            for obj in list(old.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(old)
        col = wo.collection(col_name, models_col)
        m = kit.Model(spec.get("mesh_name", name))
        spec["build"](m)
        objs = m.build(col, mats)
        for obj in objs:
            obj["template"] = name
        tris = m.triangles()
        status = load_status()  # fresh: review verdicts may have been written while this job ran
        entry = status.get(name, {})
        budget = spec.get("budget", BUDGET[category])
        entry.update({"category": category, "triangles": tris, "budget": budget,
                      "warnings": m.warnings[:10], "export_name": spec.get("export", name),
                      "meshes": [o.name for o in objs], "built_at": time.strftime("%Y-%m-%d %H:%M")})
        # bounding box vs the original template
        t = templates.get(spec.get("template", name))
        if t:
            lo, hi = roblox_bounds(objs)
            dev = [lo[i] - t["bbox_min"][i] for i in range(3)] + [hi[i] - t["bbox_max"][i] for i in range(3)]
            entry["bbox_new"] = [[round(x, 3) for x in lo], [round(x, 3) for x in hi]]
            entry["bbox_old"] = [t["bbox_min"], t["bbox_max"]]
            entry["bbox_max_dev"] = round(max(abs(d) for d in dev), 3)
            entry["bbox_ok"] = entry["bbox_max_dev"] <= spec.get("tolerance", TOLERANCE)
            entry["bbox_dev"] = [round(d, 3) for d in dev]
        entry["tris_ok"] = tris <= budget
        print("MODEL %s: %d tris (budget %d), bbox dev %s, warnings %d" % (
            name, tris, budget, entry.get("bbox_dev"), len(m.warnings)))

        # render: only this model visible
        for c in models_col.children:
            c.hide_render = c is not col
        if "--no-render" not in flags:
            out_dir = os.path.join(ROOT, "renders", "objects", name)
            os.makedirs(out_dir, exist_ok=True)
            paths = review.render_views(objs, out_dir, name, dummy)
            strip_dir = os.path.join(ROOT, "renders", "objects", "strips")
            os.makedirs(strip_dir, exist_ok=True)
            review.strip(paths, os.path.join(strip_dir, name + ".png"))
            paths = to_jpg(paths + [os.path.join(strip_dir, name + ".png")])
            entry["renders"] = [os.path.relpath(p, ROOT) for p in paths[:3]]
            entry["strip"] = os.path.relpath(paths[3], ROOT)
        for c in models_col.children:
            c.hide_render = False

        # export
        if "--no-export" not in flags:
            export_dir = os.path.join(ROOT, "export", category)
            os.makedirs(export_dir, exist_ok=True)
            fbx = os.path.join(export_dir, spec.get("export", name) + ".fbx")
            for o in bpy.context.view_layer.objects:
                o.select_set(False)
            for o in objs:
                o.select_set(True)
            bpy.context.view_layer.objects.active = objs[0]
            bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={"MESH"},
                                     apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
                                     use_mesh_modifiers=True, mesh_smooth_type="OFF", use_custom_props=False,
                                     add_leaf_bones=False, bake_anim=False, path_mode="AUTO", embed_textures=False)
            entry["fbx"] = os.path.relpath(fbx, ROOT)
        # a rebuilt model needs a new review (the round counter and notes are kept)
        entry["status"] = "built"
        entry["round"] = entry.get("round", 0)
        status = load_status()
        status[name] = entry
        save_status(status)
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("done %s in %.0fs" % (name, time.time() - t0))


if __name__ == "__main__":
    main()

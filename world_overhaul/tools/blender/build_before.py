"""
build_before.py - the "before" scene: the current world as a blockout, 1 Blender unit = 1 stud.

    bvenv/bin/python tools/blender/build_before.py            (build + save blend/before.blend)
    bvenv/bin/python tools/blender/build_before.py --render   (also render renders/before/*.png)

Every object from data/objects.json becomes ONE Blender object whose origin is the object's frame
(the exact spot a replacement model must drop into). Objects are sorted into collections by category.
The Catalog (things that only appear later in a game) is in its own collection and never in world shots.
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

import wo  # noqa: E402
import shots  # noqa: E402

CATEGORIES = ["buildings", "vehicles", "props", "nature", "ground", "decoration", "signs"]


def load():
    data = os.path.join(ROOT, "data")
    instances = json.load(open(os.path.join(data, "world_instances.json")))
    objects = json.load(open(os.path.join(data, "objects.json")))
    templates = json.load(open(os.path.join(data, "templates.json")))
    return instances, objects, templates


def sign_texts(instances):
    """part id -> list of (face, text, color) for SurfaceGuis with text."""
    by_id = {e["id"]: e for e in instances}
    children = {}
    for e in instances:
        children.setdefault(e["parent"], []).append(e)
    out = {}
    for e in instances:
        if e["class"] != "SurfaceGui":
            continue
        texts = []

        def walk(node):
            for child in children.get(node["id"], []):
                if child["class"] == "TextLabel" and child.get("Text"):
                    texts.append(child)
                walk(child)

        walk(e)
        text = " ".join(t["Text"] for t in texts if t["Text"].isascii())
        text = text.replace("\n", " ").strip()
        if not text:
            continue
        # rich text tags out
        import re
        text = re.sub(r"<[^>]+>", "", text)
        out.setdefault(e["parent"], []).append((e.get("Face", "Front"), text, texts[0].get("TextColor3", [255, 255, 255])))
    return out


def add_sign_text(col, part, face, text, color, name):
    """Approximates the SurfaceGui text as a flat 3D text on the part's face (renders only)."""
    sx, sy, sz = part["Size"]
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.0
    size = min(sy * 0.62, sx / max(1.0, len(text) * 0.62))
    curve.size = max(size, 0.05)
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    mat = wo.roblox_material(color, "Neon" if False else "SmoothPlastic", 0)
    curve.materials.append(mat)
    # local: text faces +Y (= Roblox -Z = the part's Front face)
    local = Matrix.Rotation(math.radians(180), 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")
    offset = sz / 2 + 0.03
    if face == "Back":
        local = Matrix.Rotation(math.radians(180), 4, "Z") @ local
        local.translation = Vector((0, -offset, 0))
    else:
        local.translation = Vector((0, offset, 0))
    obj.matrix_world = wo.rb_matrix(part["CFrame"]) @ local
    return obj


def add_lights(instances):
    by_id = {e["id"]: e for e in instances}
    count = 0
    for e in instances:
        if e["class"] != "PointLight":
            continue
        part = by_id.get(e["parent"])
        if part is None or "Catalog" in part["path"]:
            continue
        data = bpy.data.lights.new("PL_%d" % e["id"], "POINT")
        rng = e.get("Range", 16)
        data.energy = 40.0 * e.get("Brightness", 1) * (rng / 10.0) ** 2
        data.shadow_soft_size = 0.6
        data.color = wo.lin(e.get("Color", [255, 255, 255]))[:3]
        light = bpy.data.objects.new("PL_%d" % e["id"], data)
        wo.collection("Lights").objects.link(light)
        light.location = wo.rb_vec(part["CFrame"][:3])
        count += 1
    return count


def build():
    instances, objects, templates = load()
    by_id = {e["id"]: e for e in instances}
    texts = sign_texts(instances)
    wo.reset()
    wo.setup_render()
    wo.setup_lighting()

    world = wo.collection("World")
    catalog = wo.collection("Catalog")
    cols = {c: wo.collection("W_" + c, world) for c in CATEGORIES}
    ccols = {c: wo.collection("C_" + c, catalog) for c in CATEGORIES}
    text_col = wo.collection("W_signtext", world)
    ctext_col = wo.collection("C_signtext", catalog)

    for o in objects:
        parts = [by_id[i] for i in o["part_ids"]]
        in_catalog = o["area"].startswith("Catalog")
        col = (ccols if in_catalog else cols)[o["category"]]
        obj = wo.blockout_object(o["key"], parts, o["frame"], col)
        obj["template"] = o["template"]
        obj["category"] = o["category"]
        obj["area"] = o["area"]
        for p in parts:
            for face, text, color in texts.get(p["id"], []):
                add_sign_text(ctext_col if in_catalog else text_col, p, face, text, color, "Text_%d" % p["id"])

    n_lights = add_lights(instances)
    dummies = wo.collection("Dummies", world)
    for name, pos, facing in shots.DUMMIES:
        wo.player_dummy(dummies, location=pos, facing=facing, name=name)
    shots.make_cameras()
    print("objects:", len(objects), "lights:", n_lights)
    os.makedirs(os.path.join(ROOT, "blend"), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blend", "before.blend"))


if __name__ == "__main__":
    build()
    if "--render" in sys.argv:
        shots.render_world_shots(os.path.join(ROOT, "renders", "before"))

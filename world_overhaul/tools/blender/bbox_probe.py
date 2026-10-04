"""
bbox_probe.py - prints a model's bounding box vs the original (no Blender objects, no render).

    bvenv/bin/python tools/blender/bbox_probe.py <category> <template> [key=value overrides are not supported]
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy  # noqa: E402,F401
import kit  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
category, name = args[0], args[1]
spec = importlib.import_module("models." + category).MODELS[name]
m = kit.Model(name)
spec["build"](m)
vs = [v for g in m.groups.values() for v in g["verts"]]
# Blender (x, y, z) -> Roblox (x, z, -y)
lo = (min(v[0] for v in vs), min(v[2] for v in vs), -max(v[1] for v in vs))
hi = (max(v[0] for v in vs), max(v[2] for v in vs), -min(v[1] for v in vs))
t = json.load(open(os.path.join(HERE, "..", "..", "data", "templates.json"))).get(spec.get("template", name))
print("new", [round(x, 3) for x in lo], [round(x, 3) for x in hi], "tris", m.triangles())
if t:
    print("old", t["bbox_min"], t["bbox_max"])
    print("dev", [round(lo[i] - t["bbox_min"][i], 3) for i in range(3)] + [round(hi[i] - t["bbox_max"][i], 3) for i in range(3)])

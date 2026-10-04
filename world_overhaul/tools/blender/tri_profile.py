"""
tri_profile.py - which lines of a model's code cost the most triangles.
    bvenv/bin/python tools/blender/tri_profile.py <category> <template>
"""
import collections
import importlib
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy  # noqa: E402,F401

import kit  # noqa: E402

category, name = sys.argv[1], sys.argv[2]
module = importlib.import_module("models." + category)
spec = module.MODELS[name]
costs = collections.Counter()
orig_add = kit.Model._add


def add(self, bm, *a, **k):
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    for frame in inspect.stack()[1:]:
        if "/models/" in frame.filename or frame.filename.endswith("parts.py"):
            if "/models/" in frame.filename:
                costs["%s:%d %s" % (os.path.basename(frame.filename), frame.lineno, frame.code_context[0].strip()[:70])] += tris
                break
    return orig_add(self, bm, *a, **k)


kit.Model._add = add
m = kit.Model(name)
spec["build"](m)
print("total", m.triangles())
for k, v in costs.most_common(15):
    print("%6d  %s" % (v, k))

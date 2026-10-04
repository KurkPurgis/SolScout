"""
check_models.py - fast checks without rendering: builds every model's geometry in memory and lists
coplanar (z-fighting) box faces and thin-part warnings.

    bvenv/bin/python tools/blender/check_models.py [category ...]
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy  # noqa: E402,F401  (loads bmesh)
import kit  # noqa: E402

CATEGORIES = ["buildings", "vehicles", "props", "nature", "ground", "decoration", "signs"]
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
total = 0
count = 0
for category in (args or CATEGORIES):
    module = importlib.import_module("models." + category)
    for name, spec in module.MODELS.items():
        m = kit.Model(spec.get("mesh_name", name))
        spec["build"](m)
        problems = m.coplanar_faces() + m.warnings
        count += 1
        if problems:
            total += len(problems)
            print("%s/%s:" % (category, name))
            for p in problems[:12]:
                print("   ", p)
print("models checked:", count, "problems:", total)

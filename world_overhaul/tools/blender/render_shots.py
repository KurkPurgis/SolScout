"""
render_shots.py - opens a .blend and renders the fixed world shots.

    bvenv/bin/python tools/blender/render_shots.py <file.blend> <out dir> [samples] [shot names...]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy  # noqa: E402

import shots  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
blend, out_dir = args[0], args[1]
samples = int(args[2]) if len(args) > 2 else 48
names = args[3:] or None
bpy.ops.wm.open_mainfile(filepath=blend)
shots.render_world_shots(out_dir, names=names, samples=samples)

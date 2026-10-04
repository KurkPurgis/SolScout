"""
blueprint.py - prints the original parts of a template (what I model against).

    python3 tools/blueprint.py <template> [ctx]

Coordinates are the template's local frame (Roblox: x right, y up, z back, front = -Z), or with "ctx"
the frame of the code that built it (Plots.luau plot base, Themes furnish base, Props builder base...).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from inventory import cf_inv, cf_mul  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, ".."))
t = json.load(open(os.path.join(ROOT, "data", "templates.json")))[sys.argv[1]]
inst = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "data", "world_instances.json")))}
objs = {o["key"]: o for o in json.load(open(os.path.join(ROOT, "data", "objects.json")))}
o = objs[t["canonical"]]
frame = o["frame"]
if len(sys.argv) > 2 and sys.argv[2] == "ctx":
    frame = cf_mul(frame, cf_inv(o["frame_in_ctx"]))
inv = cf_inv(frame)
print("template", t["name"], "size", t["size"], "bbox", t["bbox_min"], t["bbox_max"], "parts", t["parts"])
print("frame_in_ctx", [round(x, 3) for x in o["frame_in_ctx"]])
for pid in o["part_ids"]:
    p = inst[pid]
    local = cf_mul(inv, p["CFrame"])
    m = local[3:]
    rot = ""
    if any(abs(m[i] - (1 if i in (0, 4, 8) else 0)) > 1e-3 for i in range(9)):
        rx = math.degrees(math.atan2(-m[5], m[8]))
        ry = math.degrees(math.asin(max(-1, min(1, m[2]))))
        rz = math.degrees(math.atan2(-m[1], m[0]))
        rot = " rot(%.0f,%.0f,%.0f)" % (rx, ry, rz)
    shape = p.get("Shape", "Block") if p["class"] == "Part" else p["class"]
    print("  %-10s pos(%7.2f %6.2f %7.2f) size(%6.2f %5.2f %6.2f)%s rgb%s %s%s %s" % (
        shape, local[0], local[1], local[2], p["Size"][0], p["Size"][1], p["Size"][2], rot,
        tuple(int(c) for c in p["Color"]), p["Material"],
        " T%.2f" % p["Transparency"] if p.get("Transparency") else "", p["name"] if p["name"] != "Part" else ""))

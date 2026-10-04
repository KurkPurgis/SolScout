"""
write_progress.py - PROGRESS.md from data/model_status.json + data/plan.json (the modelling order).
"""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
status = json.load(open(os.path.join(ROOT, "data", "model_status.json")))
plan = json.load(open(os.path.join(ROOT, "data", "plan.json")))
templates = json.load(open(os.path.join(ROOT, "data", "templates.json")))

lines = ["# Progress", "",
         "If you (or I after a restart) pick this up: read this file and STYLE_GUIDE.md first.",
         "Updated: %s" % time.strftime("%Y-%m-%d %H:%M"), "",
         "## Current step", "", plan.get("current_step", ""), "",
         "## How to continue",
         "",
         "- Build/render/export one category: `/home/user/bvenv/bin/python tools/blender/make_models.py <category> [templates]`",
         "- Look at `renders/objects/strips/<template>.png`, then `python3 tools/set_status.py <template> done|needs_review \"note\"`",
         "- Model code: `tools/blender/models/<category>.py`; kit: `tools/blender/kit.py`, `tools/blender/parts.py`",
         "- Blueprint of the original parts: `python3 tools/blueprint.py <template> [ctx]`",
         "",
         "## Phases", ""]
for phase in plan["phases"]:
    lines.append("- [%s] %s" % ("x" if phase["done"] else " ", phase["name"]))
lines += ["", "## Models (in modelling order: most visible first)", "",
          "| # | template | category | status | triangles | bbox dev | note |", "|---|---|---|---|---|---|---|"]
counts = {}
for i, name in enumerate(plan["order"], 1):
    e = status.get(name, {})
    st = e.get("status", "not_started")
    counts[st] = counts.get(st, 0) + 1
    note = (e.get("notes") or [""])[-1]
    alias = plan.get("aliases", {}).get(name)
    if alias:
        st = "uses " + alias
        counts["alias"] = counts.get("alias", 0) + 1
    lines.append("| %d | %s | %s | %s | %s | %s | %s |" % (
        i, name, templates.get(name, {}).get("category", e.get("category", "")), st,
        e.get("triangles", ""), e.get("bbox_max_dev", ""), note))
lines[lines.index("## Models (in modelling order: most visible first)") + 1:1] = []
summary = ", ".join("%s: %d" % kv for kv in sorted(counts.items()))
lines.insert(lines.index("## Phases"), "## Summary\n\n" + summary + "\n")
open(os.path.join(ROOT, "PROGRESS.md"), "w").write("\n".join(lines) + "\n")
print("PROGRESS.md:", summary)

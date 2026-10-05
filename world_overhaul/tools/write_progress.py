"""
write_progress.py - PROGRESS.md from data/model_status.json + data/plan.json (the modelling order).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
status = json.load(open(os.path.join(ROOT, "data", "model_status.json")))
plan = json.load(open(os.path.join(ROOT, "data", "plan.json")))
templates = json.load(open(os.path.join(ROOT, "data", "templates.json")))
sys.path.insert(0, HERE)
from write_import_plan import alias_model  # noqa: E402

lines = ["# Progress", "",
         "If you (or I after a restart) pick this up: read this file and STYLE_GUIDE.md first.",
         "Updated: %s" % time.strftime("%Y-%m-%d %H:%M"), "",
         "## Current step", "", plan.get("current_step", ""), "",
         "## How to continue",
         "",
         "- Build/render/export one category: `/home/user/bvenv/bin/python tools/blender/make_models.py <category> [templates]`",
         "- Look at `renders/objects/strips/<template>.jpg`, then `python3 tools/set_status.py <template> done|needs_review \"note\"`",
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
    note = e.get("review_note") or (e.get("notes") or [""])[-1]
    alias = plan.get("aliases", {}).get(name)
    if alias:  # a copy of another template (size, book count, mirrored): no model of its own
        st = "uses " + alias_model(name, templates, plan["aliases"])[0]
        counts["alias"] = counts.get("alias", 0) + 1
    else:
        counts[st] = counts.get(st, 0) + 1
    lines.append("| %d | %s | %s | %s | %s | %s | %s |" % (
        i, name, templates.get(name, {}).get("category", e.get("category", "")), st,
        e.get("triangles", ""), e.get("bbox_max_dev", ""), note))
lines[lines.index("## Models (in modelling order: most visible first)") + 1:1] = []
# kit pieces that are not object types of their own (chain links, padlock, School Loan sizes, card cases, 4th kid)
extra = sorted(n for n in status if n not in plan["order"])
lines += ["", "## Extra kit models (pieces and variants the game makes, not object types of their own)", "",
          "| template | category | status | triangles | bbox dev | note |", "|---|---|---|---|---|---|"]
for name in extra:
    e = status[name]
    st = e.get("status", "not_started")
    counts["extra " + st] = counts.get("extra " + st, 0) + 1
    lines.append("| %s | %s | %s | %s | %s | %s |" % (name, e.get("category", ""), st, e.get("triangles", ""),
                                                      e.get("bbox_max_dev", ""), e.get("review_note", "")))
summary = ", ".join("%s: %d" % kv for kv in sorted(counts.items()))
summary += " (%d kit models in all, %d FBX files)" % (len(status), sum(1 for e in status.values() if e.get("fbx")))
lines.insert(lines.index("## Phases"), "## Summary\n\n" + summary + "\n")
open(os.path.join(ROOT, "PROGRESS.md"), "w").write("\n".join(lines) + "\n")
print("PROGRESS.md:", summary)

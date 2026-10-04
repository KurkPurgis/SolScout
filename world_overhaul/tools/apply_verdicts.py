"""
apply_verdicts.py - writes my review verdicts (data/review_verdicts.txt: template|status|note per line) into
data/model_status.json (only for models that are built), then rewrites PROGRESS.md.

    python3 tools/apply_verdicts.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
path = os.path.join(ROOT, "data", "model_status.json")
status = json.load(open(path))
n = 0
for line in open(os.path.join(ROOT, "data", "review_verdicts.txt")):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, verdict, note = (line.split("|", 2) + [""])[:3]
    e = status.get(name)
    if e is None or not e.get("fbx"):
        print("not built, skipped:", name)
        continue
    e["status"] = verdict
    e["review_note"] = note
    e["round"] = max(e.get("round", 0), 1)
    n += 1
json.dump(status, open(path, "w"), indent=1, sort_keys=True)
print("verdicts applied:", n)
subprocess.run([sys.executable, os.path.join(HERE, "write_progress.py")], check=True)

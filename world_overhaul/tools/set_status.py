"""
set_status.py - records my review verdict for a model, then rewrites PROGRESS.md.

    python3 tools/set_status.py <template> <done|needs_review|in_progress|not_started> ["note"]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
path = os.path.join(ROOT, "data", "model_status.json")
status = json.load(open(path)) if os.path.exists(path) else {}
name, verdict = sys.argv[1], sys.argv[2]
note = sys.argv[3] if len(sys.argv) > 3 else ""
entry = status.setdefault(name, {})
entry["status"] = verdict
entry["round"] = entry.get("round", 0) + (1 if verdict in ("done", "needs_review") else 0)
if note:
    entry.setdefault("notes", []).append(note)
json.dump(status, open(path, "w"), indent=1, sort_keys=True)
subprocess.run([sys.executable, os.path.join(HERE, "write_progress.py")], check=True)

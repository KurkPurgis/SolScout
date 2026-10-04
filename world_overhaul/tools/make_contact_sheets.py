"""
make_contact_sheets.py - the report's contact sheets: every model (front 3/4 view), 30 per page.

    /home/user/bvenv/bin/python tools/make_contact_sheets.py
"""
import glob
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
plan = json.load(open(os.path.join(ROOT, "data", "plan.json")))
status = json.load(open(os.path.join(ROOT, "data", "model_status.json")))
names = [n for n in plan["order"] if n in status and status[n].get("renders")]
names += sorted(n for n in status if n not in plan["order"] and status[n].get("renders"))
for old in glob.glob(os.path.join(ROOT, "renders", "contact_sheet_*.jpg")):
    os.remove(old)
per = 30
for page in range((len(names) + per - 1) // per):
    chunk = names[page * per:(page + 1) * per]
    png = os.path.join(ROOT, "renders", "contact_sheet_%d.png" % (page + 1))
    subprocess.run([sys.executable, os.path.join(HERE, "contact_sheet.py"), png, "--cols", "6", "--cell", "330"]
                   + chunk, check=True)
    Image.open(png).convert("RGB").save(png[:-4] + ".jpg", quality=86, optimize=True)
    os.remove(png)
print(len(names), "models on", (len(names) + per - 1) // per, "pages")

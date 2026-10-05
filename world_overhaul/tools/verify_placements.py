"""
verify_placements.py - checks export/placements.json against the world data: for every context instance
(each plaza, each workplace, each auction/podium room, the lobby), the kit models placed by
WorldSkin.context(<key>, base) must be exactly the objects that exist there, at exactly their frames.

    python3 tools/verify_placements.py
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from write_import_plan import LINK_BY_LINK, builder_of  # noqa: E402

objects = json.load(open(os.path.join(ROOT, "data", "objects.json")))
places = json.load(open(os.path.join(ROOT, "export", "placements.json")))


def norm(frame):
    return tuple(round(v, 2) + 0.0 for v in frame)


inst = defaultdict(list)
for o in objects:
    ctx = o["context"]
    if not ctx or ctx in ("Kids", "Debts", "MoneyMakers", "ForSale", "Catalog") or builder_of(o["template"]) \
            or o["template"] in LINK_BY_LINK:
        continue
    key = ctx.split(":")[0] if ctx.startswith(("Collection", "DreamArea")) else ctx
    where = o["key"].split("/")[0]  # e.g. City_2 or City_1.Plots.Plot_Player3 or AuctionRoom_4
    inst[(key, where)].append((o["template"], norm(o["frame_in_ctx"]), round(o.get("scale", 1.0), 3)))

bad = 0
for (key, where), items in sorted(inst.items()):
    want = sorted((p["template"], norm(p["frame"]), round(p["scale"], 3)) for p in places.get(key, []))
    got = sorted(items)

    def same(a, b):
        return a[0] == b[0] and abs(a[2] - b[2]) < 1e-3 and all(abs(x - y) < 0.011 for x, y in zip(a[1], b[1]))
    pool = list(want)
    for g in got:
        hit = next((w for w in pool if same(g, w)), None)
        if hit is not None:
            pool.remove(hit)
    if pool or len(want) != len(got):
        bad += 1
        missing = [x for x in got if x not in want]
        extra = [x for x in want if x not in got]
        print("MISMATCH %s @ %s: %d objects, %d placements; not placed: %s; placed but absent: %s" % (
            key, where, len(got), len(want), missing[:3], extra[:3]))
print("context instances checked:", len(inst), "mismatches:", bad)

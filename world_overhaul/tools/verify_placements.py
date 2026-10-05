"""
verify_placements.py - checks export/placements.json against the world data: for every context instance
(each plaza, each workplace, each auction/podium room, the lobby, each showcase and dream pedestal), the kit
models that WorldSkin.context(<key>, base) places must be exactly the objects that exist there.

    python3 tools/verify_placements.py

Independent of how the generator computed the frames: the base CFrame of every instance comes straight from
the world dump (the CFrame its builder function was called with), and each placement is checked in WORLD space:
  * the kit template is the object's own model (or the model its alias uses),
  * base * placement frame has the object's rotation, and
  * the kit's box (data/model_status.json bbox_new) placed there covers the object's own box (world AABB).
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from inventory import cf_mul, cf_point  # noqa: E402
from write_import_plan import LINK_BY_LINK, builder_of  # noqa: E402

SKIPPED_CONTEXTS = ("Kids", "Debts", "MoneyMakers", "ForSale", "Catalog")


def load(*p):
    return json.load(open(os.path.join(ROOT, *p)))


def world_box(frame, lo, hi, scale=1.0):
    pts = [cf_point(frame, (x * scale, y * scale, z * scale)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
           for z in (lo[2], hi[2])]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def verify(places, quiet=False):
    """-> {"instances": Counter(kind -> count), "mismatches": n, "checked": n}"""
    objects = load("data", "objects.json")
    status = load("data", "model_status.json")
    aliases = load("data", "plan.json")["aliases"]
    parts = {e["id"]: e for e in load("data", "world_instances.json")}

    inst = defaultdict(list)  # (context, seq) -> objects
    bases = {}
    for o in objects:
        ctx = o["context"]
        if not ctx or ctx in SKIPPED_CONTEXTS or builder_of(o["template"]) or o["template"] in LINK_BY_LINK:
            continue
        group = None
        for g in parts[o["part_ids"][0]].get("groups") or []:
            if g["label"] == ctx:
                group = g
        inst[(ctx, group["seq"])].append(o)
        bases[(ctx, group["seq"])] = group["base"]

    bad = 0
    kinds = Counter()
    for (ctx, seq), items in sorted(inst.items()):
        kinds[ctx.split(":")[0]] += 1
        base = bases[(ctx, seq)]
        pool = [dict(p, world=cf_mul(base, p["frame"])) for p in places.get(ctx, [])]
        problems = []
        for o in items:
            want = o["template"] if o["template"] in status else aliases.get(o["template"])
            tol = max(0.2, status.get(want, {}).get("bbox_max_dev", 0) + 0.05)
            olo, ohi = world_box(o["frame"], o["bbox_min"], o["bbox_max"])
            hit = None
            for p in pool:
                if p["template"] != want or abs(p["scale"] - o.get("scale", 1.0)) > 1e-3:
                    continue
                if any(abs(a - b) > 1e-3 for a, b in zip(p["world"][3:], o["frame"][3:])):
                    continue  # another rotation
                klo, khi = world_box(p["world"], *status[want]["bbox_new"], scale=p["scale"])
                if all(abs(a - b) <= tol for a, b in zip(klo + khi, olo + ohi)):
                    hit = p
                    break
            if hit is None:
                problems.append("not placed: %s %s" % (o["key"], o["template"]))
            else:
                pool.remove(hit)
        problems += ["placed but absent: %s at %s" % (p["template"], [round(v, 2) for v in p["world"][:3]])
                     for p in pool]
        if problems:
            bad += 1
            if not quiet:
                print("MISMATCH %s #%s: %s" % (ctx, seq, "; ".join(problems[:4])))
    return {"instances": kinds, "checked": len(inst), "mismatches": bad}


if __name__ == "__main__":
    result = verify(load("export", "placements.json"))
    print("context instances checked:", result["checked"], dict(result["instances"]), "mismatches:",
          result["mismatches"])
    sys.exit(1 if result["mismatches"] else 0)

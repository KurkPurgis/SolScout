"""
inventory.py - turns data/world_instances.json (every instance the game code built, see
tools/luau/dump_world.luau) into logical OBJECTS and TEMPLATES.

- An OBJECT is one thing a player sees (a tree, a workplace building, a bench...).
  Parts are grouped by the builder call that made them (group stack recorded by the mock) and
  by the source line (file:line) of the statement that made them.
- A TEMPLATE is one model to build: all objects with the same shape and colors share one.
  (8 trees -> 1 template "Tree"; 8 workplaces -> 9 templates, one per theme...)

Writes:
  data/objects.json    every object instance: template, frame (Roblox CFrame), bbox, parts
  data/templates.json  every template: size, colors, instances, script references
"""

import collections
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")

PART_CLASSES = {"Part", "WedgePart", "CornerWedgePart", "SpawnLocation", "MeshPart", "TrussPart"}
HELPER = re.compile(
    r"^(Props\.luau:\d+\((part|box|cylinder|ball|sign|floatingLabel)\)"
    r"|ModelKit\.luau:\d+\((part|box|wedge|cornerWedge|cylinder|cylinderY|cylinderZ|ball|bar|railing|palm)\)"
    r"|dump_world\.luau:\d+\(\w+\))$"
)
OBJECT_LABELS = ("Maker:", "Debt:", "Dream:", "Kid", "Tree", "Palm", "Car")
CONTEXT_LABELS = ("Workplace:", "Furnish:", "Collection", "DreamArea", "Plaza", "AuctionRoom", "PodiumRoom",
                  "Lobby", "Kids", "Debts", "MoneyMakers", "ForSale", "NameSign")

# ----------------------------------------------------------------------------
# small CFrame math (Roblox convention: 12 numbers x y z r00 r01 r02 r10 ... r22, row-major)
# ----------------------------------------------------------------------------


def cf_mul(a, b):
    ax, ay, az, *am = a
    bx, by, bz, *bm = b
    m = [0.0] * 9
    for i in range(3):
        for j in range(3):
            m[i * 3 + j] = sum(am[i * 3 + k] * bm[k * 3 + j] for k in range(3))
    x = am[0] * bx + am[1] * by + am[2] * bz + ax
    y = am[3] * bx + am[4] * by + am[5] * bz + ay
    z = am[6] * bx + am[7] * by + am[8] * bz + az
    return [x, y, z] + m


def cf_inv(a):
    ax, ay, az, *m = a
    t = [m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]]
    x = -(t[0] * ax + t[1] * ay + t[2] * az)
    y = -(t[3] * ax + t[4] * ay + t[5] * az)
    z = -(t[6] * ax + t[7] * ay + t[8] * az)
    return [x, y, z] + t


def cf_point(a, p):
    ax, ay, az, *m = a
    return (m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + ax,
            m[3] * p[0] + m[4] * p[1] + m[5] * p[2] + ay,
            m[6] * p[0] + m[7] * p[1] + m[8] * p[2] + az)


def cf_pos(x, y, z):
    return [x, y, z, 1, 0, 0, 0, 1, 0, 0, 0, 1]


def cf_yaw(angle):
    c, s = math.cos(angle), math.sin(angle)
    return [0, 0, 0, c, 0, s, 0, 1, 0, -s, 0, c]


def yaw_of(cf):
    """Rotation around Y of a CFrame (Roblox: LookVector = -Z column)."""
    m = cf[3:]
    look = (-m[2], -m[5], -m[8])
    return math.atan2(-look[0], -look[2])


def yaw_only(cf):
    return cf_yaw(yaw_of(cf))


def corners(part):
    sx, sy, sz = part["Size"]
    cf = part["CFrame"]
    return [cf_point(cf, (x * sx / 2, y * sy / 2, z * sz / 2)) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]


def box_in(parts, frame):
    inv = cf_inv(frame)
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for part in parts:
        for p in corners(part):
            q = cf_point(inv, p)
            for i in range(3):
                lo[i] = min(lo[i], q[i])
                hi[i] = max(hi[i], q[i])
    return lo, hi


# ----------------------------------------------------------------------------
# Rules for parts that are not inside an object builder (walls, floors, furniture...)
# (context, set of source lines) -> (type, category, split, frame)
#   split: "one" = all these parts are one object, "cluster" = split into touching groups,
#          "each" = every part is its own object
#   frame: "base" = the context's base CFrame (plot / room / city / hall origin)
#          "bottom" = base rotation, origin at the bottom center of the object
#          "bottom_mirror" = like bottom, turned 180 degrees on the +X side (left/right pairs share one model)
#          "part" = the first part's rotation, origin at the bottom center
#          "inward" = faces the context center (city walls), origin at the bottom center
# ----------------------------------------------------------------------------

L = "Lobby.luau"
P = "Plots.luau"
T = "Themes.luau"
RULES = [
    # lobby hall
    ("Lobby", L, {332}, "Lobby_Floor", "ground", "one", "base"),
    ("Lobby", L, {333, 334}, "Lobby_Carpet", "ground", "one", "base"),
    ("Lobby", L, {345, 346}, "Lobby_Walls", "buildings", "one", "base"),
    ("Lobby", L, {351}, "Lobby_TitleSign", "signs", "one", "bottom"),
    ("Lobby", L, {358, 359, 360}, "Lobby_Pillar", "decoration", "cluster", "bottom_mirror"),
    ("Lobby", L, {368}, "Lobby_Window", "buildings", "each", "bottom_mirror"),
    ("Lobby", L, {373, 374, 375}, "Lobby_Bench", "props", "cluster", "bottom_mirror"),
    ("Lobby", L, {386}, "Lobby_PottedPalm", "nature", "cluster", "bottom_mirror"),
    ("Lobby", L, {393, 394, 395, 396, 397, 398}, "Lobby_Trophy", "props", "one", "bottom"),
    ("Lobby", L, {406}, "Lobby_Spawn", "ground", "one", "bottom"),
    ("Lobby", L, {420, 421, 426, 427, 429, 430, 432, 433}, "Lobby_RoomBooth", "buildings", "cluster", "bottom"),
    # city plaza (one per room)
    ("Plaza", "Plaza.luau", {35}, "City_Ground", "ground", "one", "base"),
    ("Plaza", "Plaza.luau", {43, 44}, "City_Wall", "decoration", "cluster", "inward"),
    ("Plaza", "Plaza.luau", {52}, "Plaza_Disc", "ground", "one", "base"),
    ("Plaza", "Plaza.luau", {58}, "Plaza_Path", "ground", "each", "part"),
    ("Plaza", "Plaza.luau", {69, 70, 71, 72}, "Plaza_Fountain", "decoration", "one", "base"),
    # auction room (one per room)
    ("AuctionRoom", "AuctionRoom.luau", {44, 45, 46, 47, 48, 49}, "AuctionRoom_Shell", "buildings", "one", "base"),
    ("AuctionRoom", "AuctionRoom.luau", {53}, "AuctionRoom_Lamp", "decoration", "each", "bottom"),
    ("AuctionRoom", "AuctionRoom.luau", {63, 64}, "AuctionRoom_Stage", "props", "one", "bottom"),
    ("AuctionRoom", "AuctionRoom.luau", {71}, "AuctionRoom_TitleSign", "signs", "one", "bottom"),
    ("AuctionRoom", "AuctionRoom.luau", {73}, "AuctionRoom_InfoBoard", "signs", "one", "bottom"),
    ("AuctionRoom", "AuctionRoom.luau", {80}, "AuctionRoom_BidderDesk", "props", "each", "bottom"),
    ("AuctionRoom", "AuctionRoom.luau", {81}, "AuctionRoom_BidderPad", "ground", "each", "bottom"),
    # podium room (one per room)
    ("PodiumRoom", "PodiumRoom.luau", {66, 67}, "PodiumRoom_Shell", "buildings", "one", "base"),
    ("PodiumRoom", "PodiumRoom.luau", {69}, "PodiumRoom_LightStrip", "decoration", "each", "bottom"),
    ("PodiumRoom", "PodiumRoom.luau", {72}, "PodiumRoom_TitleSign", "signs", "one", "bottom"),
    ("PodiumRoom", "PodiumRoom.luau", {79, 80}, "PodiumRoom_Block", "props", "cluster", "bottom"),
    ("PodiumRoom", "PodiumRoom.luau", {90}, "PodiumRoom_Board", "signs", "one", "part"),
    # workplace (every plot; colors come from the job theme)
    ("Workplace", P, {130, 132}, "Workplace_Yard", "ground", "one", "base"),
    ("Workplace", P, {131, 135, 136, 137, 138, 143, 144, 147, 148, 153, 154, 155, 162, 166, 167, 169},
     "Workplace_Building", "buildings", "one", "base"),
    ("Workplace", P, {176}, "Workplace_MakerLot", "ground", "each", "part"),
    ("Workplace", P, {183, 186}, "Workplace_Fence", "decoration", "cluster", "bottom_mirror"),
    ("Workplace", P, {189, 190}, "Workplace_LampPost", "decoration", "cluster", "bottom"),
    ("Workplace", P, {200, 202}, "Workplace_FlowerBox", "decoration", "cluster", "bottom"),
    ("Workplace", P, {207, 209}, "Workplace_Sandbox", "props", "one", "bottom"),
    ("Workplace", P, {218}, "Workplace_DebtPad", "ground", "one", "bottom"),
    ("Workplace", P, {214, 215, 216}, "FastTrack_Gate", "decoration", "one", "bottom"),
    # furniture per theme
    ("Furnish:PIZZERIA", T, {54, 55, 58}, "Pizzeria_Counter", "props", "one", "bottom"),
    ("Furnish:PIZZERIA", T, {56, 57}, "Pizzeria_Oven", "props", "one", "bottom"),
    ("Furnish:BUS DEPOT", T, {71, 73, 77}, "Depot_Bus", "vehicles", "one", "bottom"),
    ("Furnish:HOSPITAL", T, {41, 42, 43}, "HospitalBed", "props", "cluster", "bottom"),
    ("Furnish:HOSPITAL", T, {94, 95}, "Hospital_WallCross", "decoration", "one", "bottom"),
    ("Furnish:CLINIC", T, {41, 42, 43}, "HospitalBed", "props", "cluster", "bottom"),
    ("Furnish:CLINIC", T, {31, 36, 37}, "Computer", "props", "cluster", "bottom"),
    ("Furnish:CLINIC", T, {109}, "Clinic_Chair", "props", "one", "bottom"),
    ("Furnish:CLINIC", T, {110}, "Clinic_Cabinet", "props", "one", "bottom"),
    ("Furnish:CLINIC", T, {111, 112}, "Clinic_WallScreen", "decoration", "one", "bottom"),
    ("Furnish:SCHOOL", T, {124}, "School_Blackboard", "decoration", "one", "bottom"),
    ("Furnish:SCHOOL", T, {31}, "School_TeacherDesk", "props", "one", "bottom"),
    ("Furnish:SCHOOL", T, {128}, "School_StudentDesk", "props", "each", "bottom"),
    ("Furnish:POLICE", T, {144, 145}, "Police_Car", "vehicles", "one", "bottom"),
    ("Furnish:POLICE", T, {31, 36, 37}, "Computer", "props", "cluster", "bottom"),
    ("Furnish:OFFICE", T, {31, 36, 37}, "Computer", "props", "cluster", "bottom"),
    ("Furnish:OFFICE", T, {162, 163}, "Office_Screen", "decoration", "one", "bottom"),
    ("Furnish:GARAGE", T, {175, 176}, "Garage_CarLift", "vehicles", "one", "bottom"),
    ("Furnish:GARAGE", T, {178}, "Garage_ToolBoard", "decoration", "one", "bottom"),
    ("Furnish:GARAGE", T, {180}, "Garage_TireStack", "props", "one", "bottom"),
    ("Furnish:FAST TRACK", T, {202, 203}, "Lux_Sofa", "props", "cluster", "bottom"),
    ("Furnish:FAST TRACK", T, {205}, "Lux_GlassTable", "props", "one", "bottom"),
    ("Furnish:FAST TRACK", T, {207, 208, 209}, "Lux_Safe", "props", "one", "bottom"),
    ("Furnish:FAST TRACK", T, {211, 212}, "Lux_Piano", "props", "one", "bottom"),
    ("Furnish:FAST TRACK", T, {214, 219}, "Lux_Chandelier", "decoration", "one", "bottom"),
    # dynamic things in the yard
    ("Collection", P, {556, 557}, "Collection_Showcase", "props", "one", "bottom"),
    ("DreamArea", P, {490, 491}, "Dream_Pedestal", "props", "one", "bottom"),
    ("DreamArea", P, {460, 461, 462, 466, 467, 469, 471}, "Dream_Chains", "props", "one", "bottom"),
]

# Category of things made by object builders
BUILDER_CATEGORY = {
    "Tree": "nature", "Kid": "props",
}
MAKER_CATEGORY = {
    "Lemonade Stand": "props", "Vending Machine": "props", "Apartment": "buildings", "Car Wash": "buildings",
    "Food Truck": "vehicles", "Toy Shop": "buildings", "Mini Golf": "props", "House to Rent": "buildings",
    "Pizza Restaurant": "buildings", "Coffee Shop": "buildings", "Bowling Alley": "buildings", "Hotel": "buildings",
    "Game Studio": "buildings", "Shopping Mall": "buildings", "Apartment Building": "buildings",
    "Theme Park": "props", "PokeBlox Card": "props", "Rare PokeBlox Card": "props",
    "Shiny PokeBlox Card": "props", "Gold Coin": "props", "Gold Bar": "props", "Gold Treasure Chest": "props",
    "Unknown Maker": "props",
}
DREAM_CATEGORY = {"Supercar": "vehicles", "Yacht": "vehicles", "Private Jet": "vehicles",
                  "Beach Villa": "buildings", "Private Island": "nature",
                  "BeachVilla": "buildings", "PrivateIsland": "nature", "PrivateJet": "vehicles"}


def slug(text):
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", text) if w)


def is_object_label(label):
    return label in ("Kid", "Tree", "Palm", "Car") or label.startswith(("Maker:", "Debt:", "Dream:"))


def main():
    instances = json.load(open(os.path.join(DATA, "world_instances.json")))
    by_id = {e["id"]: e for e in instances}

    def ancestors(e):
        out = []
        node = by_id.get(e["parent"])
        while node:
            out.append(node)
            node = by_id.get(node["parent"])
        return out

    parts = []
    for e in instances:
        if e["class"] not in PART_CLASSES:
            continue
        e["visible"] = e.get("Transparency", 0) < 0.999
        chain = e.get("chain") or []
        sites = [f for f in chain if not HELPER.match(f)]
        e["site"] = re.sub(r"\(.*\)$", "", sites[0]) if sites else ""
        # also remember every frame, so rules can match helper calls like bed()/computer()
        e["frames"] = [re.sub(r"\(.*\)$", "", f) for f in chain]
        e["labels"] = e.get("groups") or []
        segs = e["path"].split(".")
        e["area"] = segs[1]
        parts.append(e)

    objects = {}  # key -> object dict
    unassigned = []

    def add(key, part, **info):
        obj = objects.get(key)
        if obj is None:
            obj = dict(key=key, parts=[], **info)
            objects[key] = obj
        obj["parts"].append(part)

    for part in parts:
        if not part["visible"]:
            continue  # invisible barriers, label anchors, buy buttons: stay as they are
        labels = part["labels"]
        obj_label = next((g for g in labels if is_object_label(g["label"])), None)
        ctx_label = None
        for g in labels:
            if g["label"].startswith(CONTEXT_LABELS):
                ctx_label = g  # innermost wins
        area = part["area"]
        area_key = area
        segs = part["path"].split(".")
        if "Plots" in segs:
            area_key = ".".join(segs[1:4])  # City_1.Plots.Plot_Player3
        elif area == "Catalog":
            area_key = ".".join(segs[1:3])
        ctx_name = ctx_label["label"] if ctx_label else ""
        ctx_base = ctx_label["base"] if ctx_label and ctx_label.get("base") else cf_pos(0, 0, 0)

        # --- catalog dreams (built directly, no builder group): use the dream model
        if area == "Catalog" and ".Dreams." in part["path"]:
            model = next((a for a in reversed(ancestors(part)) if a["class"] == "Model"), None)
            otype = "Dream_" + slug(model["name"])
            add("%s/%s" % (area_key, otype), part, type=otype, category=DREAM_CATEGORY.get(model["name"], "props"),
                area=area_key, frame=model["Pivot"], mode="normal", roblox_name=model["name"], context="Catalog")
            continue

        # --- things made by an object builder (makers, debts, dreams, kids, trees)
        if obj_label and not (obj_label["label"] in ("Car", "Palm") and ctx_name.startswith(("Furnish:", "Lobby"))):
            label = obj_label["label"]
            kind, _, name = label.partition(":")
            if kind == "Maker":
                otype, cat = "Maker_" + slug(name), MAKER_CATEGORY.get(name, "props")
            elif kind == "Debt":
                otype, cat = "Debt_" + slug(name), "props"
            elif kind == "Dream":
                otype, cat = "Dream_" + slug(name), DREAM_CATEGORY.get(name, "props")
            else:
                otype, cat = label, BUILDER_CATEGORY.get(label, "props")
            mode = {"ForSale": "ghost", "Collection": "mini", "DreamArea": "dream"}.get(ctx_name, "normal")
            add("%s/%s#%d" % (area_key, otype, obj_label["seq"]), part, type=otype, category=cat, area=area_key,
                frame=obj_label["base"], mode=mode, roblox_name=name or label, context=ctx_name)
            continue

        # --- rules by context + source line
        ctx_kind = ctx_name.split(":")[0] if not ctx_name.startswith("Furnish:") else ctx_name
        if ctx_kind == "Workplace":
            ctx_kind = "Workplace"
        matched = False
        for rule_ctx, rule_file, lines, otype, cat, split, frame in RULES:
            if rule_ctx != ctx_kind:
                continue
            hit = False
            for f in part["frames"]:
                fname, _, line = f.partition(":")
                if fname == rule_file and line.isdigit() and int(line) in lines:
                    # only the frame that is directly inside the context function counts
                    hit = True
                    break
            if not hit:
                continue
            theme = ctx_name.split(":", 1)[1] if ":" in ctx_name else ""
            if ctx_kind == "Workplace" and theme == "":
                theme = ""
            group_key = "%s/%s/%s" % (area_key, otype, ctx_label["seq"] if ctx_label else 0)
            add(group_key, part, type=otype, category=cat, area=area_key, split=split, frame_mode=frame,
                ctx_base=ctx_base, theme=theme, context=ctx_name, mode="normal", roblox_name=otype)
            matched = True
            break
        if not matched:
            # Car inside furniture, palms in the lobby: attach by rule on the context
            if obj_label and obj_label["label"] == "Car" and ctx_name == "Furnish:POLICE":
                add("%s/Police_Car/%s" % (area_key, ctx_label["seq"]), part, type="Police_Car", category="vehicles",
                    area=area_key, split="one", frame_mode="bottom", ctx_base=ctx_base, theme="POLICE",
                    context=ctx_name, mode="normal", roblox_name="Police_Car")
            elif obj_label and obj_label["label"] == "Car" and ctx_name == "Furnish:GARAGE":
                add("%s/Garage_CarLift/%s" % (area_key, ctx_label["seq"]), part, type="Garage_CarLift",
                    category="vehicles", area=area_key, split="one", frame_mode="bottom", ctx_base=ctx_base,
                    theme="GARAGE", context=ctx_name, mode="normal", roblox_name="Garage_CarLift")
            elif obj_label and obj_label["label"] == "Palm" and ctx_name == "Lobby":
                add("%s/Lobby_PottedPalm/%s" % (area_key, ctx_label["seq"]), part, type="Lobby_PottedPalm", category="nature",
                    area=area_key, split="cluster", frame_mode="bottom_mirror", ctx_base=ctx_base, theme="",
                    context=ctx_name, mode="normal", roblox_name="Lobby_PottedPalm")
            elif part["name"] == "Baseplate":
                add("Baseplate", part, type="Baseplate", category="ground", area="Workspace", split="one",
                    frame_mode="base", ctx_base=cf_pos(0, 0, 0), theme="", context="", mode="normal",
                    roblox_name="Baseplate")
            else:
                unassigned.append(part)

    # --- split clusters / each, compute frames and boxes
    final = []
    for obj in objects.values():
        split = obj.get("split", "one")
        groups = [obj["parts"]]
        if split == "each":
            groups = [[p] for p in obj["parts"]]
        elif split == "cluster":
            groups = cluster(obj["parts"], gap=0.6, frame=obj.get("ctx_base"))
        for index, group in enumerate(groups):
            item = {k: v for k, v in obj.items() if k not in ("parts",)}
            item["parts"] = group
            if len(groups) > 1:
                item["key"] = "%s.%d" % (obj["key"], index + 1)
            final.append(item)

    for obj in final:
        set_frame(obj)

    # --- templates: same type + same local shape and colors = same template (with a small tolerance)
    by_type = collections.defaultdict(list)
    for obj in final:
        by_type[obj["type"]].append(obj)
    templates = {}
    order = {"normal": 0, "ghost": 1, "mini": 2, "dream": 3}
    for otype, objs in by_type.items():
        objs.sort(key=lambda o: (order[o["mode"]], 0 if o["area"].startswith("Catalog") else 1, o["key"]))
        variants = []  # list of (canonical, [objects])
        for obj in objs:
            for canonical, members in variants:
                if same_shape(obj, canonical):
                    members.append(obj)
                    break
            else:
                variants.append((obj, [obj]))
        themes = [sorted({o.get("theme", "") for o in members}) for _, members in variants]
        by_theme = len(variants) > 1 and all(len(t) == 1 and t[0] for t in themes) and \
            len({t[0] for t in themes}) == len(variants)
        for index, (canonical, members) in enumerate(variants):
            name = otype
            if by_theme:
                name += "_" + slug(themes[index][0])
            elif index > 0:
                name += "_v%d" % (index + 1)
            for o in members:
                o["template"] = name
            templates[name] = make_template(name, canonical, members)
            for o in members:
                if o["mode"] in ("mini", "dream") and canonical["mode"] not in ("mini", "dream"):
                    k = o["scale"]
                    bc_world = cf_point(o["frame_cf"], bottom_center(o))
                    bc_c = bottom_center(canonical)
                    rot = list(o["frame_cf"])
                    rot[0:3] = [0, 0, 0]
                    off = cf_point(rot, (bc_c[0] * k, bc_c[1] * k, bc_c[2] * k))
                    rot[0:3] = [bc_world[i] - off[i] for i in range(3)]
                    o["frame_cf"] = rot
                    o["bbox"] = box_in(o["parts"], rot)

    out_objects = []
    for o in final:
        out_objects.append({
            "key": o["key"], "template": o["template"], "type": o["type"], "category": o["category"],
            "area": o["area"], "context": o.get("context", ""), "mode": o["mode"], "theme": o.get("theme", ""),
            "roblox_name": o.get("roblox_name", ""),
            "frame": [round(x, 5) for x in o["frame_cf"]], "scale": round(o.get("scale", 1.0), 5),
            "frame_in_ctx": [round(x, 5) for x in cf_mul(cf_inv(o.get("ctx_base") or o["frame_cf"]), o["frame_cf"])],
            "bbox_min": [round(x, 4) for x in o["bbox"][0]], "bbox_max": [round(x, 4) for x in o["bbox"][1]],
            "part_ids": [p["id"] for p in o["parts"]], "part_count": len(o["parts"]),
        })
    json.dump(out_objects, open(os.path.join(DATA, "objects.json"), "w"), indent=1)
    json.dump(templates, open(os.path.join(DATA, "templates.json"), "w"), indent=1)
    print("objects:", len(out_objects), "templates:", len(templates), "unassigned visible parts:", len(unassigned))
    for p in unassigned[:40]:
        print("  UNASSIGNED", p["path"], p["site"], [g["label"] for g in p["labels"]])


def cluster(parts, gap, frame=None):
    """Splits parts into groups that touch each other (boxes in the context frame, grown by `gap`)."""
    inv = cf_inv(yaw_only(frame)) if frame else cf_pos(0, 0, 0)
    boxes = []
    for p in parts:
        cs = [cf_point(inv, c) for c in corners(p)]
        lo = [min(c[i] for c in cs) - gap for i in range(3)]
        hi = [max(c[i] for c in cs) + gap for i in range(3)]
        boxes.append((lo, hi))
    parent = list(range(len(parts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a, b = boxes[i], boxes[j]
            if all(a[0][k] <= b[1][k] and b[0][k] <= a[1][k] for k in range(3)):
                parent[find(i)] = find(j)
    groups = collections.defaultdict(list)
    for i, p in enumerate(parts):
        groups[find(i)].append(p)
    out = list(groups.values())
    out.sort(key=lambda g: (round(cf_center(g)[0], 1), round(cf_center(g)[2], 1)))
    return out


def cf_center(group):
    lo, hi = box_in(group, cf_pos(0, 0, 0))
    return [(lo[i] + hi[i]) / 2 for i in range(3)]


def set_frame(obj):
    parts = obj["parts"]
    if "frame" in obj and obj["frame"] is not None:
        frame = list(obj["frame"])
        lo, hi = box_in(parts, frame)
        obj["frame_cf"] = frame
        obj["bbox"] = (lo, hi)
        if obj["mode"] in ("mini", "dream"):
            obj["scale"] = None  # filled in by make_template from the canonical instance
        return
    mode = obj.get("frame_mode", "base")
    base = obj.get("ctx_base") or cf_pos(0, 0, 0)
    if mode == "base":
        frame = list(base)
    else:
        if mode == "part":
            rot = yaw_only(parts[0]["CFrame"])
        elif mode == "inward":
            center_world = cf_center(parts)
            to_center = (base[0] - center_world[0], base[2] - center_world[2])
            # local -Z (front) looks at the city center
            rot = cf_yaw(math.atan2(-to_center[0], -to_center[1]))
        else:
            rot = yaw_only(base)
        rot[0:3] = [0, 0, 0]
        lo, hi = box_in(parts, rot)
        center = [(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2]
        frame = cf_mul(rot, cf_pos(*center))
        if mode == "bottom_mirror":
            local = cf_point(cf_inv(base), cf_point(frame, (0, 0, 0)))
            if local[0] > 0.01:
                frame = cf_mul(frame, cf_yaw(math.pi))
    lo, hi = box_in(parts, frame)
    obj["frame_cf"] = frame
    obj["bbox"] = (lo, hi)


def local_parts(obj):
    """Parts in the object's own frame: (class, shape, center, half-extents, wedge rotation, color).
    Half-extents are rotation-free for boxes/cylinders/balls, so a box turned 180 degrees still matches."""
    frame = obj["frame_cf"]
    inv = cf_inv(frame)
    out = []
    for p in obj["parts"]:
        local = cf_mul(inv, p["CFrame"])
        m = local[3:]
        size = p["Size"]
        ext = [sum(abs(m[i * 3 + j]) * size[j] for j in range(3)) / 2 for i in range(3)]
        rot = tuple(m) if p["class"] in ("WedgePart", "CornerWedgePart") else ()
        out.append((p["class"], p.get("Shape", ""), local[:3], ext, rot, p["Color"]))
    if obj["mode"] in ("mini", "dream"):
        # scaled copies were moved after scaling: measure from the bottom center instead of the frame origin
        lo, hi = obj["bbox"]
        bc = ((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2)
        out = [(c, sh, [ce[i] - bc[i] for i in range(3)], e, r, col) for c, sh, ce, e, r, col in out]
    return out


def bottom_center(obj):
    lo, hi = obj["bbox"]
    return ((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2)


def obj_extent(obj):
    lo, hi = obj["bbox"]
    return max(hi[i] - lo[i] for i in range(3)) or 1.0


def same_shape(a, b):
    """True when a and b are the same model (b is a template's canonical object).
    Ghost (FOR SALE) copies ignore colors; mini/dream-display copies are compared after scaling."""
    if len(a["parts"]) != len(b["parts"]):
        return False
    scaled = a["mode"] in ("mini", "dream") or b["mode"] in ("mini", "dream")
    pa = local_parts(a)
    if scaled and b["mode"] not in ("mini", "dream"):
        bb = dict(b)
        bb["mode"] = "dream"  # compare both from their bottom centers
        pb = local_parts(bb)
    else:
        pb = local_parts(b)
    factor = obj_extent(b) / obj_extent(a) if scaled else 1.0
    use_color = a["mode"] != "ghost" and b["mode"] != "ghost"
    tol = 0.06 * max(1.0, factor) if not scaled else 0.006 * obj_extent(b)
    used = [False] * len(pb)
    for cls, shape, center, ext, rot, color in sorted(pa, key=lambda r: -r[3][0] * r[3][1] * r[3][2]):
        best, best_d = None, None
        for j, (cls2, shape2, center2, ext2, rot2, color2) in enumerate(pb):
            if used[j] or cls != cls2 or shape != shape2 or len(rot) != len(rot2):
                continue
            if any(abs(rot[i] - rot2[i]) > 0.05 for i in range(len(rot))):
                continue
            d = max(max(abs(center[i] * factor - center2[i]) for i in range(3)),
                    max(abs(ext[i] * factor - ext2[i]) for i in range(3)))
            if d > tol:
                continue
            if use_color and any(abs(color[i] - color2[i]) > 6 for i in range(3)):
                continue
            if best_d is None or d < best_d:
                best, best_d = j, d
        if best is None:
            return False
        used[best] = True
    return True


def signature(obj):
    frame = obj["frame_cf"]
    inv = cf_inv(frame)
    rows = []
    lo, hi = obj["bbox"]
    size = max(hi[i] - lo[i] for i in range(3)) or 1.0
    # mini (collection) and dream-display instances are scaled copies: compare normalized
    norm = size if obj["mode"] in ("mini", "dream") else 1.0
    for p in obj["parts"]:
        local = cf_mul(inv, p["CFrame"])
        pos = [round(local[i] / norm, 2 if norm != 1 else 1) for i in range(3)]
        rot = [round(x, 1) + 0.0 for x in local[3:]]
        sz = [round(s / norm, 2 if norm != 1 else 1) for s in p["Size"]]
        color = tuple(int(round(c / 8)) for c in p["Color"]) if obj["mode"] != "ghost" else ()
        rows.append((p["class"], p.get("Shape", ""), tuple(sz), tuple(pos), tuple(rot), color))
    rows.sort()
    return hash(tuple(rows))


def make_template(name, canonical, objs):
    lo, hi = canonical["bbox"]
    size = [hi[i] - lo[i] for i in range(3)]
    for o in objs:
        olo, ohi = o["bbox"]
        osize = max(ohi[i] - olo[i] for i in range(3))
        o["scale"] = osize / max(size) if max(size) > 0 else 1.0
    colors = collections.Counter()
    materials = collections.Counter()
    for p in canonical["parts"]:
        colors[tuple(int(c) for c in p["Color"])] += 1
        materials[p["Material"]] += 1
    areas = collections.Counter(o["area"].split(".")[0] for o in objs)
    return {
        "name": name, "type": canonical["type"], "category": canonical["category"],
        "theme": canonical.get("theme", ""), "canonical": canonical["key"],
        "size": [round(s, 3) for s in size],
        "bbox_min": [round(x, 3) for x in lo], "bbox_max": [round(x, 3) for x in hi],
        "parts": len(canonical["parts"]), "instances": len(objs),
        "areas": dict(areas), "modes": dict(collections.Counter(o["mode"] for o in objs)),
        "colors": [list(c) + [n] for c, n in colors.most_common()],
        "materials": dict(materials), "roblox_name": canonical.get("roblox_name", ""),
        "canonical_part_ids": [p["id"] for p in canonical["parts"]],
        "frame_in_ctx": [round(x, 5) for x in cf_mul(cf_inv(canonical.get("ctx_base") or canonical["frame_cf"]),
                                                     canonical["frame_cf"])],
        "context": canonical.get("context", ""),
    }


if __name__ == "__main__":
    main()

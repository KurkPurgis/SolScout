"""
write_inventory.py - writes INVENTORY.md and data/objects.csv from data/*.json.
    python3 tools/write_inventory.py
"""

import collections
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
CATEGORIES = ["buildings", "vehicles", "props", "nature", "ground", "decoration", "signs"]

DESCRIPTIONS = {
    "Workplace_Building": "The job building at the back of each plot: walls, roof, pillars, striped awning, big sign with lamps",
    "Workplace_Yard": "Yard floor in front of the building + stone path to the door",
    "Workplace_MakerLot": "Sand-colored lot beside the plot where a Money Maker stands (8 per plot)",
    "Workplace_Fence": "Low white fence along the front of the plot (one each side of the entrance)",
    "Workplace_LampPost": "Lamp post at the plot entrance (glowing ball + PointLight)",
    "Workplace_FlowerBox": "Wooden flower box with 3 flower balls by the building",
    "Workplace_Sandbox": "Sandbox where the kids play",
    "Workplace_DebtPad": "Grey pad where the debt models stand",
    "FastTrack_Gate": "Golden gate with the FREE! sign (Fast Track version only)",
    "Plaza_Fountain": "Fountain in the middle of the plaza", "Plaza_Disc": "Round stone plaza",
    "Plaza_Path": "Stone path from the plaza to a workplace", "City_Ground": "Grass ground of a whole city",
    "City_Wall": "Low stone city wall with a cap (+ invisible tall barrier)", "Tree": "Round tree between workplaces",
    "Lobby_Floor": "Marble floor of the lobby hall", "Lobby_Carpet": "Red carpets in the lobby",
    "Lobby_Walls": "Lobby hall walls with gold trim", "Lobby_TitleSign": "ESCAPE THE 9 TO 5 sign on the back wall",
    "Lobby_Pillar": "Marble pillar with gold cap and a glowing lamp", "Lobby_Window": "Glass window in the lobby side wall",
    "Lobby_Bench": "Wooden bench in the lobby", "Lobby_PottedPalm": "Potted palm near the spawn",
    "Lobby_Trophy": "Golden trophy on a marble pedestal", "Lobby_Spawn": "Spawn pad",
    "Lobby_RoomBooth": "Room door: arch with glowing portal, colored platform (join trigger) and sign",
    "AuctionRoom_Shell": "Closed auction room: floor, walls, roof", "AuctionRoom_Lamp": "Ceiling lamp panel",
    "AuctionRoom_Stage": "Stage with a glowing gold edge", "AuctionRoom_TitleSign": "AUCTION sign",
    "AuctionRoom_InfoBoard": "Big info board (bids are written here)", "AuctionRoom_BidderDesk": "Bidder desk (glows gold for the top bidder)",
    "AuctionRoom_BidderPad": "Floor pad where a bidder stands", "PodiumRoom_Shell": "Podium room floor and dark backdrop",
    "PodiumRoom_LightStrip": "Glowing vertical light strip on the backdrop", "PodiumRoom_TitleSign": "Big title (X WINS!)",
    "PodiumRoom_Block": "1st/2nd/3rd podium blocks with name signs", "PodiumRoom_Board": "'Also played' board",
    "Pizzeria_Counter": "Counter with green top and a pizza", "Pizzeria_Oven": "Brick pizza oven with fire",
    "Depot_Bus": "Yellow city bus in the depot", "HospitalBed": "Hospital bed with pillow and blanket",
    "Hospital_WallCross": "Red cross on the back wall", "Computer": "Desk with a computer screen",
    "Clinic_Chair": "Dark stool", "Clinic_Cabinet": "Tall white medicine cabinet", "Clinic_WallScreen": "Heart monitor screen on the wall",
    "School_Blackboard": "Green blackboard", "School_TeacherDesk": "Teacher's desk", "School_StudentDesk": "Student desk",
    "Police_Car": "White police car with red/blue lights", "Office_Screen": "Big presentation screen",
    "Garage_CarLift": "Red car up on a lift", "Garage_ToolBoard": "Tool board on the wall", "Garage_TireStack": "Stack of tires",
    "Lux_Sofa": "White sofa", "Lux_GlassTable": "Glass coffee table", "Lux_Safe": "Golden safe ($$$)", "Lux_Piano": "Black piano",
    "Lux_Chandelier": "Glowing chandelier", "Collection_Showcase": "Wooden COLLECTION table for investments",
    "Dream_Pedestal": "Marble pedestal for the dream (Fast Track)", "Dream_Chains": "Chains and padlock around the locked dream",
    "Kid": "A player's kid (hops around)", "Baseplate": "Grass baseplate under the lobby",
    "Debt_CreditCard": "Debt: giant credit card on a stand", "Debt_CarLoan": "Debt: grey car with LOAN sign",
    "Debt_SchoolLoan": "Debt: stack of books with a graduation cap", "Debt_BankLoan": "Debt: bank vault",
    "Debt_OtherDebt": "Debt (unknown kind): grey tied-up box",
    "Dream_Supercar": "Dream: red supercar", "Dream_Yacht": "Dream: yacht", "Dream_BeachVilla": "Dream: beach villa",
    "Dream_PrivateJet": "Dream: private jet", "Dream_PrivateIsland": "Dream: private island",
}


def hexcolor(rgb):
    return "#%02X%02X%02X" % tuple(int(round(c)) for c in rgb[:3])


def main():
    instances = {e["id"]: e for e in json.load(open(os.path.join(DATA, "world_instances.json")))}
    objects = json.load(open(os.path.join(DATA, "objects.json")))
    templates = json.load(open(os.path.join(DATA, "templates.json")))
    refs = json.load(open(os.path.join(DATA, "script_refs.json")))
    scripted = set(refs["script_referenced"])
    geometry = set(refs["geometry_locked"])

    def describe(t):
        if t["type"].startswith("Maker_"):
            return "Money Maker / investment: " + t["roblox_name"]
        return DESCRIPTIONS.get(t["type"], t["type"])

    world_objs = [o for o in objects if not o["area"].startswith("Catalog")]
    cat_objs = [o for o in objects if o["area"].startswith("Catalog")]

    def main_part(o):
        parts = [instances[i] for i in o["part_ids"]]
        return max(parts, key=lambda p: p["Size"][0] * p["Size"][1] * p["Size"][2])

    def path_of(o):
        p = instances[o["part_ids"][0]]
        return p["path"].rsplit(".", 1)[0]

    lines = []
    w = lines.append
    w("# Inventory - the world of Rags to Riches (Escape the 9 to 5) as it is now")
    w("")
    w("**How this was made.** There is no place file with the world in it: the place only has a Baseplate, and")
    w("everything else is built by Luau code when the server starts (`src/server/Lobby.luau`, `src/server/World/*`).")
    w("So I ran that exact code (unchanged) on a small copy of the Roblox engine (`tools/luau/roblox_mock.luau`) and")
    w("recorded every Part it created, together with the line of code that created it (see DECISIONS.md #2-#3).")
    w("")
    w("What exists:")
    w("- **At server start** (always there): the lobby hall, and 4 identical cities (one per room, 700 studs apart),")
    w("  each with its plaza, an auction room (400 studs up) and a podium room (250 studs up).")
    w("- **During a game**: each player gets a workplace (plot) in the ring around the plaza, with their kids, debts,")
    w("  Money Makers, a FOR SALE model, a showcase for investments and their floating dream. To inventory these I filled")
    w("  city 1 with 8 players in the middle of a game (one per job) - this is what players look at most.")
    w("- **Later in a game** (Catalog, not a real place): the Fast Track workplace after escaping, the locked/won dream,")
    w("  every Money Maker and investment, every debt at small and big size, and the dreams at full size.")
    w("")
    w("![before - city](renders/before/overview_city.png)")
    w("")
    # summary
    w("## Summary")
    w("")
    w("| | count |")
    w("|---|---|")
    n_parts = sum(1 for e in instances.values() if e["class"] in ("Part", "WedgePart", "SpawnLocation"))
    w("| Parts built by the code (all areas, incl. catalog) | %d |" % n_parts)
    w("| Visible objects in the world (lobby + 4 cities + rooms, city 1 in mid-game) | %d |" % len(world_objs))
    w("| Extra objects in the catalog (appear later in a game) | %d |" % len(cat_objs))
    w("| Different models needed (templates; color/size variants counted separately) | %d |" % len(templates))
    w("| Different object types | %d |" % len({t['type'] for t in templates.values()}))
    w("| SCRIPT-REFERENCED object types | %d |" % len(scripted))
    w("")
    w("| category | object types | objects in world | objects in catalog |")
    w("|---|---|---|---|")
    for cat in CATEGORIES:
        types = {t["type"] for t in templates.values() if t["category"] == cat}
        w("| %s | %d | %d | %d |" % (cat, len(types), sum(1 for o in world_objs if o["category"] == cat),
                                     sum(1 for o in cat_objs if o["category"] == cat)))
    w("")
    w("## Hierarchy (Workspace)")
    w("")
    w("```")
    w("Workspace")
    w("├── Baseplate                         (512 x 20 x 512 grass; scripts raycast it by name)")
    w("├── Lobby            [tag Area]       hall, room booths, trophy, palms, benches, spawn")
    w("│   └── Decor                         4 potted palms (Model)")
    w("├── City_1 .. City_4 [tag Area]       one city per room, x = 700, 1400, 2100, 2800")
    w("│   ├── Plots")
    w("│   │   └── Plot_<player> (Model)     one per player, in a ring (radius 115) around the plaza")
    w("│   │       ├── Workplace             building, yard, lots, fence, lamps, flowers, sandbox, furniture")
    w("│   │       ├── Kids                  Model 'Kid' x0-4 (tag Kid)")
    w("│   │       ├── Debts                 Model '<debt name>' + 'Pay' prompt")
    w("│   │       ├── MoneyMakers           Model '<maker name>' on the 8 lots (stacked when full)")
    w("│   │       ├── ForSale               see-through Model '<maker name>' + invisible buy button (prompt)")
    w("│   │       ├── Dream                 floating dream Model (tag Spin) / pedestal + chains on the Fast Track")
    w("│   │       └── Collection            showcase table + mini investments")
    w("│   └── Plaza                         ground, wall, plaza, paths, trees, fountain")
    w("├── AuctionRoom_1 .. _4 [tag Area]   room, stage (+ folder Item), 8 bidder desks, signs")
    w("└── PodiumRoom_1 .. _4  [tag Area]   floor, backdrop, light strips, 3 podium blocks, board")
    w("```")
    w("")
    # template tables
    w("## Every object type, by category")
    w("")
    w("Size = width x height x depth in studs (the player is 5 studs tall). `SCRIPT` = SCRIPT-REFERENCED (names and")
    w("hierarchy must stay identical). `GEOM` = code places things on it or measures it (heights/bounding box must stay).")
    w("Instances: W = in the world (all 4 cities counted), C = catalog only. Variants are the same model in another color or size.")
    w("")
    by_type = collections.defaultdict(list)
    for name, t in templates.items():
        by_type[t["type"]].append((name, t))
    for cat in CATEGORIES:
        w("### %s" % cat.title())
        w("")
        w("| type | what it is | size (studs) | parts | instances | variants | main colors | materials | refs |")
        w("|---|---|---|---|---|---|---|---|---|")
        for ttype in sorted(by_type):
            group = by_type[ttype]
            if group[0][1]["category"] != cat:
                continue
            group.sort(key=lambda nt: nt[0])
            t0 = next((t for n, t in group if n == ttype), group[0][1])
            inst = [o for o in objects if o["type"] == ttype]
            wn = sum(1 for o in inst if not o["area"].startswith("Catalog"))
            cn = len(inst) - wn
            size = " x ".join("%g" % round(s, 1) for s in t0["size"])
            colors = " ".join("`%s`" % hexcolor(c) for c in t0["colors"][:4])
            mats = ", ".join(sorted(t0["materials"]))
            flags = " ".join(f for f, on in (("SCRIPT", ttype in scripted), ("GEOM", ttype in geometry)) if on)
            w("| %s | %s | %s | %d | W %d / C %d | %d | %s | %s | %s |" % (
                ttype, describe(t0), size, t0["parts"], wn, cn, len(group), colors, mats, flags))
        w("")
    # script refs
    w("## Script references (Phase 1, step 2)")
    w("")
    w("I searched `src/` for every instance name in the world and for every way the code touches a world object")
    w("after building it (tags, attributes, prompts, Touched triggers, bounding boxes, pivots, kept references).")
    w("Evidence lines are real `file:line` from the game code (`python3 tools/scriptrefs.py <src>` re-checks them).")
    w("")
    w("**Things that are true for every object:** each area folder (`Lobby`, `City_N`, `AuctionRoom_N`, `PodiumRoom_N`)")
    w("is tagged `Area`, and the client moves the whole folder out of Workspace when you are not in that area")
    w("(`src/client/AreaVisibility.luau`). New models must stay inside the same folder as the old parts.")
    w("")
    done = set()
    groups = collections.OrderedDict()
    for ttype, rs in sorted(refs["by_type"].items()):
        for r in rs:
            if r["kind"] == "context":
                continue
            groups.setdefault((r["kind"], r["why"], tuple(r["evidence"])), []).append(ttype)
    for kind in ("name", "geometry"):
        w("### %s" % ("SCRIPT-REFERENCED (names / tags / prompts / triggers / kept references)" if kind == "name"
                       else "Geometry the code depends on (heights, bounding boxes)"))
        w("")
        for (k, why, evidence), types in groups.items():
            if k != kind:
                continue
            w("- **%s** - %s" % (", ".join(types), why))
            for ev in evidence[:4]:
                w("  - `%s`" % ev)
        w("")
    w("### Name search")
    w("")
    w("Names found as strings in `src/` (`\"Name\"`):")
    w("")
    for name, hits in sorted(refs["name_search"].items()):
        if hits:
            w("- `%s`: %s" % (name, ", ".join(hits[:4]) + (" ..." if len(hits) > 4 else "")))
    w("")
    w("Note: the treasure chest lid is named `Lid` but no script uses that name. Money Maker, debt and dream names")
    w("are the keys of `Config.Deals` / `Config.Jobs` / `Config.Dreams`: the code picks the model by that name.")
    w("")
    # invisible
    w("## Invisible parts (kept as they are, not remodelled)")
    w("")
    inv = collections.Counter()
    for e in instances.values():
        if e["class"] in ("Part",) and e.get("Transparency", 0) >= 0.999 and not e["path"].startswith("Workspace.Catalog"):
            what = "invisible wall (BarrierHeight 150)" if e["Size"][1] >= 100 else (
                "buy button (FOR SALE prompt)" if e["Size"] == [4, 4, 4] else "label anchor (BillboardGui)")
            inv[(e["path"].split(".")[1].rstrip("0123456789").rstrip("_"), what)] += 1
    w("| area | what | count |")
    w("|---|---|---|")
    for (area, what), n in sorted(inv.items()):
        w("| %s | %s | %d |" % (area, what, n))
    w("")
    # full list
    w("## Every visible object (full list)")
    w("")
    w("Position = the object's origin (the spot a new model drops into) in Roblox world studs; the same list is in")
    w("`data/objects.csv` and, with every part id, in `data/objects.json`.")
    w("")
    w("<details><summary>%d objects (click to open)</summary>" % len(objects))
    w("")
    w("| object | template | path | category | size | position | main color | material | parts |")
    w("|---|---|---|---|---|---|---|---|---|")
    rows = []
    for o in objects:
        mp = main_part(o)
        size = [o["bbox_max"][i] - o["bbox_min"][i] for i in range(3)]
        row = {
            "object": o["key"], "template": o["template"], "path": path_of(o), "category": o["category"],
            "size": " x ".join("%g" % round(s, 1) for s in size),
            "position": ", ".join("%g" % round(x, 1) for x in o["frame"][:3]),
            "main_color": hexcolor(mp["Color"]), "material": mp["Material"], "parts": o["part_count"],
            "mode": o["mode"],
        }
        rows.append(row)
        w("| %s | %s | %s | %s | %s | %s | `%s` | %s | %d |" % (
            row["object"], row["template"], row["path"], row["category"], row["size"], row["position"],
            row["main_color"], row["material"], row["parts"]))
    w("")
    w("</details>")
    w("")
    open(os.path.join(ROOT, "INVENTORY.md"), "w").write("\n".join(lines))
    with open(os.path.join(DATA, "objects.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("INVENTORY.md written:", len(lines), "lines")


if __name__ == "__main__":
    main()

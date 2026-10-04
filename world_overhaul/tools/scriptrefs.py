"""
scriptrefs.py - which objects do scripts depend on? (Phase 1, step 2)

Two passes over the game's src/ folder (read only):
1. Name search: every Roblox instance name in the world (folders, models, named parts) is searched as a
   string in src/. A hit means code may look it up by name.
2. Known dependencies: patterns for every way the code touches a world object after building it
   (tags, attributes, prompts, Touched, bounding boxes, pivots, stored references that get recolored...).
   Each pattern is searched in src/ so the evidence below always has the real file:line.

Writes data/script_refs.json: template type -> list of {why, evidence: ["file:line: code"]}
    python3 tools/scriptrefs.py <game src dir>
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

# (kind, template types this applies to (prefix match), why, [(file, regex), ...])
# kind: "name"     = looked up by name/tag/attribute, holds a prompt/trigger, or kept and changed later
#                    -> SCRIPT-REFERENCED: names and hierarchy must stay identical
#       "geometry" = code puts things on it / measures it -> heights and bounding box must stay
#       "context"  = only lives inside an area folder (true for everything in that area)
DEPENDENCIES = [
    ("name", ["Maker_"], "Built by NAME: Props.moneyMaker looks up the builder by the deal name and names the Model after it.",
     [("server/World/Props.luau", r"local builder = makerBuilders\[name\]"),
      ("server/World/Props.luau", r"model.Name = name")]),
    ("geometry", ["Maker_"], "Its BOUNDING BOX decides how high the next Money Maker is stacked and where the label floats.",
     [("server/World/Plots.luau", r"self.slotTops\[slotIndex\] = box.Position.Y"),
      ("server/World/Plots.luau", r"local cframe, size = model:GetBoundingBox\(\)")]),
    ("geometry", ["Maker_"], "FOR SALE copies are made see-through by Props.makeGhost (every BasePart: Transparency, ForceField, no collision).",
     [("server/World/Props.luau", r"item.Material = Enum.Material.ForceField"),
      ("server/World/Plots.luau", r"Props.makeGhost\(model\)")]),
    ("geometry", ["Maker_Gold", "Maker_PokeBlox", "Maker_RarePokeBlox", "Maker_ShinyPokeBlox"],
     "Investments are also shrunk to 40% (ScaleTo) and put on the COLLECTION table.",
     [("server/World/Plots.luau", r"model:ScaleTo\(0.4\)")]),
    ("name", ["Maker_", "Debt_"], "The tutorial arrow finds the player's plot by name and points at the first Model in its ForSale/Debts folder (bounding box).",
     [("client/Tutorial.luau", r'workspace:FindFirstChild\("Plot_" \.\. player.Name, true\)'),
      ("client/Tutorial.luau", r"local box, size = item:GetBoundingBox\(\)")]),
    ("geometry", ["Maker_PokeBlox", "Maker_RarePokeBlox", "Maker_ShinyPokeBlox"],
     "The case color (COMMON/RARE/EPIC/LEGENDARY) is chosen at runtime from the card's value.",
     [("server/World/Props.luau", r"local case = Props.cardCase\(value\)")]),
    ("name", ["Debt_"], "Built by NAME (debt name = Model name); size grows with the amount (scale factor in code).",
     [("server/World/Props.luau", r"local builder = debtBuilders\[debtName\]"),
      ("server/World/Props.luau", r"model.Name = debtName")]),
    ("name", ["Debt_"], "A 'Pay $1,000' ProximityPrompt is parented to its MAIN PART (needs a BasePart to hold it).",
     [("server/World/Plots.luau", r'self:addPrompt\(main, "Pay "')]),
    ("name", ["Kid"], "Model named 'Kid' with tag 'Kid' and a PrimaryPart; the client makes it hop with GetPivot/PivotTo.",
     [("server/World/Props.luau", r'CollectionService:AddTag\(model, "Kid"\)'),
      ("server/World/Props.luau", r"model.PrimaryPart = body"),
      ("client/WorldFx.luau", r"kids\[model\] = \{ base = model:GetPivot\(\)")]),
    ("name", ["Dream_Supercar", "Dream_Yacht", "Dream_BeachVilla", "Dream_PrivateJet", "Dream_PrivateIsland"], "Built by NAME (DreamModels), scaled with ScaleTo from its bounding box, pivot = PrimaryPart at the bottom center.",
     [("server/World/Props.luau", r"local builder = DreamModels\[dreamName\]"),
      ("server/World/Props.luau", r"model:ScaleTo\(displaySize / math.max\(size.X, size.Z\)\)"),
      ("shared/Models/ModelKit.luau", r"primary.PivotOffset = primary.CFrame:Inverse\(\)")]),
    ("name", ["Dream_Supercar", "Dream_Yacht", "Dream_BeachVilla", "Dream_PrivateJet", "Dream_PrivateIsland"], "Tag 'Spin': the client spins the floating dream (PivotTo every frame).",
     [("server/World/Props.luau", r'CollectionService:AddTag\(model, "Spin"\)'),
      ("client/WorldFx.luau", r"spinners\[model\] = model:GetPivot\(\)")]),
    ("name", ["Dream_Supercar", "Dream_Yacht", "Dream_BeachVilla", "Dream_PrivateJet", "Dream_PrivateIsland"], "Every part's Transparency is changed to make the dream glow in as you get closer (attribute BaseTransparency).",
     [("server/World/Props.luau", r'item:SetAttribute\("BaseTransparency"'),
      ("server/World/Plots.luau", r"item.Transparency = own \+ \(1 - own\)")]),
    ("geometry", ["Dream_Chains"] + ["Dream_Supercar", "Dream_Yacht", "Dream_BeachVilla", "Dream_PrivateJet", "Dream_PrivateIsland"], "Chains and padlock are generated around the dream's bounding box.",
     [("server/World/Plots.luau", r"local function addChains")]),
    ("geometry", ["Dream_Pedestal"], "The dream is placed at height 1.8 on it: the pedestal top must stay at 1.8 studs.",
     [("server/World/Plots.luau", r"self.base \* CFrame.new\(0, 1.8, -9\)")]),
    ("geometry", ["Collection_Showcase"], "Investments are placed ON the table top (2.6 studs): table height must stay.",
     [("server/World/Plots.luau", r"local tableTop = SHOWCASE.Y \+ 2.6")]),
    ("name", ["Workplace_"], "Lives in folder 'Workplace' of Model 'Plot_<player>'; the folder is cleared and rebuilt as the Fast Track version on escape.",
     [("server/World/Plots.luau", r'self.workplaceFolder = newFolder\(model, "Workplace"\)'),
      ("server/World/Plots.luau", r"self:buildWorkplace\(Themes.luxury\)")]),
    ("geometry", ["Workplace_Yard", "Workplace_Building"], "Players are teleported onto the yard (stand spot) and the turn camera looks at the building: floor heights must stay.",
     [("server/World/Plots.luau", r"return self.base \* CFrame.new\(0, 4, -18\)"),
      ("server/World/Plots.luau", r"local eye = \(self.base \* CFrame.new\(0, 28, -58\)\)")]),
    ("name", ["Lobby_RoomBooth"], "The glowing platform is a TOUCH TRIGGER: walking onto it joins the room (keep its size and position).",
     [("server/Lobby.luau", r"platform.Touched:Connect")]),
    ("name", ["Lobby_Spawn"], "SpawnLocation: players appear here (class must stay SpawnLocation).",
     [("server/Lobby.luau", r'Instance.new\("SpawnLocation"\)')]),
    ("context", ["Lobby_", "City_", "Plaza_", "Tree", "Workplace_", "AuctionRoom_", "PodiumRoom_", "Baseplate"],
     "The area folders (Lobby, City_N, AuctionRoom_N, PodiumRoom_N) are tagged 'Area' and moved in/out of Workspace by the client: models must stay inside their area folder.",
     [("server/World/Props.luau", r'CollectionService:AddTag\(folder, "Area"\)'),
      ("client/AreaVisibility.luau", r'CollectionService:GetTagged\("Area"\)')]),
    ("context", ["Lobby_Walls", "City_Wall"], "An invisible tall barrier part sits inside the wall (kept as is).",
     [("server/Lobby.luau", r"Config.World.BarrierHeight, size.Z\), C.White, \{ Transparency = 1"),
      ("server/World/Plaza.luau", r"world.BarrierHeight, size.Z\), C.White")]),
    ("name", ["AuctionRoom_BidderDesk"], "Stored in self.podiums: its Color and Material change (gold Neon) for the top bidder.",
     [("server/World/AuctionRoom.luau", r"self.podiums\[index\] = Props.box"),
      ("server/World/AuctionRoom.luau", r"podium.Material = if isTop")]),
    ("name", ["AuctionRoom_InfoBoard"], "Its SurfaceGui TextLabel is found and its text changes during the auction.",
     [("server/World/AuctionRoom.luau", r"self.infoLabel = \(info:FindFirstChildOfClass\(\"SurfaceGui\"\)")]),
    ("geometry", ["AuctionRoom_Stage"], "The item for sale is put on the stage at height 3: the stage top must stay at 3 studs.",
     [("server/World/AuctionRoom.luau", r"self.base \* CFrame.new\(0, 3, STAGE_Z\)")]),
    ("name", ["PodiumRoom_TitleSign"], "Its SurfaceGui TextLabel shows 'X WINS!' / 'FINAL RESULTS'.",
     [("server/World/PodiumRoom.luau", r"self.title = labelOf\(title\)")]),
    ("name", ["PodiumRoom_Block"], "Front sign text is set per rank; winners stand on top (height + 3): block heights must stay.",
     [("server/World/PodiumRoom.luau", r"self.blockLabels\[rank\] = label"),
      ("server/World/PodiumRoom.luau", r"local spot = self.base \* CFrame.new\(block.x, block.height \+ 3, PODIUM_Z\)")]),
    ("name", ["PodiumRoom_Board"], "Shown/hidden with Transparency and filled with a SurfaceGui list of players.",
     [("server/World/PodiumRoom.luau", r"self.board.Transparency = if #standings > 3")]),
    ("name", ["Baseplate"], "Props.groundY raycasts against Workspace.Baseplate by name to find the ground height.",
     [("server/World/Props.luau", r'workspace:FindFirstChild\("Baseplate"\)')]),
]

# Instance names that exist in the world (besides model/maker/debt/dream names from templates)
EXTRA_NAMES = ["Lobby", "Decor", "Plots", "Plaza", "Workplace", "Kids", "Debts", "MoneyMakers", "ForSale", "Dream",
               "Collection", "Item", "Baseplate", "Lid", "Kid", "Remotes"]


def find(src, rel, pattern):
    path = os.path.join(src, rel)
    out = []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            if re.search(pattern, line):
                out.append("src/%s:%d: %s" % (rel, number, line.strip()[:120]))
    return out


def main():
    src = sys.argv[1]
    templates = json.load(open(os.path.join(ROOT, "data", "templates.json")))
    files = []
    for base, _, names in os.walk(src):
        for n in names:
            if n.endswith(".luau"):
                files.append(os.path.relpath(os.path.join(base, n), src))
    files.sort()
    texts = {f: open(os.path.join(src, f), encoding="utf-8").read().splitlines() for f in files}

    refs = {}
    missing = []
    for kind, prefixes, why, patterns in DEPENDENCIES:
        evidence = []
        for rel, pattern in patterns:
            hits = find(src, rel, pattern)
            if not hits:
                missing.append((rel, pattern))
            evidence += hits
        for name, t in templates.items():
            ttype = t["type"]
            if any(ttype == p or ttype.startswith(p) for p in prefixes):
                refs.setdefault(ttype, [])
                if not any(r["why"] == why for r in refs[ttype]):
                    refs[ttype].append({"kind": kind, "why": why, "evidence": evidence})

    # name search
    names = set(EXTRA_NAMES)
    for t in templates.values():
        if t.get("roblox_name"):
            names.add(t["roblox_name"])
    name_hits = {}
    for name in sorted(names):
        hits = []
        for rel, lines in texts.items():
            for number, line in enumerate(lines, 1):
                if '"%s"' % name in line:
                    hits.append("src/%s:%d" % (rel, number))
        name_hits[name] = hits

    script_referenced = sorted(t for t, rs in refs.items() if any(r["kind"] == "name" for r in rs))
    geometry = sorted(t for t, rs in refs.items() if any(r["kind"] == "geometry" for r in rs))
    out = {"script_referenced": script_referenced, "geometry_locked": geometry, "by_type": refs,
           "name_search": name_hits, "patterns_not_found": missing}
    json.dump(out, open(os.path.join(ROOT, "data", "script_refs.json"), "w"), indent=1)
    print("SCRIPT-REFERENCED types:", len(script_referenced), script_referenced)
    print("geometry-locked types:", len(geometry))
    print("patterns not found:", missing)


if __name__ == "__main__":
    main()

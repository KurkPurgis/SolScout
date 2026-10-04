"""
write_import_plan.py - writes IMPORT_PLAN.md and the placement data the swap needs.

    python3 tools/write_import_plan.py

Outputs:
  IMPORT_PLAN.md                         the exact swap procedure (NOT executed)
  export/placements.json                 every placement of every kit model, relative to its builder's base CFrame
  export/roblox/WorldSkinPlacements.luau the same as a Luau module (copy into the game when you do the swap)
  export/roblox/WorldSkin.luau           the swap module (copy into the game when you do the swap)
"""

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from inventory import RULES  # noqa: E402

CANONICAL_AREA = {"Lobby": "Lobby", "Plaza": "City_1", "AuctionRoom": "AuctionRoom_1", "PodiumRoom": "PodiumRoom_1"}
# objects made by a builder function: the swap happens right after that function builds them
BUILDER = [
    ("Kid", "Props.kid (Props.luau:220)", "after the parts are made, before `return model`"),
    ("Debt_", "Props.debtModel (Props.luau:325)", "after `main = ...`, before `model.Parent = parent`"),
    ("Maker_", "Props.moneyMaker (Props.luau:583)", "after the builder ran, before `model.Parent = parent`"),
    ("Dream_Supercar", "Props.dream (Props.luau:604)", "right after `builder.build()`, before `GetBoundingBox`"),
    ("Dream_Yacht", "Props.dream (Props.luau:604)", "right after `builder.build()`, before `GetBoundingBox`"),
    ("Dream_PrivateJet", "Props.dream (Props.luau:604)", "right after `builder.build()`, before `GetBoundingBox`"),
    ("Dream_BeachVilla", "Props.dream (Props.luau:604)", "right after `builder.build()`, before `GetBoundingBox`"),
    ("Dream_PrivateIsland", "Props.dream (Props.luau:604)", "right after `builder.build()`, before `GetBoundingBox`"),
    ("Tree", "Props.tree (Props.luau:352)", "after the parts are made"),
]
CONTEXT_HOOK = {
    "Lobby": ("Lobby.luau `buildHall()` (line 316)", "at the end of `buildHall()`", "the hall origin CFrame"),
    "Plaza": ("Plaza.new (Plaza.luau:21)", "at the end of `Plaza.new`", "the city base CFrame"),
    "AuctionRoom": ("AuctionRoom.new (AuctionRoom.luau:30)", "at the end of `AuctionRoom.new`", "`self.base`"),
    "PodiumRoom": ("PodiumRoom.new (PodiumRoom.luau:55)", "at the end of `PodiumRoom.new`", "`self.base`"),
    "Workplace": ("Plots:buildWorkplace (Plots.luau:122)", "at the end of `buildWorkplace`", "`self.base`"),
    "Furnish": ("Themes furniture (called from Plots:buildWorkplace)", "at the end of `buildWorkplace`",
                "`self.base`"),
    "Collection": ("Plots:syncCollection (Plots.luau:535)", "after the showcase table is made", "`self.base`"),
    "DreamArea": ("Plots:syncDream / addChains (Plots.luau:447-520)", "after the pedestal / chains are made",
                  "`self.base`"),
}


def load(*p):
    return json.load(open(os.path.join(ROOT, *p)))


def builder_of(template):
    for prefix, where, when in BUILDER:
        if template.startswith(prefix):
            return where, when
    return None


def source_of(template_type):
    out = []
    for ctx, f, lines, typ, *_ in RULES:
        if typ == template_type:
            out.append("%s:%s" % (f, ",".join(str(n) for n in sorted(lines))))
    return "; ".join(sorted(set(out)))


def cf_lua(c):
    return "CFrame.new(%s)" % ", ".join(("%.4f" % v).rstrip("0").rstrip(".") if "." in "%.4f" % v else str(v)
                                       for v in c)


def placements(objects, templates):
    """context key -> list of {template, frame (12 numbers), scale}"""
    out, first = {}, {}
    for o in objects:
        ctx = o["context"]
        if not ctx or ctx in ("Kids", "Debts", "MoneyMakers", "ForSale", "Catalog"):
            continue
        if builder_of(o["template"]):
            continue  # made by a builder function: swapped there, not by context
        base = ctx.split(":")[0]
        area = o["area"].split(".")[0]
        want = CANONICAL_AREA.get(base)
        if want and area != want:
            continue
        if base in ("Collection", "DreamArea"):
            ctx = base
        key = ctx
        where = o["key"].split("/")[0]  # one instance of the context (e.g. one plot) is the pattern for all
        if first.setdefault(key, where) != where:
            continue
        frame = [round(v, 3) + 0.0 for v in o["frame_in_ctx"]]
        out.setdefault(key, []).append({"template": o["template"], "frame": frame, "scale": o.get("scale", 1.0)})
    return out


SKIN_MODULE = r'''--[[
	WorldSkin: puts the new (Blender) look on the world that the game code builds.
	NOT active until you add the calls listed in world_overhaul/IMPORT_PLAN.md.

	The old parts stay where they are and keep doing their job (collision, prompts, text, lights);
	they only become invisible. The new MeshParts are visual only. Switch back: WorldSkin.ENABLED = false.
]]

local ServerStorage = game:GetService("ServerStorage")

local WorldSkin = {}
WorldSkin.ENABLED = true

local Placements = require(script.Parent.WorldSkinPlacements)
local Kit = ServerStorage:WaitForChild("WorldKit")

-- hides the old parts under `root` (keeps collision, prompts, SurfaceGui text, lights)
local function hideOld(root: Instance)
	local list = if root:IsA("BasePart") then { root } else root:GetDescendants()
	for _, item in list do
		if item:IsA("BasePart") and not item:GetAttribute("WorldSkinNew") then
			if item.Transparency < 1 then
				item:SetAttribute("WorldSkinOldTransparency", item.Transparency)
			end
			item.Transparency = 1
			-- the dream fade (Plots.luau:514) restores "BaseTransparency": keep the old part hidden
			if item:GetAttribute("BaseTransparency") ~= nil then
				item:SetAttribute("BaseTransparency", 1)
			end
		end
	end
end

local function cloneKit(name: string): Model?
	local kit = Kit:FindFirstChild(name)
	if not kit then
		warn("WorldSkin: no kit model " .. name)
		return nil
	end
	local copy = kit:Clone()
	for _, item in copy:GetDescendants() do
		if item:IsA("BasePart") then
			item:SetAttribute("WorldSkinNew", true)
			item:SetAttribute("BaseTransparency", item.Transparency)
		end
	end
	return copy
end

-- one kit model at `cframe` (the original object's frame), optional uniform scale
function WorldSkin.add(parent: Instance, name: string, cframe: CFrame, scale: number?): Model?
	local copy = cloneKit(name)
	if not copy then
		return nil
	end
	if scale and math.abs(scale - 1) > 1e-3 then
		copy:ScaleTo(scale)
	end
	copy:PivotTo(cframe)
	copy.Parent = parent
	return copy
end

-- everything a builder context made (lobby hall, plaza, auction room, podium room, workplace + furniture...)
function WorldSkin.context(key: string, base: CFrame, root: Instance)
	if not WorldSkin.ENABLED then
		return
	end
	local list = Placements[key]
	if not list then
		return
	end
	hideOld(root)
	for _, p in list do
		WorldSkin.add(root, p.template, base * p.frame, p.scale)
	end
end

-- one named object (Kid, Money Maker, dream, tree): the kit model replaces its look
function WorldSkin.object(model: Instance, template: string, base: CFrame)
	if not WorldSkin.ENABLED then
		return
	end
	hideOld(model)
	WorldSkin.add(model, template, base)
end

-- a debt: the code sizes it by the amount, so the kit model is stretched to the old parts' box
-- (all kit meshes are axis-aligned with `base`, so a per-axis stretch is exact)
function WorldSkin.stretched(model: Model, template: string, base: CFrame)
	if not WorldSkin.ENABLED then
		return
	end
	local kit = Kit:FindFirstChild(template)
	if not kit then
		return
	end
	-- the old box in base space
	local lo, hi = Vector3.one * math.huge, -Vector3.one * math.huge
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and part.Transparency < 1 then
			local cf, size = part.CFrame, part.Size / 2
			for _, sx in { -1, 1 } do
				for _, sy in { -1, 1 } do
					for _, sz in { -1, 1 } do
						local p = base:PointToObjectSpace(cf:PointToWorldSpace(Vector3.new(sx * size.X, sy * size.Y, sz * size.Z)))
						lo, hi = lo:Min(p), hi:Max(p)
					end
				end
			end
		end
	end
	local kitLo, kitHi = kit:GetAttribute("BoxMin"), kit:GetAttribute("BoxMax") -- set in step 4
	local copy = cloneKit(template)
	if not copy or not kitLo then
		return
	end
	hideOld(model)
	local ratio = (hi - lo) / (kitHi - kitLo)
	for _, part in copy:GetDescendants() do
		if part:IsA("BasePart") then
			local p = (part.Position - kitLo) * ratio + lo -- the kit sits at the origin, axis-aligned
			part.Size = part.Size * ratio
			part.CFrame = base * CFrame.new(p)
		end
	end
	copy.Parent = model
end

-- shows/hides the new look of an object whose old part the game shows/hides (e.g. the podium board)
function WorldSkin.setVisible(root: Instance, visible: boolean)
	for _, item in root:GetDescendants() do
		if item:IsA("BasePart") and item:GetAttribute("WorldSkinNew") then
			item.Transparency = if visible then (item:GetAttribute("BaseTransparency") or 0) else 1
		end
	end
end

return WorldSkin
'''


def main():
    status = load("data", "model_status.json")
    templates = load("data", "templates.json")
    objects = load("data", "objects.json")
    refs = load("data", "script_refs.json")
    plan = load("data", "plan.json")
    aliases = plan["aliases"]

    places = placements(objects, templates)
    os.makedirs(os.path.join(ROOT, "export", "roblox"), exist_ok=True)
    json.dump(places, open(os.path.join(ROOT, "export", "placements.json"), "w"), indent=1)
    lua = ["-- generated by world_overhaul/tools/write_import_plan.py: every kit model placement,",
           "-- relative to the base CFrame of the code that builds that part of the world.", "return {"]
    for key in sorted(places):
        lua.append('\t["%s"] = {' % key)
        for p in places[key]:
            lua.append('\t\t{ template = "%s", frame = %s, scale = %s },' % (p["template"], cf_lua(p["frame"]),
                                                                            p["scale"]))
        lua.append("\t},")
    lua.append("}")
    open(os.path.join(ROOT, "export", "roblox", "WorldSkinPlacements.luau"), "w").write("\n".join(lua) + "\n")
    open(os.path.join(ROOT, "export", "roblox", "WorldSkin.luau"), "w").write(SKIN_MODULE)

    L = []
    w = L.append
    w("# Import plan - how to swap the new look into the game (NOT executed)")
    w("")
    w("Written %s. Nothing here has been done: nothing was uploaded, published or changed in `src/`." %
      time.strftime("%Y-%m-%d %H:%M"))
    w("")
    w("## The idea in one paragraph")
    w("")
    w("The world is built by Luau code when the server starts (and while a game runs), so the swap also happens in "
      "code: right after the game builds something, a small module (`WorldSkin`) makes the old parts invisible and "
      "puts a copy of the new model on exactly the same spot. The old parts keep **all** their jobs - collision, "
      "prompts, SurfaceGui text, lights, the invisible barriers and buy buttons - so gameplay cannot change. The new "
      "MeshParts are visual only. One switch (`WorldSkin.ENABLED = false`) brings the old look back.")
    w("")
    w("## Step 1 - safety first")
    w("")
    w("1. Make a git branch in the game repo (e.g. `new-look`). Do the steps below in a copy of the place, not the "
      "live game.")
    w("2. You will add 2 files to `src/` and ~12 one-line calls; everything else happens in Studio.")
    w("")
    w("## Step 2 - upload the palette (2 images)")
    w("")
    w("Upload `world_overhaul/palette/palette_color.png` and `palette_roughness.png` (Asset Manager > Import, or "
      "Bulk Import). Note both asset ids. These two images color **every** model in the world.")
    w("")
    w("## Step 3 - import the meshes")
    w("")
    w("Import every file in `world_overhaul/export/<category>/*.fbx` with the 3D Importer (File > Import 3D). "
      "Settings ([Roblox: Blender to Studio settings](https://github.com/Roblox/creator-docs/blob/main/content/en-us/art/blender.md)):")
    w("")
    w("| section | setting | value | why |")
    w("|---|---|---|---|")
    w("| File General | Import Only as a Model | on | body + glow + glass meshes stay together in one Model |")
    w("| File General | Upload to Roblox | on | gives the MeshIds |")
    w("| File General | Insert Using Scene Position | **on** | the FBX origin IS the original object's frame - it must not move |")
    w("| File Transform | World Forward / World Up | Front / Top | (see the check below) |")
    w("| File Geometry | Scale Unit | **Stud** | 1 Blender unit = 1 stud |")
    w("")
    w("**Check on the first model before importing the rest:** import `export/buildings/Workplace_Building_PIZZERIA.fbx` "
      "at the origin and compare with the numbers in `data/model_status.json` -> `bbox_new` (Roblox x, y, z): the "
      "open front of the building must be on the **-Z** side and the box must span x -23..23, y 0..~20. If the "
      "building is turned 180 degrees, set World Forward to **Back** for every import (the FBX files were exported "
      "with Blender's default axes: forward -Z, up Y, so the file coordinates are already Roblox coordinates).")
    w("")
    w("## Step 4 - the WorldKit folder")
    w("")
    w("Put every imported model in `ServerStorage/WorldKit`, **renamed to its template name** (the table at the end "
      "lists FBX file -> template name). Then run this once in the command bar (fill in the two asset ids):")
    w("")
    w("```lua")
    w("local COLOR, ROUGH = \"rbxassetid://<palette_color id>\", \"rbxassetid://<palette_roughness id>\"")
    pal = load("palette", "palette.json")["colors"]
    w("local GLOW = {")
    for k, v in pal.items():
        w("\t%s = Color3.fromRGB(%d, %d, %d)," % (k, v["rgb"][0], v["rgb"][1], v["rgb"][2]))
    w("}")
    w("local template = Instance.new(\"SurfaceAppearance\")")
    w("template.ColorMap, template.RoughnessMap = COLOR, ROUGH")
    w("for _, kit in game.ServerStorage.WorldKit:GetChildren() do")
    w("\tkit.WorldPivot = CFrame.new() -- the FBX origin = the original object's frame")
    w("\tlocal lo, hi = Vector3.one * math.huge, -Vector3.one * math.huge")
    w("\tfor _, p in kit:GetDescendants() do")
    w("\t\tif p:IsA(\"MeshPart\") then")
    w("\t\t\tp.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false")
    w("\t\t\tp.CollisionFidelity = Enum.CollisionFidelity.Box")
    w("\t\t\tp.Massless = true")
    w("\t\t\tp.CastShadow = p.Size.X * p.Size.Y * p.Size.Z > 6 -- tiny details cast no shadow")
    w("\t\t\tlocal glow = p.Name:match(\"_Glow_([A-Z_]+)\")")
    w("\t\t\tif glow then")
    w("\t\t\t\tlocal color, t = glow:match(\"^(.-)_T(%d+)$\")")
    w("\t\t\t\tp.Material = Enum.Material.Neon")
    w("\t\t\t\tp.Color = GLOW[color or glow]")
    w("\t\t\t\tp.Transparency = if t then tonumber(t) / 100 else 0.35 -- the game's NEON_SOFTNESS")
    w("\t\t\t\tp.CastShadow = false")
    w("\t\t\telseif p.Name:match(\"_Glass$\") then")
    w("\t\t\t\tp.Material, p.Color, p.Transparency = Enum.Material.Glass, GLOW.WINDOW, 0.3")
    w("\t\t\telse")
    w("\t\t\t\tp.Material, p.Reflectance = Enum.Material.SmoothPlastic, 0")
    w("\t\t\t\tfor _, old in p:GetChildren() do if old:IsA(\"SurfaceAppearance\") then old:Destroy() end end")
    w("\t\t\t\ttemplate:Clone().Parent = p")
    w("\t\t\tend")
    w("\t\t\tlocal half = p.Size / 2")
    w("\t\t\tlo, hi = lo:Min(p.Position - half), hi:Max(p.Position + half)")
    w("\t\tend")
    w("\tend")
    w("\tkit:SetAttribute(\"BoxMin\", lo) -- used to stretch debts to their size")
    w("\tkit:SetAttribute(\"BoxMax\", hi)")
    w("end")
    w("```")
    w("")
    w("(The glow color table lists the whole palette; a glow mesh is named `<model>_Glow_<COLOR>` or "
      "`<model>_Glow_<COLOR>_T<transparency %>`; `_T100` = hidden until a script shows it.)")
    w("")
    w("## Step 5 - add the two modules")
    w("")
    w("Copy `world_overhaul/export/roblox/WorldSkin.luau` and `WorldSkinPlacements.luau` to "
      "`src/server/World/`. `WorldSkinPlacements` is generated from the world data: every kit model's frame "
      "relative to the base CFrame of the code that builds it. Checked with `tools/verify_placements.py`: for all 35 "
      "places the game builds (4 plazas, 9 workplaces, 4 auction rooms, 4 podium rooms, the lobby, furniture, "
      "showcases), the list puts exactly the objects that are there, at exactly their frames (0 mismatches).")
    w("")
    w("## Step 6 - the calls (one line each)")
    w("")
    w("`local WorldSkin = require(script.Parent.WorldSkin)` at the top of each file (path as needed), then:")
    w("")
    w("| file / function | where | add |")
    w("|---|---|---|")
    w("| `Lobby.luau` `buildHall()` | at the end | `WorldSkin.context(\"Lobby\", <hall origin CFrame>, <hall folder>)` |")
    w("| `World/Plaza.luau` `Plaza.new` | at the end | `WorldSkin.context(\"Plaza\", <city base>, <city plaza folder>)` |")
    w("| `World/AuctionRoom.luau` `AuctionRoom.new` | at the end | `WorldSkin.context(\"AuctionRoom\", self.base, <room folder>)` |")
    w("| `World/PodiumRoom.luau` `PodiumRoom.new` | at the end | `WorldSkin.context(\"PodiumRoom\", self.base, <room folder>)` |")
    w("| `World/Plots.luau` `Plots:buildWorkplace(theme)` | at the end | `WorldSkin.context(\"Workplace:\" .. theme.name, self.base, self.workplaceFolder)` and `WorldSkin.context(\"Furnish:\" .. theme.name, self.base, self.workplaceFolder)` |")
    w("| `World/Plots.luau` `Plots:syncCollection` | after the showcase table is made | `WorldSkin.context(\"Collection\", self.base, <showcase part or folder>)` |")
    w("| `World/Plots.luau` `syncDream` / `addChains` (Fast Track) | after the pedestal / chains are made | `WorldSkin.context(\"DreamArea\", self.base, <pedestal + chains>)` |")
    w("| `World/Props.luau` `Props.kid` | before `return model` | `WorldSkin.object(model, <Kid / Kid_v2 / Kid_v3 by shirt color>, base)` |")
    w("| `World/Props.luau` `Props.moneyMaker` | before `model.Parent = parent` | `WorldSkin.object(model, <template for name>, base)` |")
    w("| `World/Props.luau` `Props.debtModel` | before `model.Parent = parent` | `WorldSkin.stretched(model, <template for debtName>, base)` (School Loan: `Debt_SchoolLoan_books<n>`) |")
    w("| `World/Props.luau` `Props.dream` | right after `builder.build()` | `WorldSkin.object(model, \"Dream_\" .. <name>, model:GetPivot())` |")
    w("| `World/Props.luau` `Props.tree` | before it returns | `WorldSkin.object(<tree model>, \"Tree\", base)` |")
    w("| `World/AuctionRoom.luau` `AuctionRoom:highlight` | inside the loop | `WorldSkin.setVisible(<desk glow shell>, isTop)`: the old desk turns gold Neon, the new desk has a hidden gold shell (`_Glow_GOLD_T100`) for that |")
    w("| `World/PodiumRoom.luau` `fillBoard` (line 158) | next to `self.board.Transparency = ...` | `WorldSkin.setVisible(<board kit copy>, #standings > 3)` |")
    w("")
    w("Why these places: the ghost FOR SALE copies (`Props.makeGhost`), the 0.4x collection minis "
      "(`model:ScaleTo(0.4)`), the floating dreams (`ScaleTo` + `PivotTo`), the kids' hop and the dream spin "
      "(`PivotTo`) all run **after** these builders return, so they automatically include the new MeshParts "
      "(they are BaseParts inside the same Model).")
    w("")
    w("## Step 7 - test in Studio (Play Solo, then 2-4 players)")
    w("")
    for item in [
        "Lobby: walk around, the room booths still open, the spawn still works, the trophy and palms look right.",
        "Start a game: your workplace appears with the new building, furniture, fence, lamps and yard; you still "
        "walk on the same floor heights, the Pay/Buy prompts still appear on the debts and the FOR SALE item.",
        "Buy a Money Maker: it stands on the lot, the next one stacks on top at the same height as before "
        "(`GetBoundingBox`), its label floats at the same spot.",
        "The FOR SALE copy looks see-through (ForceField) - also the new meshes.",
        "Add investments: the minis in the showcase are 0.4x and sit on the table.",
        "Your dream floats and spins; it fades in/out as before (the old parts must stay hidden while it fades).",
        "Escape: the workplace turns into the Fast Track version (new look too), pedestal + chains.",
        "Auction: the top bidder's desk glows gold. Podium: the board shows only with more than 3 players.",
        "Text: every sign still shows its text (prices, names, job names) in front of the new boards.",
        "Performance: open the MicroProfiler / Stats on a phone-sized client: triangles and draw calls.",
    ]:
        w("- [ ] " + item)
    w("")
    w("## Switch back")
    w("")
    w("Set `WorldSkin.ENABLED = false` (or remove the calls): nothing is hidden and no kit model is added, so the "
      "game looks exactly like today. Nothing else was changed.")
    w("")
    w("## Collision and materials per object type")
    w("")
    w("| type | new MeshParts | old parts |")
    w("|---|---|---|")
    w("| everything | Anchored, CanCollide/CanQuery/CanTouch **off**, CollisionFidelity Box, Massless | stay, invisible (Transparency 1), collide/prompt/trigger exactly as today |")
    w("| body mesh | SmoothPlastic + SurfaceAppearance (palette color + roughness) | |")
    w("| `_Glow_<COLOR>` | Neon, palette color, Transparency 0.35 (or `_T..`), no shadow | |")
    w("| `_Glass` | Glass, WINDOW color, Transparency 0.3 | |")
    w("| tiny details (< 6 cubic studs) | CastShadow off | |")
    w("")
    w("## Every model: file, name and where it goes")
    w("")
    w("| template (= WorldKit name) | FBX | meshes | how it is placed | built by (game code) | script-referenced |")
    w("|---|---|---|---|---|---|")
    for name in plan["order"]:
        t = templates.get(name, {})
        e = status.get(name)
        if e is None and name in aliases:
            w("| %s | uses `%s` | | stretched to its own size | %s | %s |" % (
                name, aliases[name], (builder_of(name) or ("",))[0],
                "yes" if name in refs["script_referenced"] else ""))
            continue
        if e is None:
            w("| %s | (not modelled) | | | | |" % name)
            continue
        b = builder_of(name)
        if b:
            how = "`WorldSkin.%s`" % ("stretched" if name.startswith("Debt_") else "object")
            src = b[0]
        else:
            keys = sorted(k for k, lst in places.items() if any(p["template"] == name for p in lst))
            if len(keys) > 2:
                groups = sorted({k.split(":")[0] for k in keys})
                label = ", ".join("%s:* (%d)" % (g, sum(1 for k in keys if k.startswith(g + ":"))) for g in groups)
            else:
                label = ", ".join(keys)
            how = "`WorldSkin.context` in %s" % label if keys else "(by hand: one object)"
            src = source_of(t.get("type", name)) or ""
        fbx = e.get("fbx", "")
        meshes = ", ".join("`%s`" % m for m in e.get("meshes", []))
        w("| %s | `%s` | %s | %s | %s | %s |" % (name, fbx, meshes, how, src,
                                               "yes" if name in refs["script_referenced"] else ""))
    extra = sorted(n for n in status if n not in plan["order"])
    if extra:
        w("")
        w("Extra kit meshes: " + ", ".join("`%s` (`%s`)" % (n, status[n].get("fbx", "")) for n in extra) + ".")
    w("")
    open(os.path.join(ROOT, "IMPORT_PLAN.md"), "w").write("\n".join(L) + "\n")
    print("IMPORT_PLAN.md written,", sum(len(v) for v in places.values()), "context placements in", len(places),
          "contexts")


if __name__ == "__main__":
    main()

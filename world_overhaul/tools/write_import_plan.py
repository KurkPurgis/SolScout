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
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from inventory import RULES, cf_inv, cf_mul, cf_pos  # noqa: E402

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
]

# Step 6 of IMPORT_PLAN.md: (file / function, where, the line)
STEP6 = [
    ("`Lobby.luau` (start-up)", "right before `buildHall()` is called (line 476)",
     "`WorldSkin.object(workspace:FindFirstChild(\"Baseplate\"), \"Baseplate\", CFrame.new())`: the grass "
     "baseplate of the place (Rojo `default.project.json`); the old Part stays, invisible, so `Props.groundY` "
     "still raycasts against it"),
    ("`Lobby.luau` `buildHall()`", "at the end",
     "`WorldSkin.context(\"Lobby\", hallBase, folder)`"),
    ("`World/Plaza.luau` `Plaza.new`", "before `return self`",
     "`WorldSkin.context(\"Plaza\", base, folder)`"),
    ("`World/AuctionRoom.luau` `AuctionRoom.new`", "before `return self`",
     "`WorldSkin.context(\"AuctionRoom\", BASE, folder)`"),
    ("`World/PodiumRoom.luau` `PodiumRoom.new`", "before `return self`",
     "`WorldSkin.context(\"PodiumRoom\", base, folder)`"),
    ("`World/Plots.luau` `Plots:buildWorkplace(theme)`", "at the very end of the function: after the "
     "sandbox and the `if theme.luxury ... else ... end` block (Fast Track gate / debt pad), just before its `end`",
     "`WorldSkin.context({ \"Workplace:\" .. theme.title, \"Furnish:\" .. theme.title }, self.base, "
     "self.workplaceFolder)` (one call for both: they share the folder; the keys use the sign title, e.g. "
     "`Workplace:BUS DEPOT`)"),
    ("`World/Plots.luau` `Plots:syncCollection`", "right after the two `Props.box` lines of the showcase table "
     "(before the loop)", "`WorldSkin.context(\"Collection\", self.base, self.collectionFolder)`"),
    ("`World/Plots.luau` `Plots:syncDream`", "in the `else` branch (locked or won dream), right after the two "
     "`Props.box` lines of the marble pedestal (before `Props.dream`)",
     "`WorldSkin.context(\"DreamArea\", self.base, self.dreamFolder)`"),
    ("`World/Plots.luau` `addChains(folder, model)`", "at the end",
     "`WorldSkin.chains(folder)`: the chains **link by link** (your decision): `Dream_ChainSegment` pieces tiled "
     "along every chain bar + `Dream_Padlock`"),
    ("`World/Props.luau` `Props.kid`", "after `model.PrimaryPart = body`",
     "`WorldSkin.object(model, WorldSkin.kidTemplate(shirtColor), base)` (4 shirts: `Kid`, `Kid_v2`, `Kid_v3`, "
     "`Kid_v4`)"),
    ("`World/Props.luau` `Props.moneyMaker`", "before `model.Parent = parent`",
     "`WorldSkin.object(model, WorldSkin.makerTemplate(name, value), base)` (PokeBlox cards: the model with the "
     "case color of `Props.cardCase(value)`)"),
    ("`World/Props.luau` `Props.debtModel`", "before `model.Parent = parent`",
     "`WorldSkin.stretched(model, WorldSkin.debtTemplate(debtName, amount), base)` (School Loan: the model with "
     "the right number of books)"),
    ("`World/Props.luau` `Props.dream`", "right after `local model = builder.build()`",
     "`WorldSkin.object(model, \"Dream_\" .. model.Name, model:GetPivot())` (`model.Name` is `BeachVilla`, "
     "`PrivateJet`...; not `dreamName`, which has spaces)"),
    ("`World/AuctionRoom.luau` `AuctionRoom:highlight`", "inside the loop, after the two lines",
     "`WorldSkin.setGlow(WorldSkin.nearest(self.folder, \"AuctionRoom_BidderDesk\", podium.Position), isTop)`: "
     "the old desk (now hidden) turns gold Neon; the new desk shows its gold glow shell (`_Glow_GOLD_T100`)"),
    ("`World/PodiumRoom.luau` `PodiumRoom:fillBoard`", "**replace** line 158 "
     "`self.board.Transparency = if #standings > 3 then 0 else 1`",
     "`WorldSkin.show(self.board, self.folder, \"PodiumRoom_Board\", #standings > 3)` (shows/hides the new "
     "board and keeps the old one hidden; without WorldSkin it does exactly what line 158 did)"),
]


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


HELPER_FILES = ("Props.luau", "ModelKit.luau", "dump_world.luau")


def built_by(template, objects, parts):
    """The game-code lines that build an object (file:line), from the world dump: for every part, the first
    frame of its call chain that is not a helper (Props / ModelKit), e.g. Themes.luau:143 for Props.car."""
    lines = {}
    for o in objects:
        if o["template"] != template:
            continue
        for pid in o["part_ids"]:
            for frame in parts[pid].get("chain") or []:
                file, _, line = re.sub(r"\(.*\)$", "", frame).partition(":")
                if file not in HELPER_FILES and line.isdigit():
                    lines.setdefault(file, set()).add(int(line))
                    break
    return "; ".join("%s:%s" % (f, ",".join(str(n) for n in sorted(v))) for f, v in sorted(lines.items()))


def alias_model(name, templates, aliases):
    """-> (kit model, how) for a template without a model of its own (data/plan.json aliases)."""
    base = aliases[name]
    if name.startswith("Debt_SchoolLoan"):
        books = int(round((templates[name]["size"][1] - 0.62) / 0.8))  # 0.8 per book on a 0.62 base
        model = "Debt_SchoolLoan" if books == 3 else "Debt_SchoolLoan_books%d" % books
        return model, "its own %d-book model, picked by `WorldSkin.debtTemplate`" % books
    if name.startswith("Debt_"):
        return base, "`%s`, stretched to its size by `WorldSkin.stretched`" % base
    return base, "`%s`, placed turned / moved by `WorldSkin.context` (same size)" % base


def is_script_referenced(name, templates, refs):
    return templates.get(name, {}).get("type", name) in refs["script_referenced"]


def cf_lua(c):
    return "CFrame.new(%s)" % ", ".join(("%.4f" % v).rstrip("0").rstrip(".") if "." in "%.4f" % v else str(v)
                                       for v in c)


# owner decision 2026-10-05: the locked dream's chains are swapped link by link (kit pieces), not as one mesh
LINK_BY_LINK = {"Dream_Chains"}
# PokeBlox cards: the case color follows the card's value (Props.cardCase), so there is a kit model per case
CARD_CASES = {
    "PokeBlox Card": ["Maker_PokeBloxCard", "Maker_PokeBloxCard_case2", "Maker_PokeBloxCard_case3",
                      "Maker_PokeBloxCard_case4"],
    "Rare PokeBlox Card": ["Maker_RarePokeBloxCard", "Maker_RarePokeBloxCard_v2", "Maker_RarePokeBloxCard_v3",
                           "Maker_RarePokeBloxCard_v4"],
    "Shiny PokeBlox Card": ["Maker_ShinyPokeBloxCard_case1", "Maker_ShinyPokeBloxCard_case2",
                            "Maker_ShinyPokeBloxCard", "Maker_ShinyPokeBloxCard_case4"],
}
CARD_DEFAULT_VALUE = {"PokeBlox Card": 500, "Rare PokeBlox Card": 8000, "Shiny PokeBlox Card": 20000}
# Plots.luau KID_SHIRTS (Config.MaxChildren = 4)
KID_SHIRTS = {"255,90,90": "Kid", "90,200,255": "Kid_v2", "255,210,60": "Kid_v3", "150,230,110": "Kid_v4"}


def world_parts():
    return {e["id"]: e for e in load("data", "world_instances.json")}


def context_group(o, parts):
    """The dump group of the builder call that made this object's context (label == the context name,
    innermost wins): {"label", "seq", "base"}. `base` is the CFrame that code builds with (self.base,
    CFrame.new(origin), the hall origin...) - the same CFrame the Step 6 call passes to WorldSkin."""
    hit = None
    for g in parts[o["part_ids"][0]].get("groups") or []:
        if g["label"] == o["context"]:
            hit = g
    if hit is None or not hit.get("base"):
        raise SystemExit("no context group with a base for %s (%s)" % (o["key"], o["context"]))
    return hit


def resolve_alias(template, templates, aliases, status):
    """-> (kit template, offset CFrame) for a context object. A same-size alias (e.g. the mirrored lobby palm)
    uses its base model, moved by the difference of the two boxes; a stretched alias cannot be placed by context."""
    if template in status:
        return template, None
    base = aliases.get(template)
    if base is None or base not in status:
        raise SystemExit("placement of %s: no kit model (not built, no alias)" % template)
    a, b = templates[base], templates[template]
    if any(abs(x - y) > 1e-3 for x, y in zip(a["size"], b["size"])):
        raise SystemExit("placement of %s: alias of %s with another size" % (template, base))
    d = [b["bbox_min"][i] - a["bbox_min"][i] for i in range(3)]
    return base, (cf_pos(*d) if any(abs(v) > 1e-3 for v in d) else None)


def placements(objects, templates, aliases, status, parts):
    """context key -> list of {template, frame (12 numbers, relative to the context base), scale}.
    One built instance of each context (the first plot / room / city met) is the pattern for all of them."""
    out, first = {}, {}
    for o in objects:
        ctx = o["context"]
        if not ctx or ctx in ("Kids", "Debts", "MoneyMakers", "ForSale", "Catalog"):
            continue
        if builder_of(o["template"]):
            continue  # made by a builder function: swapped there, not by context
        if o["template"] in LINK_BY_LINK:
            continue  # the chains are swapped link by link (WorldSkin.chains), not as one model
        area = o["area"].split(".")[0]
        want = CANONICAL_AREA.get(ctx)
        if want and area != want:
            continue
        group = context_group(o, parts)
        if first.setdefault(ctx, group["seq"]) != group["seq"]:
            continue
        template, offset = resolve_alias(o["template"], templates, aliases, status)
        frame = cf_mul(cf_inv(group["base"]), o["frame"])
        if offset:
            frame = cf_mul(frame, offset)
        frame = [round(v, 3) + 0.0 for v in frame]
        out.setdefault(ctx, []).append({"template": template, "frame": frame, "scale": o.get("scale", 1.0)})
    return out


SKIN_MODULE = r'''--[[
	WorldSkin: puts the new (Blender) look on the world that the game code builds.
	NOT active until you add the calls listed in world_overhaul/IMPORT_PLAN.md.

	The old parts stay where they are and keep doing their job (collision, prompts, text, lights);
	they only become invisible. The new MeshParts are visual only. Switch back: WorldSkin.ENABLED = false.
	If a kit model is missing, WorldSkin warns and leaves that object (or that whole context) in the old look:
	nothing is hidden without its replacement.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local Config = require(ReplicatedStorage.Shared.Config)
local Placements = require(script.Parent.WorldSkinPlacements)

local WorldSkin = {}
WorldSkin.ENABLED = true

local Kit = ServerStorage:FindFirstChild("WorldKit")
if not Kit then
	warn("WorldSkin: ServerStorage.WorldKit is missing (IMPORT_PLAN.md step 4) - the old look stays")
	WorldSkin.ENABLED = false
end

-- how see-through a hidden glow shell (a `_T100` mesh) is when a script shows it: the game's NEON_SOFTNESS
local SHELL_SHOWN = 0.35

-- game name -> kit model (generated from the world data)
--@NAME_TABLES@

-- does the kit have this model? (warns when it does not)
local function hasKit(name: string?): boolean
	if Kit and name and Kit:FindFirstChild(name) then
		return true
	end
	warn("WorldSkin: no kit model " .. tostring(name) .. " - the old look stays")
	return false
end

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
	if not hasKit(name) then
		return nil
	end
	local copy = (Kit :: Instance):FindFirstChild(name):Clone()
	for _, item in copy:GetDescendants() do
		if item:IsA("BasePart") then
			item:SetAttribute("WorldSkinNew", true)
			-- "WorldSkinShown": the Transparency this part has when it is shown (setVisible / setGlow)
			if item.Transparency >= 1 then
				item:SetAttribute("WorldSkinShell", true) -- a glow shell, hidden until a script shows it
				item:SetAttribute("WorldSkinShown", SHELL_SHOWN)
			else
				item:SetAttribute("WorldSkinShown", item.Transparency)
			end
			item:SetAttribute("BaseTransparency", item.Transparency)
		end
	end
	return copy
end

-- the new parts under `root` (or `root` itself)
local function newParts(root: Instance): { BasePart }
	local out = {}
	local list = if root:IsA("BasePart") then { root } else root:GetDescendants()
	for _, item in list do
		if item:IsA("BasePart") and item:GetAttribute("WorldSkinNew") then
			table.insert(out, item)
		end
	end
	return out
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

-- everything a builder context made (lobby hall, plaza, auction room, podium room, workplace + furniture...).
-- `keys`: one Placements key, or several that share `root` (the workplace and its furniture).
function WorldSkin.context(keys: string | { string }, base: CFrame, root: Instance)
	if not WorldSkin.ENABLED then
		return
	end
	local lists = {}
	for _, key in (if type(keys) == "table" then keys else { keys }) do
		local list = Placements[key]
		if list then
			for _, p in list do
				if not hasKit(p.template) then
					return -- keep the whole old look here, so nothing goes missing
				end
			end
			table.insert(lists, list)
		end
	end
	if #lists == 0 then
		return
	end
	hideOld(root)
	for _, list in lists do
		for _, p in list do
			WorldSkin.add(root, p.template, base * p.frame, p.scale)
		end
	end
end

-- one named object (kid, Money Maker, dream, the baseplate): the kit model replaces its look
function WorldSkin.object(model: Instance?, template: string?, base: CFrame)
	if not WorldSkin.ENABLED or not model or not hasKit(template) then
		return
	end
	hideOld(model :: Instance)
	WorldSkin.add(model :: Instance, template :: string, base)
end

-- a debt: the code sizes it by the amount, so the kit model is stretched to the old parts' box
-- (all kit meshes are axis-aligned with `base`, so a per-axis stretch is exact)
function WorldSkin.stretched(model: Model, template: string?, base: CFrame)
	if not WorldSkin.ENABLED or not hasKit(template) then
		return
	end
	local kit = (Kit :: Instance):FindFirstChild(template :: string)
	local kitLo, kitHi = kit:GetAttribute("BoxMin"), kit:GetAttribute("BoxMax") -- set in step 4
	if not kitLo or not kitHi then
		warn("WorldSkin: kit model " .. tostring(template) .. " has no BoxMin/BoxMax (step 4) - the old look stays")
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
	local copy = cloneKit(template :: string)
	if not copy then
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

-- The locked dream's chains, LINK BY LINK (owner decision): Plots.luau addChains() makes "Chain" bars
-- (ModelKit.bar: Size = (0.35, 0.35, length), the length along the bar's local Z) and a padlock
-- ("PadlockBody", "PadlockHole", "PadlockShackle"). Every bar gets Dream_ChainSegment kit pieces
-- (2 links, 3 studs long along their local +Z, origin at one end) tiled end to end; the padlock gets
-- Dream_Padlock. Works for any dream size, because it follows the bars the game actually made.
local SEGMENT_LENGTH = 3
function WorldSkin.chains(folder: Instance)
	if not WorldSkin.ENABLED or not hasKit("Dream_ChainSegment") or not hasKit("Dream_Padlock") then
		return
	end
	for _, part in folder:GetChildren() do
		-- "WorldSkinDone": this bar already has its pieces (a second call adds nothing)
		if part:IsA("BasePart") and not part:GetAttribute("WorldSkinNew") and not part:GetAttribute("WorldSkinDone") then
			if part.Name == "Chain" then
				local length = part.Size.Z
				local count = math.max(1, math.round(length / SEGMENT_LENGTH))
				local step = length / count -- each piece is scaled a little so the pieces fill the bar exactly
				for index = 0, count - 1 do
					WorldSkin.add(folder, "Dream_ChainSegment", part.CFrame * CFrame.new(0, 0, -length / 2 + index * step),
						step / SEGMENT_LENGTH)
				end
				part:SetAttribute("WorldSkinDone", true)
				hideOld(part)
			elseif part.Name == "PadlockBody" then
				WorldSkin.add(folder, "Dream_Padlock", part.CFrame)
				part:SetAttribute("WorldSkinDone", true)
				hideOld(part)
			elseif part.Name == "PadlockHole" or part.Name == "PadlockShackle" then
				hideOld(part)
			end
		end
	end
end

-- shows/hides the whole new look of an object whose old part the game shows/hides (the podium board).
-- `root`: the kit copy (a Model) or one of its parts; nil (no kit copy, e.g. WorldSkin off) does nothing.
function WorldSkin.setVisible(root: Instance?, visible: boolean)
	if not root then
		return
	end
	for _, item in newParts(root) do
		item.Transparency = if visible then (item:GetAttribute("WorldSkinShown") or 0) else 1
	end
end

-- turns the hidden glow shell (`_Glow_<COLOR>_T100`) of a kit copy on/off; the rest of the copy stays as it is
function WorldSkin.setGlow(root: Instance?, on: boolean)
	if not root then
		return
	end
	for _, item in newParts(root) do
		if item:GetAttribute("WorldSkinShell") then
			item.Transparency = if on then SHELL_SHOWN else 1
		end
	end
end

-- an object the game shows/hides (the podium board, PodiumRoom:fillBoard): shows/hides the kit copy named
-- `template` under `root` and keeps the old part hidden; without a kit copy (WorldSkin off) the old part as before
function WorldSkin.show(oldPart: BasePart, root: Instance, template: string, visible: boolean)
	local copy = root:FindFirstChild(template)
	if copy and copy:IsA("Model") then
		oldPart.Transparency = 1
		WorldSkin.setVisible(copy, visible)
	else
		oldPart.Transparency = if visible then 0 else 1
	end
end

-- the kit copy named `template` under `root` whose pivot is closest to `position` (e.g. the desk of podium i)
function WorldSkin.nearest(root: Instance, template: string, position: Vector3): Model?
	local best, bestDistance = nil, math.huge
	for _, item in root:GetChildren() do
		if item:IsA("Model") and item.Name == template then
			local distance = (item:GetPivot().Position - position).Magnitude
			if distance < bestDistance then
				best, bestDistance = item, distance
			end
		end
	end
	return best
end

-- the kit model for a Money Maker / investment (Props.moneyMaker): PokeBlox cards by their case (value)
function WorldSkin.makerTemplate(name: string, value: number?): string
	local cases = CARD_CASES[name]
	if cases then
		local worth = value or CARD_DEFAULT_VALUE[name] -- the builders' own default (Props.luau makerBuilders)
		for index, case in Config.Investments.CardCases do
			if worth < case.below then
				return cases[index]
			end
		end
		return cases[#cases]
	end
	return MAKERS[name] or "Maker_UnknownMaker" -- unknown names get the golden box (Props.moneyMaker)
end

-- the kit model for a debt (Props.debtModel); School Loan: one model per number of books
function WorldSkin.debtTemplate(debtName: string, amount: number): string
	if debtName == "School Loan" then
		local books = math.clamp(2 + math.floor(amount / 15000), 2, 7) -- Props.luau debtBuilders["School Loan"]
		return if books == 3 then "Debt_SchoolLoan" else "Debt_SchoolLoan_books" .. books
	end
	return DEBTS[debtName] or "Debt_OtherDebt" -- unknown names get the debt crate (Props.debtCrate)
end

-- the kit model for a kid (Props.kid), by shirt color (Plots.luau KID_SHIRTS)
function WorldSkin.kidTemplate(shirtColor: Color3): string
	local key = string.format("%d,%d,%d", math.round(shirtColor.R * 255), math.round(shirtColor.G * 255),
		math.round(shirtColor.B * 255))
	return KIDS[key] or "Kid"
end

return WorldSkin
'''


def name_tables(templates, status):
    """Luau tables: game name -> kit model, for the builder calls (makers, debts, kids, PokeBlox cases)."""
    makers, debts = {}, {}
    for name, t in sorted(templates.items()):
        if "_v" in name or name not in status:
            continue
        if name.startswith("Maker_"):
            makers[t["roblox_name"]] = name
        elif name.startswith("Debt_"):
            debts[t["roblox_name"]] = name
    for game_name in CARD_CASES:
        makers.pop(game_name, None)
    for needed in [n for c in CARD_CASES.values() for n in c] + list(KID_SHIRTS.values()):
        if needed not in status:
            raise SystemExit("name table: no kit model " + needed)
    L = ["local MAKERS = {"]
    L += ['\t["%s"] = "%s",' % kv for kv in sorted(makers.items())]
    L += ["}", "local DEBTS = {"]
    L += ['\t["%s"] = "%s",' % kv for kv in sorted(debts.items()) if kv[0] != "School Loan"]
    L += ["}", "-- in Config.Investments.CardCases order: COMMON, RARE, EPIC, LEGENDARY", "local CARD_CASES = {"]
    for game_name, names in CARD_CASES.items():
        L.append('\t["%s"] = { %s },' % (game_name, ", ".join('"%s"' % n for n in names)))
    L += ["}", "local CARD_DEFAULT_VALUE = {"]
    L += ['\t["%s"] = %d,' % kv for kv in CARD_DEFAULT_VALUE.items()]
    L += ["}", "local KIDS = {"]
    L += ['\t["%s"] = "%s",' % kv for kv in KID_SHIRTS.items()]
    L.append("}")
    return "\n".join(L)


def main():
    status = load("data", "model_status.json")
    templates = load("data", "templates.json")
    objects = load("data", "objects.json")
    refs = load("data", "script_refs.json")
    plan = load("data", "plan.json")
    aliases = plan["aliases"]

    places = placements(objects, templates, aliases, status, world_parts())
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
    open(os.path.join(ROOT, "export", "roblox", "WorldSkin.luau"), "w").write(
        SKIN_MODULE.replace("--@NAME_TABLES@", name_tables(templates, status)))

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
    w("2. You will add 2 files to `src/`, a `require` line in 6 files and %d one-line calls (Step 6; one of them "
      "replaces a line); everything else happens in Studio." % len(STEP6))
    w("")
    w("## Step 2 - upload the palette (2 images)")
    w("")
    w("Upload `world_overhaul/palette/palette_color.png` and `palette_roughness.png` (Asset Manager > Import, or "
      "Bulk Import). Note both asset ids. These two images color **every** model in the world.")
    w("")
    w("## Step 3 - import the meshes")
    w("")
    fbx_count = sum(1 for n, e in status.items() if e.get("fbx") and n not in LINK_BY_LINK)
    w("Import every file in `world_overhaul/export/<category>/*.fbx` - %d files: all of them except "
      "`export/props/Dream_Chains.fbx`, the one-piece chains that your link-by-link decision replaced - "
      "with the 3D Importer (File > Import 3D). " % fbx_count +
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
    (lx, ly, lz), (hx, hy, hz) = status["Workplace_Building_PIZZERIA"]["bbox_new"]
    w("**Check on the first model before importing the rest:** import `export/buildings/Workplace_Building_PIZZERIA.fbx` "
      "at the origin. Its box must span x %.1f..%.1f, y %.1f..%.1f, z %.1f..%.1f (from `data/model_status.json` -> "
      "`bbox_new`): the open front (awning edge at z %.1f) and the big sign (near z 6.5) on the low-z side. If "
      "the box spans z %.1f..%.1f instead (and x %.1f..%.1f), the file came in turned 180 degrees about the "
      "origin: set World Forward to **Back** for every import. The FBX files were exported with Blender's default "
      "axes (forward -Z, up Y), so the coordinates in the files already are Roblox coordinates."
      % (lx, hx, ly, hy, lz, hz, lz, -hz, -lz, -hx, -lx))
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
    w("\t\t\tlocal glow = p.Name:match(\"_Glow_([%w_]+)$\")")
    w("\t\t\tif glow then")
    w("\t\t\t\tlocal color, t = glow:match(\"^(.-)_T(%d+)$\")")
    w("\t\t\t\tp.Material = Enum.Material.Neon")
    w("\t\t\t\tlocal c = GLOW[color or glow]")
    w("\t\t\t\tif c then p.Color = c else warn(\"no glow color for \" .. p:GetFullName()) end")
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
    from verify_placements import verify  # here: it imports this file
    check = verify(places, quiet=True)
    if check["mismatches"]:
        raise SystemExit("verify_placements: %d mismatches - fix the placements first" % check["mismatches"])
    kinds = check["instances"]
    w("Copy `world_overhaul/export/roblox/WorldSkin.luau` and `WorldSkinPlacements.luau` to "
      "`src/server/World/`. `WorldSkinPlacements` is generated from the world data: every kit model's frame "
      "relative to the base CFrame of the code that builds it (one built copy of each context is the pattern). "
      "Checked with `tools/verify_placements.py`, independently: it takes each place's base CFrame from the world "
      "dump and checks, in world space, that the list puts exactly the objects that are there, turned the same way, "
      "with the kit's box on the object's box. All %d places the snapshot built pass (0 mismatches): %s. The chains "
      "are not in this check: `WorldSkin.chains` follows the chain bars the game makes (tested in "
      "`tools/luau/test_worldskin_chains.luau`)." % (check["checked"], ", ".join(
          "%d %s" % (n, label) for n, label in [
              (kinds["Workplace"], "workplaces"),
              (kinds["Furnish"], "furniture sets"), (kinds["Plaza"], "plazas"),
              (kinds["AuctionRoom"], "auction rooms"), (kinds["PodiumRoom"], "podium rooms"),
              (kinds["Collection"], "showcases"), (kinds["DreamArea"], "dream pedestals"),
              (kinds["Lobby"], "lobby")])))
    w("")
    w("`WorldSkin` never hides anything without its replacement: if a kit model is missing from `WorldKit`, it warns "
      "in the output and leaves that object (or that whole context) in the old look. Without a `WorldKit` folder it "
      "switches itself off.")
    w("")
    w("## Step 6 - the calls (one line each)")
    w("")
    w("`local WorldSkin = require(script.Parent.WorldSkin)` at the top of `Plaza.luau`, `AuctionRoom.luau`, "
      "`PodiumRoom.luau`, `Plots.luau` and `Props.luau` (all in `World/`), and "
      "`local WorldSkin = require(script.Parent.World.WorldSkin)` in `Lobby.luau` (adjust to your Rojo tree), then:")
    w("")
    w("| file / function | where | line |")
    w("|---|---|---|")
    for row in STEP6:
        w("| %s | %s | %s |" % row)
    w("")
    w("Trees need no call of their own: `Props.tree` puts its parts straight into the plaza folder, so the "
      "`Plaza` context hides them and places the 8 `Tree` models around the plaza with the rest of it.")
    w("")
    w("Why these places: the ghost FOR SALE copies (`Props.makeGhost`), the 0.4x collection minis "
      "(`model:ScaleTo(0.4)`), the floating dreams (`ScaleTo` + `PivotTo`), the kids' hop and the dream spin "
      "(`PivotTo`) all run **after** these builders return, so they automatically include the new MeshParts "
      "(they are BaseParts inside the same Model).")
    w("")
    w("## Step 7 - test in Studio (Play Solo, then 2-4 players)")
    w("")
    for item in [
        "Lobby: walk around, the room booths still open, the spawn still works, the trophy and palms look right; "
        "the grass baseplate has the new look and you still stand on it.",
        "Start a game: your workplace appears with the new building, furniture, fence, lamps and yard; you still "
        "walk on the same floor heights, the Pay/Buy prompts still appear on the debts and the FOR SALE item.",
        "Buy a Money Maker: it stands on the lot, the next one stacks on top at the same height as before "
        "(`GetBoundingBox`), its label floats at the same spot.",
        "The FOR SALE copy looks see-through (ForceField) - also the new meshes.",
        "Add investments: the minis in the showcase are 0.4x and sit on the table; a PokeBlox card whose value "
        "crosses a case boundary (1000 / 10000 / 30000) changes its case color.",
        "Have 4 kids: all 4 have the new look (red, blue, yellow, green shirts) and still hop.",
        "Your dream floats and spins; it fades in/out as before (the old parts must stay hidden while it fades).",
        "Escape: the workplace turns into the Fast Track version (new look too), pedestal + chains.",
        "Auction: only the top bidder's desk glows gold. Podium: the board shows only with more than 3 players.",
        "Output: no `WorldSkin:` warnings (a warning names a kit model that is missing from `WorldKit`).",
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
    w("*name in the game*: the Model name for objects the game makes as a named Model (Money Makers, debts, "
      "dreams, `Kid`; the kit goes inside that Model, so the name stays); otherwise the inventory name of a group "
      "of plain `Part`s (`INVENTORY.md`), which keep their own names. `Other Debt` and `Unknown Maker` are "
      "stand-in names the world dump used to make the game build its fallback debt crate and golden box. "
      "*script-referenced*: some game script finds "
      "the object type by name, measures it or changes it (`data/script_refs.json`).")
    w("")
    w("| template (= WorldKit name) | name in the game | FBX | meshes | how it is placed | built by (game code) | script-referenced |")
    w("|---|---|---|---|---|---|---|")
    parts = world_parts()
    for name in plan["order"]:
        t = templates.get(name, {})
        e = status.get(name)
        sref = "yes" if is_script_referenced(name, templates, refs) else ""
        if e is None and name in aliases:
            model, how = alias_model(name, templates, aliases)
            src = (builder_of(name) or (built_by(name, objects, parts),))[0]
            w("| %s | %s | uses `%s` (`%s`) | | %s | %s | %s |" % (
                name, t.get("roblox_name", ""), model, status[model].get("fbx", ""), how, src, sref))
            continue
        if e is None:
            w("| %s | %s | (not modelled) | | | | |" % (name, t.get("roblox_name", "")))
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
            how = "`WorldSkin.context` in %s" % label
            src = built_by(name, objects, parts)
            if name in LINK_BY_LINK:
                how = ("**not imported**: replaced link by link by `Dream_ChainSegment` + `Dream_Padlock` "
                       "(`WorldSkin.chains`, your decision)")
            elif name == "Baseplate":
                how, src = "`WorldSkin.object` (Step 6, `Lobby.luau`)", "the place (Rojo `default.project.json`)"
            elif not keys:
                raise SystemExit("model table: no way to place " + name)
        fbx = e.get("fbx", "")
        meshes = ", ".join("`%s`" % m for m in e.get("meshes", []))
        w("| %s | %s | `%s` | %s | %s | %s | %s |" % (name, t.get("roblox_name", ""), fbx, meshes, how, src, sref))
    extra = sorted(n for n in status if n not in plan["order"])
    if extra:
        w("")
        w("Extra kit meshes: " + ", ".join("`%s` (`%s`)" % (n, status[n].get("fbx", "")) for n in extra) + ". "
          "`Dream_ChainSegment` and `Dream_Padlock` are used by `WorldSkin.chains`; `WorldSkin.debtTemplate` picks "
          "the `Debt_SchoolLoan_books<n>` meshes by the number of books, `WorldSkin.makerTemplate` the "
          "`..._case<n>` PokeBlox cards by the case color of the card's value, `WorldSkin.kidTemplate` `Kid_v4` "
          "for the 4th (green) shirt. The card cases and `Kid_v4` were not in the snapshot, but the game makes "
          "them; the 4- and 7-book School Loans were (`Debt_SchoolLoan_v3`, `_v2`).")
    w("")
    open(os.path.join(ROOT, "IMPORT_PLAN.md"), "w").write("\n".join(L) + "\n")
    print("IMPORT_PLAN.md written,", sum(len(v) for v in places.values()), "context placements in", len(places),
          "contexts")


if __name__ == "__main__":
    main()

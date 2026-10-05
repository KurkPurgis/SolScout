--[[
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
local MAKERS = {
	["Apartment"] = "Maker_Apartment",
	["Apartment Building"] = "Maker_ApartmentBuilding",
	["Bowling Alley"] = "Maker_BowlingAlley",
	["Car Wash"] = "Maker_CarWash",
	["Coffee Shop"] = "Maker_CoffeeShop",
	["Food Truck"] = "Maker_FoodTruck",
	["Game Studio"] = "Maker_GameStudio",
	["Gold Bar"] = "Maker_GoldBar",
	["Gold Coin"] = "Maker_GoldCoin",
	["Gold Treasure Chest"] = "Maker_GoldTreasureChest",
	["Hotel"] = "Maker_Hotel",
	["House to Rent"] = "Maker_HouseToRent",
	["Lemonade Stand"] = "Maker_LemonadeStand",
	["Mini Golf"] = "Maker_MiniGolf",
	["Pizza Restaurant"] = "Maker_PizzaRestaurant",
	["Shopping Mall"] = "Maker_ShoppingMall",
	["Theme Park"] = "Maker_ThemePark",
	["Toy Shop"] = "Maker_ToyShop",
	["Unknown Maker"] = "Maker_UnknownMaker",
	["Vending Machine"] = "Maker_VendingMachine",
}
local DEBTS = {
	["Bank Loan"] = "Debt_BankLoan",
	["Car Loan"] = "Debt_CarLoan",
	["Credit Card"] = "Debt_CreditCard",
	["Other Debt"] = "Debt_OtherDebt",
}
-- in Config.Investments.CardCases order: COMMON, RARE, EPIC, LEGENDARY
local CARD_CASES = {
	["PokeBlox Card"] = { "Maker_PokeBloxCard", "Maker_PokeBloxCard_case2", "Maker_PokeBloxCard_case3", "Maker_PokeBloxCard_case4" },
	["Rare PokeBlox Card"] = { "Maker_RarePokeBloxCard", "Maker_RarePokeBloxCard_v2", "Maker_RarePokeBloxCard_v3", "Maker_RarePokeBloxCard_v4" },
	["Shiny PokeBlox Card"] = { "Maker_ShinyPokeBloxCard_case1", "Maker_ShinyPokeBloxCard_case2", "Maker_ShinyPokeBloxCard", "Maker_ShinyPokeBloxCard_case4" },
}
local CARD_DEFAULT_VALUE = {
	["PokeBlox Card"] = 500,
	["Rare PokeBlox Card"] = 8000,
	["Shiny PokeBlox Card"] = 20000,
}
local KIDS = {
	["255,90,90"] = "Kid",
	["90,200,255"] = "Kid_v2",
	["255,210,60"] = "Kid_v3",
	["150,230,110"] = "Kid_v4",
}

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

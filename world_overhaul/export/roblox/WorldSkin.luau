--[[
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

-- The locked dream's chains, LINK BY LINK (owner decision): Plots.luau addChains() makes "Chain" bars
-- (ModelKit.bar: Size = (0.35, 0.35, length), the length along the bar's local Z) and a padlock
-- ("PadlockBody", "PadlockHole", "PadlockShackle"). Every bar gets Dream_ChainSegment kit pieces
-- (2 links, 3 studs long along their local +Z, origin at one end) tiled end to end; the padlock gets
-- Dream_Padlock. Works for any dream size, because it follows the bars the game actually made.
local SEGMENT_LENGTH = 3
function WorldSkin.chains(folder: Instance)
	if not WorldSkin.ENABLED then
		return
	end
	for _, part in folder:GetChildren() do
		if part:IsA("BasePart") and not part:GetAttribute("WorldSkinNew") then
			if part.Name == "Chain" then
				local length = part.Size.Z
				local count = math.max(1, math.round(length / SEGMENT_LENGTH))
				local step = length / count -- each piece is scaled a little so the pieces fill the bar exactly
				for index = 0, count - 1 do
					WorldSkin.add(folder, "Dream_ChainSegment", part.CFrame * CFrame.new(0, 0, -length / 2 + index * step),
						step / SEGMENT_LENGTH)
				end
				hideOld(part)
			elseif part.Name == "PadlockBody" then
				WorldSkin.add(folder, "Dream_Padlock", part.CFrame)
				hideOld(part)
			elseif part.Name == "PadlockHole" or part.Name == "PadlockShackle" then
				hideOld(part)
			end
		end
	end
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

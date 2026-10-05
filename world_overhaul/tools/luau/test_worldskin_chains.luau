--[[
	test_worldskin_chains.luau - functional test of WorldSkin.chains (and the helpers it uses:
	WorldSkin.add, hideOld, cloneKit) on the Roblox API mock. Builds everything in memory and
	writes no files.

	usage: luaurun test_worldskin_chains.luau [world_overhaul dir] [game src dir] [--raw-clone]
	  --raw-clone  run WITHOUT the Clone shim below (shows what the bare mock does)

	What it does, for 3 fake dreams (2 sizes + a rotated one, and one that hits the "no ScaleTo" branch):
	1. builds the dream folder like Plots:syncDream (pedestal parts, the dream model) and runs
	   addChains() - a verbatim copy of Plots.luau addChains, checked against the game file below -
	   with the game's own ModelKit (loaded through the mock);
	2. calls WorldSkin.chains(folder) and checks:
	   (a) the Dream_ChainSegment copies of every Chain bar lie on the bar axis, are parallel to it
	       and cover it end to end (gaps/overlaps <= 0.05, total length = bar length +- 0.05);
	   (b) piece scale = step / 3, step = length / count, count = max(1, round(length / 3));
	   (c) every old Chain / PadlockBody / PadlockHole / PadlockShackle part has Transparency 1;
	   (d) one Dream_Padlock copy, its pivot at the PadlockBody CFrame;
	   (e) the other parts (pedestal, dream model incl. its own "Chain"/"PadlockBody" parts, the kit)
	       are untouched;
	   (f) calling chains() twice: are the pieces doubled? (a question, reported as such)
	Exit: error (non-zero) when a check (a)-(e) or an extra check fails; (f) is only reported.
]]

local positional, RAW_CLONE = {}, false
for _, a in arg do
	if a == "--raw-clone" then
		RAW_CLONE = true
	else
		table.insert(positional, a)
	end
end
local ROOT = positional[1] or "/home/user/SolScout/world_overhaul"
local GAME_SRC = positional[2] or "/home/user/game/Escape9to5/src"
local MOCK = ROOT .. "/tools/luau/roblox_mock.luau"
local SKIN = ROOT .. "/export/roblox/WorldSkin.luau"
local MODELKIT = GAME_SRC .. "/shared/Models/ModelKit.luau"
local PLOTS = GAME_SRC .. "/server/World/Plots.luau"

local R = __loadfile(MOCK, setmetatable({}, { __index = _G }))()
local Instance, Vector3, CFrame, Color3, Enum = R.Instance, R.Vector3, R.CFrame, R.Color3, R.Enum
local workspace = R.workspace

-------------------------------------------------------------------------------
-- MOCK SHIM (test-only, the mock file is not changed): roblox_mock's Instance:Clone() copies
-- properties, attributes, tags and children, but NOT a Model's WorldPivot (the mock keeps it in
-- the raw field _worldPivot) nor its ScaleTo scale (_scale). Real Roblox keeps WorldPivot on Clone
-- (it is a saved property), and WorldSkin depends on it: the kit piece's pivot is one END of the
-- piece. Without the shim every mock clone pivots at its bounding-box center.
-------------------------------------------------------------------------------
if not RAW_CLONE then
	local mt = getmetatable(Instance.new("Folder"))
	local baseIndex = mt.__index
	local rawClone = baseIndex(Instance.new("Folder"), "Clone")
	local function copyHidden(src, dst)
		rawset(dst, "_worldPivot", rawget(src, "_worldPivot"))
		rawset(dst, "_scale", rawget(src, "_scale"))
		local from, to = rawget(src, "_children"), rawget(dst, "_children")
		for i, child in from do
			copyHidden(child, to[i])
		end
	end
	local function clone(self)
		local copy = rawClone(self)
		copyHidden(self, copy)
		return copy
	end
	mt.__index = function(self, key)
		if key == "Clone" then
			return clone
		end
		return baseIndex(self, key)
	end
end

-------------------------------------------------------------------------------
-- Globals the game modules see (like dump_world.luau's G)
-------------------------------------------------------------------------------
local warnings = {}
local G = setmetatable({
	game = R.game,
	workspace = R.workspace,
	Workspace = R.workspace,
	Instance = Instance,
	Vector3 = Vector3,
	Vector2 = R.Vector2,
	CFrame = CFrame,
	Color3 = Color3,
	UDim = R.UDim,
	UDim2 = R.UDim2,
	Enum = Enum,
	task = R.task,
	typeof = R.typeof,
	warn = function(...)
		local parts = {}
		for i = 1, select("#", ...) do
			parts[i] = tostring((select(i, ...)))
		end
		table.insert(warnings, table.concat(parts, " "))
		print("[warn]", ...)
	end,
}, { __index = _G })

-------------------------------------------------------------------------------
-- Kit stubs in ServerStorage.WorldKit
-------------------------------------------------------------------------------
local ServerStorage = R.getService("ServerStorage")
local Kit = Instance.new("Folder")
Kit.Name = "WorldKit"
Kit.Parent = ServerStorage

local SEG_LEN = 3
local function kitPart(model, name, size, cframe)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = cframe
	p.Anchored = true
	p.Parent = model
	return p
end
-- Dream_ChainSegment: 2 links, local z 0..3, pivot (origin) at one end
local segKit = Instance.new("Model")
segKit.Name = "Dream_ChainSegment"
kitPart(segKit, "LinkA", Vector3.new(1, 1, 1.5), CFrame.new(0, 0, 0.75))
kitPart(segKit, "LinkB", Vector3.new(1, 1, 1.5), CFrame.new(0, 0, 2.25))
segKit.WorldPivot = CFrame.new()
segKit.Parent = Kit
-- Dream_Padlock: 3 x 2.6 x 1 body at the origin (pivot = body center) + a shackle on top, so the
-- pivot is NOT the bounding-box center (a pivot mistake would show)
local lockKit = Instance.new("Model")
lockKit.Name = "Dream_Padlock"
kitPart(lockKit, "Body", Vector3.new(3, 2.6, 1), CFrame.new())
kitPart(lockKit, "Shackle", Vector3.new(2.15, 1.6, 0.35), CFrame.new(0, 2.1, 0))
lockKit.WorldPivot = CFrame.new()
lockKit.Parent = Kit

-------------------------------------------------------------------------------
-- WorldSkin.luau, loaded like a ModuleScript next to WorldSkinPlacements (require -> {})
-------------------------------------------------------------------------------
local skinFolder = Instance.new("Folder")
skinFolder.Name = "WorldSkinFolder"
skinFolder.Parent = R.getService("ServerScriptService")
local skinScript = Instance.new("ModuleScript")
skinScript.Name = "WorldSkin"
skinScript.Parent = skinFolder
local placementsScript = Instance.new("ModuleScript")
placementsScript.Name = "WorldSkinPlacements"
placementsScript.Parent = skinFolder
-- WorldSkin reads Config.Investments.CardCases: ReplicatedStorage.Shared.Config -> the game's own Config
local shared = Instance.new("Folder")
shared.Name = "Shared"
shared.Parent = R.getService("ReplicatedStorage")
local configScript = Instance.new("ModuleScript")
configScript.Name = "Config"
configScript.Parent = shared
local Config = __loadfile(GAME_SRC .. "/shared/Config.luau", setmetatable({}, { __index = G }))()
local skinEnv = setmetatable({ script = skinScript }, { __index = G })
skinEnv.require = function(module)
	if module == placementsScript then
		return {}
	end
	if module == configScript then
		return Config
	end
	error("WorldSkin requires an unexpected module: " .. tostring(module))
end
local WorldSkin = __loadfile(SKIN, skinEnv)()

-- the game's own ModelKit (no requires)
local ModelKit = __loadfile(MODELKIT, setmetatable({}, { __index = G }))()
local C = { Gold = Color3.fromRGB(255, 200, 60), Dark = Color3.fromRGB(35, 35, 40) }

-------------------------------------------------------------------------------
-- VERBATIM copy of Plots.luau addChains (checked against the game file: "fidelity" below)
-------------------------------------------------------------------------------
local function addChains(folder: Instance, model: Model)
	local cframe, size = model:GetBoundingBox()
	local chain = Color3.fromRGB(70, 70, 80)
	local metal = { material = Enum.Material.Metal }
	local half = size / 2 + Vector3.new(0.4, 0.2, 0.4)
	local function corner(x: number, y: number, z: number): Vector3
		return (cframe * CFrame.new(x * half.X, y * half.Y, z * half.Z)).Position
	end
	-- An "X" of chains on every side, and a band around the middle.
	for _, side in { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } } do
		local sx, sz = side[1], side[2]
		local ax, az = if sx == 0 then 1 else sx, if sz == 0 then 1 else sz
		local bx, bz = if sx == 0 then -1 else sx, if sz == 0 then -1 else sz
		ModelKit.bar(folder :: any, "Chain", corner(ax, -1, az), corner(bx, 1, bz), 0.35, chain, metal)
		ModelKit.bar(folder :: any, "Chain", corner(bx, -1, bz), corner(ax, 1, az), 0.35, chain, metal)
		ModelKit.bar(folder :: any, "Chain", corner(ax, 0, az), corner(bx, 0, bz), 0.35, chain, metal)
	end
	-- Padlock on the front (-Z side).
	local front = cframe * CFrame.new(0, 0, -half.Z - 0.6)
	ModelKit.part(folder :: any, "PadlockBody", Vector3.new(3, 2.6, 1), front, C.Gold, { material = Enum.Material.Metal, reflectance = 0.2 })
	ModelKit.part(folder :: any, "PadlockHole", Vector3.new(0.5, 0.9, 0.1), front * CFrame.new(0, -0.2, -0.55), C.Dark)
	for _, x in { -0.9, 0.9 } do
		ModelKit.part(folder :: any, "PadlockShackle", Vector3.new(0.35, 1.6, 0.35), front * CFrame.new(x, 2, 0), chain, metal)
	end
	ModelKit.part(folder :: any, "PadlockShackle", Vector3.new(2.15, 0.35, 0.35), front * CFrame.new(0, 2.8, 0), chain, metal)
end

-------------------------------------------------------------------------------
-- Results
-------------------------------------------------------------------------------
local checks = {} -- key -> { ok = bool, notes = {} }
local order = {}
local function check(key, title)
	if not checks[key] then
		checks[key] = { ok = true, title = title, notes = {}, fails = {} }
		table.insert(order, key)
	end
	return checks[key]
end
local function note(key, text)
	table.insert(checks[key].notes, text)
end
local function fail(key, text)
	checks[key].ok = false
	if #checks[key].fails < 12 then
		table.insert(checks[key].fails, text)
	end
end
local function fmt(n)
	return string.format("%.4f", n)
end

-- fidelity: our addChains == the game's addChains (whitespace-normalized)
do
	check("fidelity", "addChains copy == Plots.luau addChains")
	local function extract(text)
		local start = string.find(text, "local function " .. "addChains(", 1, true)
		if not start then
			return nil
		end
		local stop = string.find(text, "\nend\n", start, true)
		return (string.gsub(string.sub(text, start, stop + 4), "%s+", " "))
	end
	local mine = extract(__readfile(debug.info(1, "s")))
	local game = extract(__readfile(PLOTS))
	if mine == nil or game == nil then
		fail("fidelity", "could not find addChains (mine: " .. tostring(mine ~= nil) .. ", Plots: " .. tostring(game ~= nil) .. ")")
	elseif mine ~= game then
		fail("fidelity", "the copy differs from " .. PLOTS .. ": update the copy in this test")
	else
		note("fidelity", "identical to " .. PLOTS .. " (whitespace-normalized)")
	end
end

-------------------------------------------------------------------------------
-- Helpers
-------------------------------------------------------------------------------
local function isOld(name)
	return name == "Chain" or name == "PadlockBody" or name == "PadlockHole" or name == "PadlockShackle"
end

local function cfDiff(a, b) -- max |difference| of position and of rotation entries
	local ac, bc = { a:GetComponents() }, { b:GetComponents() }
	local dp, dr = 0, 0
	for i = 1, 3 do
		dp = math.max(dp, math.abs(ac[i] - bc[i]))
	end
	for i = 4, 12 do
		dr = math.max(dr, math.abs(ac[i] - bc[i]))
	end
	return dp, dr
end

local function snapshot(part)
	local attrs = {}
	for k, v in part:GetAttributes() do
		table.insert(attrs, k .. "=" .. tostring(v))
	end
	table.sort(attrs)
	local s = part.Size
	return table.concat({
		part.Name,
		tostring(part.Parent),
		string.format("%.6f", part.Transparency),
		string.format("%.6f %.6f %.6f", s.X, s.Y, s.Z),
		string.format(string.rep("%.6f ", 12), part.CFrame:GetComponents()),
		tostring(part.CanCollide),
		table.concat(attrs, ","),
	}, " | ")
end

local function partsUnder(root)
	local out = {}
	for _, item in root:GetDescendants() do
		if item:IsA("BasePart") then
			table.insert(out, item)
		end
	end
	return out
end

local function countCopies(folder, name)
	local n = 0
	for _, child in folder:GetChildren() do
		if child.Name == name and child:IsA("Model") then
			n += 1
		end
	end
	return n
end

-------------------------------------------------------------------------------
-- One case
-------------------------------------------------------------------------------
local function runCase(label, dreamSize, dreamCFrame)
	local folder = Instance.new("Folder")
	folder.Name = "Dream_" .. label
	folder.Parent = workspace

	-- like syncDream: the pedestal (direct children), then the dream model, then addChains
	local bottom = dreamCFrame * CFrame.new(0, -dreamSize.Y / 2, 0)
	ModelKit.part(folder, "Part", Vector3.new(15, 1.5, 15), bottom * CFrame.new(0, -1.05, 0), Color3.fromRGB(240, 235, 225))
	ModelKit.part(folder, "Part", Vector3.new(15.4, 0.3, 15.4), bottom * CFrame.new(0, -0.15, 0), C.Gold)
	-- a direct-child new-look part named "Chain" (WorldSkinNew): must be skipped
	local newLook = ModelKit.part(folder, "Chain", Vector3.new(0.35, 0.35, 6), bottom * CFrame.new(0, -3, 0), C.Gold)
	newLook:SetAttribute("WorldSkinNew", true)

	local dream = Instance.new("Model")
	dream.Name = "Dream"
	ModelKit.part(dream, "Body", dreamSize, dreamCFrame, C.Gold)
	-- parts INSIDE the dream model with chain/padlock names (e.g. a bike chain): not direct children
	ModelKit.part(dream, "Chain", Vector3.new(0.3, 0.3, 2), dreamCFrame, C.Dark)
	ModelKit.part(dream, "PadlockBody", Vector3.new(1, 1, 1), dreamCFrame * CFrame.new(0, 1, 0), C.Dark)
	local faded = ModelKit.part(dream, "Glass", Vector3.new(1, 1, 1), dreamCFrame * CFrame.new(0, -1, 0), C.Dark)
	faded.Transparency = 0.4
	faded:SetAttribute("BaseTransparency", 0.4)
	dream.WorldPivot = dreamCFrame
	dream.Parent = folder

	local before = {}
	for _, child in folder:GetChildren() do
		before[child] = true
	end
	addChains(folder, dream)

	local bars, oldParts = {}, {}
	for _, child in folder:GetChildren() do
		if not before[child] then
			assert(isOld(child.Name), "addChains made an unexpected " .. child.Name)
			table.insert(oldParts, child)
			if child.Name == "Chain" then
				table.insert(bars, child)
			end
		end
	end
	local oldSnap = {}
	for _, p in oldParts do
		oldSnap[p] = { cframe = p.CFrame, size = p.Size, collide = p.CanCollide }
	end
	local others = {} -- every pre-existing part that chains() must not touch
	for _, p in partsUnder(folder) do
		if not oldSnap[p] then
			others[p] = snapshot(p)
		end
	end
	for _, p in partsUnder(Kit) do
		others[p] = snapshot(p)
	end
	local kitPivots = { seg = segKit:GetPivot(), lock = lockKit:GetPivot() }
	local body
	for _, p in oldParts do
		if p.Name == "PadlockBody" then
			body = p
		end
	end

	local warnBefore = #warnings
	WorldSkin.chains(folder)

	local segs, locks = {}, {}
	for _, child in folder:GetChildren() do
		if child.Name == "Dream_ChainSegment" then
			table.insert(segs, child)
		elseif child.Name == "Dream_Padlock" then
			table.insert(locks, child)
		end
	end

	-- extra: no warnings, copies are new-look models
	check("warnings", "no WorldSkin warnings (kit found)")
	if #warnings > warnBefore then
		fail("warnings", label .. ": " .. warnings[#warnings])
	end
	check("newlook", "copies: WorldSkinNew + BaseTransparency on every kit part, parented to the folder")
	for _, list in { segs, locks } do
		for _, copy in list do
			if copy.Parent ~= folder then
				fail("newlook", label .. ": copy not in the folder")
			end
			for _, p in partsUnder(copy) do
				if p:GetAttribute("WorldSkinNew") ~= true or p:GetAttribute("BaseTransparency") ~= 0 then
					fail("newlook", label .. ": " .. copy.Name .. "." .. p.Name .. " missing WorldSkinNew/BaseTransparency")
				end
			end
		end
	end

	-- (a) + (b): assign every segment copy to the bar whose axis it lies on
	check("a", "pieces on the bar axis, parallel, covering it end to end")
	check("b", "piece scale = step/3, count = max(1, round(length/3))")
	local perBar = {}
	for _, bar in bars do
		perBar[bar] = {}
	end
	local unassigned = 0
	for _, copy in segs do
		local best, bestParallel
		local info
		for _, bar in bars do
			local inv = bar.CFrame:Inverse()
			local half = bar.Size.Z / 2
			local onAxis, parallel = true, true
			local zmin, zmax = math.huge, -math.huge
			for _, p in partsUnder(copy) do
				local rel = inv * p.CFrame
				if math.abs(rel.X) > 0.05 or math.abs(rel.Y) > 0.05 or rel.Z < -half - 0.05 or rel.Z > half + 0.05 then
					onAxis = false
				end
				if rel.ZVector.Z < 1 - 1e-6 or rel.XVector.X < 1 - 1e-6 then
					parallel = false
				end
				for _, q in R.corners(p) do
					local z = (inv * q).Z
					zmin, zmax = math.min(zmin, z), math.max(zmax, z)
				end
			end
			if onAxis and (best == nil or (parallel and not bestParallel)) then
				best, bestParallel = bar, parallel
				info = { copy = copy, zmin = zmin, zmax = zmax, parallel = parallel }
			end
		end
		if best then
			table.insert(perBar[best], info)
		else
			unassigned += 1
		end
	end
	if unassigned > 0 then
		fail("a", label .. ": " .. unassigned .. " of " .. #segs .. " Dream_ChainSegment copies lie on no bar axis")
	end

	local worstGap, worstEnd, worstTotal, worstScale = 0, 0, 0, 0
	local skipped, lengths = 0, {}
	for barIndex, bar in bars do
		local length = bar.Size.Z
		local count = math.max(1, math.round(length / SEG_LEN))
		local step = length / count
		local want = step / SEG_LEN
		table.insert(lengths, string.format("%.2f->%dx%.4f", length, count, want))
		local list = perBar[bar]
		table.sort(list, function(x, y)
			return x.zmin < y.zmin
		end)
		if #list ~= count then
			fail("a", string.format("%s bar %d (L=%.3f): %d pieces, expected %d", label, barIndex, length, #list, count))
			fail("b", string.format("%s bar %d (L=%.3f): %d pieces, expected count %d", label, barIndex, length, #list, count))
		end
		if #list > 0 then
			local total = 0
			for i, item in list do
				if not item.parallel then
					fail("a", string.format("%s bar %d piece %d: not parallel to the bar", label, barIndex, i))
				end
				total += item.zmax - item.zmin
				if i > 1 then
					local gap = math.abs(item.zmin - list[i - 1].zmax)
					worstGap = math.max(worstGap, gap)
					if gap > 0.05 then
						fail("a", string.format("%s bar %d: gap/overlap %.4f between pieces %d and %d", label, barIndex, gap, i - 1, i))
					end
				end
				-- (b) scale: measured length / 3 and the model's ScaleTo factor
				local measured = (item.zmax - item.zmin) / SEG_LEN
				local err = math.abs(measured - want)
				worstScale = math.max(worstScale, err)
				if err > 1e-3 + 1e-9 then
					fail("b", string.format("%s bar %d piece %d: scale %.5f, expected step/3 = %.5f", label, barIndex, i, measured, want))
				end
				local applied = item.copy:GetScale()
				if math.abs(want - 1) > 1e-3 and math.abs(applied - want) > 1e-9 then
					fail("b", string.format("%s bar %d piece %d: ScaleTo factor %.5f, expected %.5f", label, barIndex, i, applied, want))
				end
				for _, p in partsUnder(item.copy) do
					local sz = p.Size
					if math.abs(sz.Z - 1.5 * applied) > 1e-6 or math.abs(sz.X - applied) > 1e-6 then
						fail("b", string.format("%s bar %d piece %d: part size not uniformly scaled", label, barIndex, i))
					end
				end
				if math.abs(want - 1) <= 1e-3 and math.abs(want - 1) > 1e-12 then
					skipped += 1
				end
			end
			local endErr = math.max(math.abs(list[1].zmin + length / 2), math.abs(list[#list].zmax - length / 2))
			worstEnd = math.max(worstEnd, endErr)
			if endErr > 0.05 then
				fail("a", string.format("%s bar %d: ends off by %.4f (first %.4f, last %.4f, bar +-%.4f)", label, barIndex, endErr,
					list[1].zmin, list[#list].zmax, length / 2))
			end
			worstTotal = math.max(worstTotal, math.abs(total - length))
			if math.abs(total - length) > 0.05 then
				fail("a", string.format("%s bar %d: pieces total %.4f, bar %.4f", label, barIndex, total, length))
			end
		end
	end
	note("a", string.format("%s: %d bars, %d pieces; worst gap/overlap %s, worst end error %s, worst total error %s",
		label, #bars, #segs, fmt(worstGap), fmt(worstEnd), fmt(worstTotal)))
	note("b", string.format("%s: worst scale error %.6f; %d piece(s) not ScaleTo'd (|step/3-1| <= 1e-3 branch); bars %s",
		label, worstScale, skipped, table.concat(lengths, " ")))
	-- nothing placed on the new-look "Chain"
	for _, copy in segs do
		local rel = newLook.CFrame:Inverse() * copy:GetPivot()
		if math.abs(rel.X) < 0.05 and math.abs(rel.Y) < 0.05 then
			fail("e", label .. ": a chain piece was placed on the WorldSkinNew 'Chain' part")
		end
	end

	-- (c) old parts hidden, collision/frame kept, old transparency remembered
	check("c", "old Chain/Padlock* parts Transparency 1 (frame, size, collision kept)")
	local hidden = 0
	for _, p in oldParts do
		if p.Transparency ~= 1 then
			fail("c", string.format("%s: %s Transparency %s", label, p.Name, tostring(p.Transparency)))
		else
			hidden += 1
		end
		local s = oldSnap[p]
		local dp, dr = cfDiff(p.CFrame, s.cframe)
		if dp > 1e-9 or dr > 1e-9 or p.Size ~= s.size or p.CanCollide ~= s.collide then
			fail("c", label .. ": " .. p.Name .. " moved/resized/collision changed")
		end
		if p:GetAttribute("WorldSkinOldTransparency") ~= 0 then
			fail("c", label .. ": " .. p.Name .. " WorldSkinOldTransparency = " .. tostring(p:GetAttribute("WorldSkinOldTransparency")))
		end
	end
	note("c", string.format("%s: %d/%d old parts hidden (%d Chain, %d padlock parts)", label, hidden, #oldParts, #bars, #oldParts - #bars))

	-- (d) one padlock, pivot at the PadlockBody CFrame
	check("d", "one Dream_Padlock, pivot = PadlockBody CFrame")
	if #locks ~= 1 then
		fail("d", label .. ": " .. #locks .. " Dream_Padlock copies")
	end
	if #locks >= 1 and body then
		local dp, dr = cfDiff(locks[1]:GetPivot(), body.CFrame)
		local kitBody = locks[1]:FindFirstChild("Body")
		local bp, br = cfDiff(kitBody.CFrame, body.CFrame)
		if dp > 1e-4 or dr > 1e-6 or bp > 1e-4 or br > 1e-6 then
			fail("d", string.format("%s: pivot off by pos %.5f rot %.6f; kit body off by pos %.5f rot %.6f", label, dp, dr, bp, br))
		end
		if math.abs(locks[1]:GetScale() - 1) > 1e-9 or kitBody.Size ~= Vector3.new(3, 2.6, 1) then
			fail("d", label .. ": the padlock was scaled")
		end
		note("d", string.format("%s: pivot error pos %.2e rot %.2e (kit body part error pos %.2e)", label, dp, dr, bp))
	end

	-- (e) everything else untouched
	check("e", "other parts (pedestal, dream model, new-look 'Chain', kit) untouched")
	local changed, total = 0, 0
	for p, snap in others do
		total += 1
		if snapshot(p) ~= snap then
			changed += 1
			fail("e", label .. ": changed: " .. snapshot(p) .. "  (was " .. snap .. ")")
		end
	end
	local sd, sr = cfDiff(segKit:GetPivot(), kitPivots.seg)
	local ld, lr = cfDiff(lockKit:GetPivot(), kitPivots.lock)
	if sd + sr + ld + lr > 1e-12 or segKit:GetScale() ~= 1 or lockKit:GetScale() ~= 1 then
		fail("e", label .. ": a kit model in WorldKit was moved or scaled")
	end
	note("e", string.format("%s: %d/%d other parts unchanged", label, total - changed, total))

	-- (f) a second call
	check("f", "calling chains() twice does not double the pieces (question)")
	local segs1, locks1 = countCopies(folder, "Dream_ChainSegment"), countCopies(folder, "Dream_Padlock")
	local oldAttr = {}
	for _, p in oldParts do
		oldAttr[p] = p:GetAttribute("WorldSkinOldTransparency")
	end
	WorldSkin.chains(folder)
	local segs2, locks2 = countCopies(folder, "Dream_ChainSegment"), countCopies(folder, "Dream_Padlock")
	local attrKept = true
	for _, p in oldParts do
		if p:GetAttribute("WorldSkinOldTransparency") ~= oldAttr[p] or p.Transparency ~= 1 then
			attrKept = false
		end
	end
	if segs2 ~= segs1 or locks2 ~= locks1 then
		fail("f", string.format("%s: 2nd call: Dream_ChainSegment %d -> %d, Dream_Padlock %d -> %d", label, segs1, segs2, locks1, locks2))
	end
	note("f", string.format("%s: ChainSegment %d -> %d, Padlock %d -> %d after a 2nd call; old parts stay hidden and keep WorldSkinOldTransparency: %s",
		label, segs1, segs2, locks1, locks2, tostring(attrKept)))
end

-------------------------------------------------------------------------------
-- Cases
-------------------------------------------------------------------------------
-- A: a 13-stud-ish dream (Props.dream size 13), axis-aligned, on the pedestal like syncDream
runCase("A_13x9x11", Vector3.new(13, 9, 11), CFrame.new(0, 1.8 + 4.5, -9))
-- B: tall and thin, rotated (yaw 37 deg + 8 deg tilt) - rotated dream CFrame
runCase("B_6.2x14.5x4.1_rot", Vector3.new(6.2, 14.5, 4.1), CFrame.new(40, 9, 25) * CFrame.Angles(math.rad(8), math.rad(37), 0))
-- C: the middle band is 15.0008 long -> step/3 = 1.00005: the "no ScaleTo" branch (|scale-1| <= 1e-3)
runCase("C_14.2008x3x29.2_yaw180", Vector3.new(14.2008, 3, 29.2), CFrame.new(-30, 3, 60) * CFrame.Angles(0, math.pi, 0))

-- extra: ENABLED = false -> chains() does nothing
do
	check("disabled", "WorldSkin.ENABLED = false: chains() is a no-op")
	local folder = Instance.new("Folder")
	folder.Parent = workspace
	local dream = Instance.new("Model")
	ModelKit.part(dream, "Body", Vector3.new(8, 8, 8), CFrame.new(0, 4, 0), C.Gold)
	dream.Parent = folder
	addChains(folder, dream)
	local n = #folder:GetChildren()
	WorldSkin.ENABLED = false
	WorldSkin.chains(folder)
	WorldSkin.ENABLED = true
	local visible = 0
	for _, p in partsUnder(folder) do
		if p.Transparency < 1 then
			visible += 1
		end
	end
	if #folder:GetChildren() ~= n or visible ~= #partsUnder(folder) then
		fail("disabled", "chains() changed the folder while disabled")
	end
	note("disabled", string.format("%d children before and after, %d/%d parts still visible", n, visible, #partsUnder(folder)))
end

-------------------------------------------------------------------------------
-- Report
-------------------------------------------------------------------------------
print(string.format("WorldSkin.chains test (%s)", if RAW_CLONE then "RAW mock Clone, no shim" else "with Clone/WorldPivot shim"))
local failed = 0
for _, key in order do
	local c = checks[key]
	local status = if c.ok then "PASS" elseif key == "f" then "QUESTION" else "FAIL"
	if not c.ok and key ~= "f" then
		failed += 1
	end
	print(string.format("[%s] %s: %s", status, key, c.title))
	for _, text in c.notes do
		print("    " .. text)
	end
	for _, text in c.fails do
		print("    ! " .. text)
	end
end
if failed > 0 then
	error(failed .. " check(s) failed")
end
print("all checks (a)-(e) + extras passed")

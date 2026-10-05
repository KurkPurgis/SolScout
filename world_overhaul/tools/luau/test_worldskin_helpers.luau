--[[
	test_worldskin_helpers.luau - functional test of the rest of WorldSkin (export/roblox/WorldSkin.luau)
	and of the Step 4 command-bar script in IMPORT_PLAN.md, on the Roblox API mock. In memory (the Step 4 snippet
	is compiled through one temp file, /tmp/worldskin_step4_snippet.luau).

	usage: luaurun test_worldskin_helpers.luau [world_overhaul dir] [game src dir]

	1. step4      the Step 4 script, verbatim from IMPORT_PLAN.md, on a fake WorldKit: every glow mesh
	              (`_Glow_GOLD_T100`, `_Glow_RED_T45`, `_Glow_GLOW_WARM`) gets its color and transparency, a
	              bad glow name only warns, and EVERY kit after it is still set up (collision off, pivot, box)
	2. names      makerTemplate / debtTemplate / kidTemplate against the game code: every Money Maker and debt
	              builder name has its own kit model, PokeBlox cards pick the case of Props.cardCase(value),
	              School Loan the number of books of debtBuilders["School Loan"], the 4 KID_SHIRTS 4 kids;
	              every name returned is a model that was built (data/model_status.json)
	3. missing    a missing kit model hides nothing (object, stretched, context, chains)
	4. context    one call with two keys (workplace + furniture): both lists placed, old parts hidden
	5. glow       setGlow(nearest(...)) turns on only that desk's glow shell, the desk body stays as it is
	6. show       show(): the podium board's kit copy shows/hides, the old board stays hidden;
	              without a kit copy it behaves like the old line 158
	7. nokit      without ServerStorage.WorldKit: ENABLED = false, every call is a no-op
	Exit: error (non-zero) when a check fails.
]]

local ROOT = arg[1] or "/home/user/SolScout/world_overhaul"
local GAME_SRC = arg[2] or "/home/user/game/Escape9to5/src"
local R = __loadfile(ROOT .. "/tools/luau/roblox_mock.luau", setmetatable({}, { __index = _G }))()
local Instance, Vector3, CFrame, Color3, Enum = R.Instance, R.Vector3, R.CFrame, R.Color3, R.Enum

-- Clone shim (same as test_worldskin_chains.luau): real Roblox keeps a Model's WorldPivot on Clone
do
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
	mt.__index = function(self, key)
		if key == "Clone" then
			return function(this)
				local copy = rawClone(this)
				copyHidden(this, copy)
				return copy
			end
		end
		return baseIndex(self, key)
	end
end

local warnings = {}
local G = setmetatable({
	game = R.game,
	workspace = R.workspace,
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
	end,
}, { __index = _G })

local failures, passes = {}, 0
local function expect(name, ok, detail)
	if ok then
		passes += 1
	else
		table.insert(failures, name .. ": " .. tostring(detail))
	end
end

local ServerStorage = R.getService("ServerStorage")
local ReplicatedStorage = R.getService("ReplicatedStorage")
local planText = __readfile(ROOT .. "/IMPORT_PLAN.md")
local statusText = __readfile(ROOT .. "/data/model_status.json")
local propsText = __readfile(GAME_SRC .. "/server/World/Props.luau")
local plotsText = __readfile(GAME_SRC .. "/server/World/Plots.luau")
local function built(template)
	return string.find(statusText, '\n "' .. template .. '": {', 1, true) ~= nil
end

local function part(parent, name, size, cframe, transparency, className)
	local p = Instance.new(className or "Part")
	p.Name = name
	p.Size = size
	p.CFrame = cframe
	p.Transparency = transparency or 0
	p.Anchored = true
	p.Parent = parent
	return p
end
local function model(parent, name, pivot)
	local m = Instance.new("Model")
	m.Name = name
	m.WorldPivot = pivot or CFrame.new()
	m.Parent = parent
	return m
end

-------------------------------------------------------------------------------
-- 1. step4: the command-bar script from IMPORT_PLAN.md, verbatim
-------------------------------------------------------------------------------
do
	local code = string.match(planText, "## Step 4.-```lua\n(.-)```")
	expect("step4 found", code ~= nil, "no ```lua block under ## Step 4 in IMPORT_PLAN.md")
	local kit = Instance.new("Folder")
	kit.Name = "WorldKit"
	kit.Parent = ServerStorage
	local names = {
		{ "Bad", { "Bad_Glow_NOTACOLOR" } }, -- first: a bad name must not stop the loop
		{ "AuctionRoom_BidderDesk", { "AuctionRoom_BidderDesk", "AuctionRoom_BidderDesk_Glow_GOLD_T100" } },
		{ "Lobby_RoomBooth", { "Lobby_RoomBooth", "Lobby_RoomBooth_Glow_RED_T45" } },
		{ "AuctionRoom_Lamp", { "AuctionRoom_Lamp", "AuctionRoom_Lamp_Glow_GLOW_WARM" } },
		{ "Maker_PokeBloxCard", { "Maker_PokeBloxCard", "Maker_PokeBloxCard_Glass" } },
	}
	for index, entry in names do
		local m = model(kit, entry[1], CFrame.new(index * 10, 3, 0)) -- importer pivot: somewhere else
		for _, meshName in entry[2] do
			part(m, meshName, Vector3.new(2, 2, 2), CFrame.new(1, 1, 1), 0, "MeshPart")
		end
	end
	if code then
		-- the runner compiles files only: the snippet goes through one temp file
		local tmp = "/tmp/worldskin_step4_snippet.luau"
		__writefile(tmp, code)
		local ok, err = pcall(__loadfile(tmp, setmetatable({}, { __index = G })))
		expect("step4 runs", ok, err)
		local pal = string.match(planText, "local GLOW = {(.-)\n}")
		local function rgb(key)
			local r, g, b = string.match(pal, "\t" .. key .. " = Color3.fromRGB%((%d+), (%d+), (%d+)%)")
			return Color3.fromRGB(tonumber(r), tonumber(g), tonumber(b))
		end
		for _, m in kit:GetChildren() do
			local identity = true
			for i, v in { m.WorldPivot:GetComponents() } do
				identity = identity and math.abs(v - ({ 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1 })[i]) < 1e-12
			end
			expect("step4 pivot " .. m.Name, identity, m.WorldPivot)
			expect("step4 box " .. m.Name, m:GetAttribute("BoxMin") ~= nil and m:GetAttribute("BoxMax") ~= nil, "no BoxMin/BoxMax")
			for _, p in m:GetChildren() do
				expect("step4 collision " .. p.Name, p.CanCollide == false and p.CanQuery == false and p.CanTouch == false, "still collides")
			end
		end
		local function get(name)
			for _, m in kit:GetChildren() do
				local p = m:FindFirstChild(name)
				if p then
					return p
				end
			end
		end
		local desk = get("AuctionRoom_BidderDesk_Glow_GOLD_T100")
		expect("step4 T100", desk.Transparency == 1 and desk.Color == rgb("GOLD") and desk.Material == Enum.Material.Neon,
			string.format("T %s color %s", tostring(desk.Transparency), tostring(desk.Color)))
		local booth = get("Lobby_RoomBooth_Glow_RED_T45")
		expect("step4 T45", math.abs(booth.Transparency - 0.45) < 1e-9 and booth.Color == rgb("RED"), booth.Transparency)
		local lamp = get("AuctionRoom_Lamp_Glow_GLOW_WARM")
		expect("step4 GLOW_WARM", math.abs(lamp.Transparency - 0.35) < 1e-9 and lamp.Color == rgb("GLOW_WARM"), lamp.Transparency)
		local glass = get("Maker_PokeBloxCard_Glass")
		expect("step4 glass", glass.Material == Enum.Material.Glass and math.abs(glass.Transparency - 0.3) < 1e-9, glass.Material)
		local body = get("Maker_PokeBloxCard")
		expect("step4 body", body:FindFirstChildOfClass("SurfaceAppearance") ~= nil, "no SurfaceAppearance")
		local warned = false
		for _, w in warnings do
			warned = warned or string.find(w, "Bad_Glow_NOTACOLOR", 1, true) ~= nil
		end
		expect("step4 warns on a bad glow name", warned, "no warning")
	end
	kit:Destroy()
	table.clear(warnings)
end

-------------------------------------------------------------------------------
-- WorldSkin with a test WorldKit and test Placements
-------------------------------------------------------------------------------
local shared = Instance.new("Folder")
shared.Name = "Shared"
shared.Parent = ReplicatedStorage
local configScript = Instance.new("ModuleScript")
configScript.Name = "Config"
configScript.Parent = shared
local Config = __loadfile(GAME_SRC .. "/shared/Config.luau", setmetatable({}, { __index = G }))()

local Placements = {
	Room = {
		{ template = "Desk", frame = CFrame.new(-5, 0, 0), scale = 1 },
		{ template = "Desk", frame = CFrame.new(5, 0, 0), scale = 1 },
		{ template = "Board", frame = CFrame.new(0, 0, -10), scale = 1 },
	},
	["Workplace:TEST"] = { { template = "Desk", frame = CFrame.new(0, 0, 0), scale = 1 } },
	["Furnish:TEST"] = { { template = "Board", frame = CFrame.new(0, 0, 4), scale = 1 } },
	Broken = {
		{ template = "Desk", frame = CFrame.new(), scale = 1 },
		{ template = "NotInTheKit", frame = CFrame.new(), scale = 1 },
	},
}

local function loadSkin()
	local folder = Instance.new("Folder")
	folder.Parent = R.getService("ServerScriptService")
	local skinScript = Instance.new("ModuleScript")
	skinScript.Name = "WorldSkin"
	skinScript.Parent = folder
	local placementsScript = Instance.new("ModuleScript")
	placementsScript.Name = "WorldSkinPlacements"
	placementsScript.Parent = folder
	local env = setmetatable({ script = skinScript }, { __index = G })
	env.require = function(module)
		if module == placementsScript then
			return Placements
		elseif module == configScript then
			return Config
		end
		error("unexpected require " .. tostring(module))
	end
	return __loadfile(ROOT .. "/export/roblox/WorldSkin.luau", env)()
end

local Kit = Instance.new("Folder")
Kit.Name = "WorldKit"
Kit.Parent = ServerStorage
do
	local desk = model(Kit, "Desk")
	part(desk, "Desk", Vector3.new(4, 3, 1.5), CFrame.new(0, 1.5, 0))
	part(desk, "Desk_Glow_GOLD_T100", Vector3.new(4.2, 3.2, 1.7), CFrame.new(0, 1.5, 0), 1)
	local board = model(Kit, "Board")
	part(board, "Board", Vector3.new(16, 18, 0.4), CFrame.new(0, 9, 0))
	part(board, "Board_Glow_GOLD_T55", Vector3.new(16, 0.3, 0.3), CFrame.new(0, 18, 0), 0.55)
	for _, name in { "Kid", "Dream_ChainSegment", "Dream_Padlock" } do
		local m = model(Kit, name)
		part(m, name, Vector3.new(1, 1, 1), CFrame.new())
	end
	local loan = model(Kit, "Debt_CreditCard")
	part(loan, "Debt_CreditCard", Vector3.new(3, 2, 1), CFrame.new(0, 1, 0))
	loan:SetAttribute("BoxMin", Vector3.new(-1.5, 0, -0.5))
	loan:SetAttribute("BoxMax", Vector3.new(1.5, 2, 0.5))
end
local WorldSkin = loadSkin()
expect("loaded enabled", WorldSkin.ENABLED == true, WorldSkin.ENABLED)

-------------------------------------------------------------------------------
-- 2. names
-------------------------------------------------------------------------------
do
	for name in string.gmatch(propsText, 'makerBuilders%["([^"]+)"%] = function') do
		local t = WorldSkin.makerTemplate(name, nil)
		expect("maker " .. name, t ~= "Maker_UnknownMaker" and built(t), t)
	end
	expect("maker unknown", WorldSkin.makerTemplate("No Such Maker", 100) == "Maker_UnknownMaker", "")
	expect("maker unknown built", built("Maker_UnknownMaker"), "")
	-- PokeBlox: the case that Props.cardCase(value) picks, for values around every boundary
	local cases = Config.Investments.CardCases
	local defaults = { ["PokeBlox Card"] = 500, ["Rare PokeBlox Card"] = 8000, ["Shiny PokeBlox Card"] = 20000 }
	for name, default in defaults do
		expect("card default " .. name, string.find(propsText, 'makerBuilders%["' .. name:gsub("%p", "%%%0") ..
			'"%] = function%(model, base, value%)%s*pokeBloxCard%(model, base, "[^"]+", Color3%.fromRGB%([%d, ]+%), %a+, value or ' ..
			default .. "%)") ~= nil, "the builder's default value is not " .. default)
		local seen = {}
		local values = { 0, 999.99, 1000, 9999, 10000, 29999, 30000, 1e7, nil }
		for i = 1, 9 do
			local value = values[i]
			local worth = value or default
			local want
			for index, case in cases do
				if worth < case.below then
					want = index
					break
				end
			end
			want = want or #cases
			local t = WorldSkin.makerTemplate(name, value)
			seen[want] = seen[want] or t
			expect("card " .. name .. " " .. tostring(value), built(t) and seen[want] == t, t)
		end
		local distinct = {}
		for _, t in seen do
			distinct[t] = true
		end
		local n = 0
		for _ in distinct do
			n += 1
		end
		expect("card " .. name .. " 4 cases, 4 models", n == 4, n)
	end
	-- debts
	for name in string.gmatch(propsText, 'debtBuilders%["([^"]+)"%] = function') do
		local t = WorldSkin.debtTemplate(name, 20000)
		expect("debt " .. name, t ~= "Debt_OtherDebt" and built(t), t)
	end
	expect("debt crate", WorldSkin.debtTemplate("Something Else", 500) == "Debt_OtherDebt" and built("Debt_OtherDebt"), "")
	expect("school loan formula in the game", string.find(propsText,
		"local books = math.clamp(2 + math.floor(amount / 15000), 2, 7)", 1, true) ~= nil, "debtBuilders School Loan changed")
	for amount = 0, 150000, 2500 do
		local books = math.clamp(2 + math.floor(amount / 15000), 2, 7)
		local t = WorldSkin.debtTemplate("School Loan", amount)
		local want = if books == 3 then "Debt_SchoolLoan" else "Debt_SchoolLoan_books" .. books
		expect("school loan " .. amount, t == want and built(t), t)
	end
	-- kids: the 4 shirts of Plots.luau KID_SHIRTS
	local block = string.match(plotsText, "local KID_SHIRTS = {(.-)\n}")
	local kids, n = {}, 0
	for r, g, b in string.gmatch(block or "", "Color3%.fromRGB%((%d+), (%d+), (%d+)%)") do
		n += 1
		local t = WorldSkin.kidTemplate(Color3.fromRGB(tonumber(r), tonumber(g), tonumber(b)))
		expect("kid shirt " .. n, built(t) and not kids[t], t)
		kids[t] = true
	end
	expect("4 kid shirts", n == 4, n)
end

-------------------------------------------------------------------------------
-- 3. missing kit models hide nothing
-------------------------------------------------------------------------------
local function oldModel(name)
	local m = model(R.workspace, name)
	part(m, "Old", Vector3.new(2, 2, 2), CFrame.new(0, 1, 0))
	return m
end
local function allVisible(root)
	for _, p in root:GetDescendants() do
		if p:IsA("BasePart") and not p:GetAttribute("WorldSkinNew") and p.Transparency ~= 0 then
			return false
		end
	end
	return true
end
do
	local m = oldModel("Maker")
	WorldSkin.object(m, "NotInTheKit", CFrame.new())
	expect("object missing kit", allVisible(m) and #m:GetChildren() == 1, "old part hidden / something added")
	WorldSkin.object(m, nil, CFrame.new())
	expect("object nil template", allVisible(m), "old part hidden")
	local d = oldModel("Debt")
	WorldSkin.stretched(d, "NotInTheKit", CFrame.new())
	expect("stretched missing kit", allVisible(d) and #d:GetChildren() == 1, "")
	local room = Instance.new("Folder")
	room.Parent = R.workspace
	part(room, "Old", Vector3.new(2, 2, 2), CFrame.new())
	WorldSkin.context("Broken", CFrame.new(), room)
	expect("context missing kit", allVisible(room) and #room:GetChildren() == 1, "")
	-- chains with the segment kit missing
	local seg = Kit:FindFirstChild("Dream_ChainSegment")
	seg.Parent = nil
	local dream = Instance.new("Folder")
	dream.Parent = R.workspace
	part(dream, "Chain", Vector3.new(0.35, 0.35, 9), CFrame.new())
	part(dream, "PadlockBody", Vector3.new(3, 2.6, 1), CFrame.new(0, 0, -2))
	WorldSkin.chains(dream)
	expect("chains missing kit", allVisible(dream) and #dream:GetChildren() == 2, "")
	seg.Parent = Kit
	-- the kit is there: object() works and the old parts hide
	WorldSkin.object(m, "Kid", CFrame.new(3, 0, 0))
	expect("object with kit", not allVisible(m) and m:FindFirstChild("Kid") ~= nil, "")
	local w = 0
	for _, text in warnings do
		if string.find(text, "NotInTheKit", 1, true) then
			w += 1
		end
	end
	expect("missing kits warn", w >= 3, w)
end

-------------------------------------------------------------------------------
-- 4. context: two keys on one folder
-------------------------------------------------------------------------------
do
	local folder = Instance.new("Folder")
	folder.Parent = R.workspace
	part(folder, "Wall", Vector3.new(4, 4, 1), CFrame.new(100, 2, 0))
	part(folder, "Oven", Vector3.new(2, 2, 2), CFrame.new(100, 1, 4))
	local base = CFrame.new(100, 0, 0) * CFrame.Angles(0, math.rad(90), 0)
	WorldSkin.context({ "Workplace:TEST", "Furnish:TEST" }, base, folder)
	local desk, board = folder:FindFirstChild("Desk"), folder:FindFirstChild("Board")
	expect("context both lists", desk ~= nil and board ~= nil, "")
	expect("context old hidden", folder:FindFirstChild("Wall").Transparency == 1 and folder:FindFirstChild("Oven").Transparency == 1, "")
	if board then
		local d = (board:GetPivot().Position - (base * CFrame.new(0, 0, 4)).Position).Magnitude
		expect("context frame", d < 1e-6, d)
	end
end

-------------------------------------------------------------------------------
-- 5. glow (AuctionRoom:highlight) and 6. show (PodiumRoom:fillBoard)
-------------------------------------------------------------------------------
do
	local room = Instance.new("Folder")
	room.Parent = R.workspace
	local base = CFrame.new(0, 50, 0)
	local podiums = {
		part(room, "Podium1", Vector3.new(4, 3, 1.5), base * CFrame.new(-5, 1.5, 0)),
		part(room, "Podium2", Vector3.new(4, 3, 1.5), base * CFrame.new(5, 1.5, 0)),
	}
	local oldBoard = part(room, "OldBoard", Vector3.new(16, 18, 0.4), base * CFrame.new(0, 9, -10))
	WorldSkin.context("Room", base, room)
	-- the game's highlight loop, with the Step 6 line
	local function highlight(index)
		for podiumIndex, podium in podiums do
			local isTop = podiumIndex == index
			podium.Color = if isTop then Color3.fromRGB(255, 200, 60) else Color3.fromRGB(60, 40, 35)
			WorldSkin.setGlow(WorldSkin.nearest(room, "Desk", podium.Position), isTop)
		end
	end
	local function deskState(x)
		local desk = WorldSkin.nearest(room, "Desk", (base * CFrame.new(x, 0, 0)).Position)
		return desk:FindFirstChild("Desk").Transparency, desk:FindFirstChild("Desk_Glow_GOLD_T100").Transparency
	end
	local b1, s1 = deskState(-5)
	expect("glow off at start", b1 == 0 and s1 == 1, string.format("%s %s", b1, s1))
	highlight(2)
	local b1b, s1b = deskState(-5)
	local b2, s2 = deskState(5)
	expect("glow only desk 2", b1b == 0 and s1b == 1 and b2 == 0 and math.abs(s2 - 0.35) < 1e-9,
		string.format("desk1 %s/%s desk2 %s/%s", b1b, s1b, b2, s2))
	highlight(nil)
	local _, s2c = deskState(5)
	expect("glow off again", s2c == 1, s2c)
	expect("old podiums stay hidden", podiums[1].Transparency == 1 and podiums[2].Transparency == 1, "")

	local board = room:FindFirstChild("Board")
	local function boardState()
		return board:FindFirstChild("Board").Transparency, board:FindFirstChild("Board_Glow_GOLD_T55").Transparency
	end
	WorldSkin.show(oldBoard, room, "Board", false)
	local t1, g1 = boardState()
	expect("show false", t1 == 1 and g1 == 1 and oldBoard.Transparency == 1, string.format("%s %s %s", t1, g1, oldBoard.Transparency))
	WorldSkin.show(oldBoard, room, "Board", true)
	local t2, g2 = boardState()
	expect("show true", t2 == 0 and math.abs(g2 - 0.55) < 1e-9 and oldBoard.Transparency == 1,
		string.format("%s %s %s", t2, g2, oldBoard.Transparency))
	-- no kit copy (WorldSkin off): exactly the old line 158
	local plain = Instance.new("Folder")
	plain.Parent = R.workspace
	local lone = part(plain, "OldBoard", Vector3.new(16, 18, 0.4), CFrame.new())
	WorldSkin.show(lone, plain, "Board", false)
	expect("show old false", lone.Transparency == 1, lone.Transparency)
	WorldSkin.show(lone, plain, "Board", true)
	expect("show old true", lone.Transparency == 0, lone.Transparency)
	WorldSkin.setVisible(nil, true)
	WorldSkin.setGlow(nil, true)
	expect("nil roots", true, "")
end

-------------------------------------------------------------------------------
-- 7. no WorldKit folder
-------------------------------------------------------------------------------
do
	Kit.Parent = nil
	table.clear(warnings)
	local Off = loadSkin()
	expect("nokit disabled", Off.ENABLED == false, Off.ENABLED)
	expect("nokit warns", #warnings == 1 and string.find(warnings[1], "WorldKit", 1, true) ~= nil, warnings[1])
	local folder = Instance.new("Folder")
	folder.Parent = R.workspace
	part(folder, "Wall", Vector3.new(4, 4, 1), CFrame.new())
	part(folder, "Chain", Vector3.new(0.35, 0.35, 9), CFrame.new())
	Off.context("Room", CFrame.new(), folder)
	Off.chains(folder)
	local m = oldModel("Maker2")
	Off.object(m, "Desk", CFrame.new())
	expect("nokit no-ops", allVisible(folder) and #folder:GetChildren() == 2 and allVisible(m), "")
	Kit.Parent = ServerStorage
end

print(string.format("%d checks passed, %d failed", passes, #failures))
for _, f in failures do
	print("FAIL " .. f)
end
if #failures > 0 then
	error("WorldSkin helper checks failed")
end

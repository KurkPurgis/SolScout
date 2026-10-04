--[[
	dump_world.luau - runs the game's own (unchanged) world code on the Roblox mock and writes
	every Part to JSON.

	usage: luaurun dump_world.luau <mock path> <project src dir> <manifest file> <out json>

	What gets built:
	1. Workspace.Baseplate (from default.project.json)
	2. The server start script (init.server.luau -> Lobby.start()): lobby hall + 4 cities with
	   plaza, auction room and podium room each.
	3. "Snapshot": city 1 in the middle of a game: 8 workplaces (one per job) with kids, debts,
	   Money Makers, a FOR SALE model, the floating dream and investment showcases.
	4. "Catalog" (far away, NOT part of the real world): things that only appear later in a game:
	   the luxury Fast Track workplace, the locked/won dream pedestal, every Money Maker and
	   investment at normal size, every debt model at small and big size, the kid, all dreams.
]]

local mockPath, srcDir, manifestPath, outPath = arg[1], arg[2], arg[3], arg[4]
local env0 = setmetatable({}, { __index = _G })
local R = __loadfile(mockPath, env0)()

-------------------------------------------------------------------------------
-- Globals every game script sees
-------------------------------------------------------------------------------
local G = {
	game = R.game,
	workspace = R.workspace,
	Workspace = R.workspace,
	Instance = R.Instance,
	Vector3 = R.Vector3,
	Vector2 = R.Vector2,
	CFrame = R.CFrame,
	Color3 = R.Color3,
	UDim = R.UDim,
	UDim2 = R.UDim2,
	Enum = R.Enum,
	RaycastParams = R.RaycastParams,
	OverlapParams = R.OverlapParams,
	NumberRange = R.NumberRange,
	NumberSequence = R.NumberSequence,
	ColorSequence = R.ColorSequence,
	TweenInfo = R.TweenInfo,
	BrickColor = R.BrickColor,
	PhysicalProperties = R.PhysicalProperties,
	Random = R.Random,
	task = R.task,
	typeof = R.typeof,
	warn = function(...)
		print("[warn]", ...)
	end,
	tick = os.clock,
	wait = function()
		return 0
	end,
	spawn = function() end,
	delay = function() end,
}
setmetatable(G, { __index = _G })

local cache = {}
local function runScript(scriptInstance)
	local file = rawget(scriptInstance, "_file")
	local env = setmetatable({ script = scriptInstance }, { __index = G })
	env.require = function(module)
		if cache[module] == nil then
			local result = runScript(module)
			cache[module] = { result }
		end
		return cache[module][1]
	end
	local fn = __loadfile(file, env)
	return fn()
end
G.require = function(module)
	if cache[module] == nil then
		cache[module] = { runScript(module) }
	end
	return cache[module][1]
end

-------------------------------------------------------------------------------
-- The Rojo tree (default.project.json)
-------------------------------------------------------------------------------
local function node(className, name, parent, file)
	local item = R.Instance.new(className)
	item.Name = name
	if file then
		rawset(item, "_file", file)
	end
	item.Parent = parent
	return item
end

-- manifest: one relative path per line, e.g. "server/World/Props.luau"
local manifest = {}
for line in string.gmatch(__readfile(manifestPath), "[^\n]+") do
	table.insert(manifest, line)
end

local ReplicatedStorage = R.getService("ReplicatedStorage")
local ServerScriptService = R.getService("ServerScriptService")

local roots = {
	shared = node("Folder", "Shared", ReplicatedStorage),
	server = node("Script", "Server", ServerScriptService, srcDir .. "/server/init.server.luau"),
}
local folders = {}
local function folderFor(dir) -- "server/World"
	if roots[dir] then
		return roots[dir]
	end
	if folders[dir] then
		return folders[dir]
	end
	local parentDir, name = string.match(dir, "^(.*)/([^/]+)$")
	local item = node("Folder", name, folderFor(parentDir))
	folders[dir] = item
	return item
end

local scripts = {}
for _, path in manifest do
	local dir, fileName = string.match(path, "^(.*)/([^/]+)$")
	if dir and (string.sub(dir, 1, 6) == "shared" or string.sub(dir, 1, 6) == "server") then
		if fileName ~= "init.server.luau" then
			local parent = folderFor(dir)
			local name, kind = string.match(fileName, "^(.-)%.(server)%.luau$")
			if name then
				scripts[name] = node("Script", name, parent, srcDir .. "/" .. path)
			else
				name = string.match(fileName, "^(.-)%.luau$")
				node("ModuleScript", name, parent, srcDir .. "/" .. path)
			end
		end
	end
end

-- Workspace.Baseplate exactly like default.project.json
local baseplate = R.Instance.new("Part")
baseplate.Name = "Baseplate"
baseplate.Anchored = true
baseplate.Color = R.Color3.new(0.36, 0.62, 0.3)
baseplate.Locked = true
baseplate.Size = R.Vector3.new(512, 20, 512)
baseplate.CFrame = R.CFrame.new(0, -10, 0)
baseplate.Material = R.Enum.Material.Grass
baseplate.Parent = R.workspace

-------------------------------------------------------------------------------
-- Wrap the builder functions (the game code is NOT changed: we only replace fields in the
-- module tables, so every part remembers which builder call made it and with which base).
-------------------------------------------------------------------------------
local World0 = roots.server.World
local Props0 = G.require(World0.Props)
local ModelKit0 = G.require(ReplicatedStorage.Shared.Models.ModelKit)
local Plaza0 = G.require(World0.Plaza)
local Plots0 = G.require(World0.Plots)
local Themes0 = G.require(World0.Themes)
local AuctionRoom0 = G.require(World0.AuctionRoom)
local PodiumRoom0 = G.require(World0.PodiumRoom)
local Config0 = G.require(ReplicatedStorage.Shared.Config)

local function wrap(tbl, key, labelFn)
	local original = tbl[key]
	tbl[key] = function(...)
		local label, base = labelFn(...)
		R.pushGroup(label, base)
		local results = table.pack(original(...))
		R.popGroup()
		return table.unpack(results, 1, results.n)
	end
end
wrap(Props0, "tree", function(_, base) return "Tree", base end)
wrap(Props0, "palm", function(_, base) return "Palm", base end)
wrap(Props0, "car", function(_, base) return "Car", base end)
wrap(Props0, "kid", function(_, base) return "Kid", base end)
wrap(Props0, "debtModel", function(_, base, name) return "Debt:" .. name, base end)
wrap(Props0, "moneyMaker", function(_, base, name) return "Maker:" .. name, base end)
wrap(Props0, "dream", function(_, base, name) return "Dream:" .. name, base end)
wrap(Props0, "sign", function(_, base, pos) return "Sign", base * R.CFrame.new(pos.X, pos.Y, pos.Z) end)
wrap(Props0, "floatingLabel", function() return "Label", nil end)
wrap(ModelKit0, "palm", function(_, _, base) return "Palm", base end)
wrap(Plaza0, "new", function(origin) return "Plaza", R.CFrame.new(origin.X, origin.Y, origin.Z) end)
wrap(AuctionRoom0, "new", function(origin) return "AuctionRoom", R.CFrame.new(origin.X, origin.Y + Config0.World.AuctionRoomHeight, origin.Z) end)
wrap(PodiumRoom0, "new", function(origin) return "PodiumRoom", R.CFrame.new(origin.X, origin.Y + Config0.World.PodiumHeight, origin.Z) end)
wrap(Plots0, "buildWorkplace", function(self, theme) return "Workplace:" .. theme.title, self.base end)
wrap(Plots0, "buildSign", function(self) return "NameSign", self.base end)
wrap(Plots0, "syncKids", function(self) return "Kids", self.base end)
wrap(Plots0, "syncDebts", function(self) return "Debts", self.base end)
wrap(Plots0, "syncMakers", function(self) return "MoneyMakers", self.base end)
wrap(Plots0, "syncOffer", function(self) return "ForSale", self.base end)
wrap(Plots0, "syncDream", function(self) return "DreamArea", self.base end)
wrap(Plots0, "syncCollection", function(self) return "Collection", self.base end)
for name, theme in Themes0 do
	if type(theme) == "table" and theme.furnish then
		wrap(theme, "furnish", function(_, base) return "Furnish:" .. theme.title, base end)
	end
end

-------------------------------------------------------------------------------
-- 1+2. Run the server like Roblox does
-------------------------------------------------------------------------------
R.pushGroup("Lobby", R.CFrame.new())
runScript(roots.server)
R.popGroup()
for name, item in scripts do
	runScript(item)
end

-------------------------------------------------------------------------------
-- 3. Snapshot: city 1 in the middle of a game
-------------------------------------------------------------------------------
local Shared = ReplicatedStorage.Shared
local World = roots.server.World
local Config = G.require(Shared.Config)
local Plots = G.require(World.Plots)
local Props = G.require(World.Props)
local DreamModels = G.require(Shared.Models.DreamModels)

local NAMES = { "Mia", "Leo", "Ava", "Max", "Zoe", "Sam", "Ella", "Noah" }
local function fakePlayer(index)
	return { Name = "Player" .. index, DisplayName = NAMES[index] or ("Player" .. index), UserId = 1000 + index }
end

local DREAMS = Config.Dreams
local PLAN = {
	{ makers = { "Lemonade Stand", "Food Truck" }, offer = { "Car Wash", 4000, 900 } },
	{ makers = { "Vending Machine", "Toy Shop" }, offer = { "Gold Coin", 4000, 0, "Investment" }, invest = { { "Gold Coin", 4000 }, { "PokeBlox Card", 500 } } },
	{ makers = { "Apartment", "Mini Golf" }, offer = { "PokeBlox Card", 500, 0, "Investment" } },
	{ makers = { "House to Rent", "Pizza Restaurant" }, offer = { "Hotel", 20000, 12000 } },
	{ makers = { "Coffee Shop", "Bowling Alley" }, offer = { "Gold Bar", 15000, 0, "Investment" }, invest = { { "Rare PokeBlox Card", 8000 }, { "Gold Bar", 15000 }, { "Shiny PokeBlox Card", 20000 }, { "Gold Treasure Chest", 50000 } } },
	{ makers = { "Game Studio", "Shopping Mall" }, offer = { "Rare PokeBlox Card", 8000, 0, "Investment" } },
	{ makers = { "Apartment Building", "Theme Park" }, offer = { "Gold Treasure Chest", 50000, 0, "Investment" } },
	{ makers = { "Lemonade Stand", "Car Wash", "Vending Machine" }, offer = { "Shiny PokeBlox Card", 20000, 0, "Investment" } },
}

local function viewFor(index, job, extra)
	local plan = PLAN[index]
	local makers = {}
	for _, name in plan.makers do
		table.insert(makers, { name = name, freeMoney = 100 })
	end
	local investments = {}
	for _, item in plan.invest or {} do
		table.insert(investments, { name = item[1], value = item[2] })
	end
	local dream = DREAMS[(index - 1) % #DREAMS + 1]
	local view = {
		name = NAMES[index],
		children = job.children,
		debts = job.debts,
		makers = makers,
		offer = { name = plan.offer[1], price = plan.offer[2], freeMoney = plan.offer[3], type = plan.offer[4] },
		dream = { name = dream.name, icon = dream.icon, price = dream.price },
		dreamProgress = 0.15 * index,
		progress = 0.1 * index,
		escaped = false,
		won = false,
		bankrupt = false,
		investments = investments,
	}
	if extra then
		for k, v in extra do
			view[k] = v
		end
	end
	return view
end

local city1 = R.workspace:FindFirstChild("City_1")
local origin1 = R.Vector3.new(1 * Config.Rooms.CitySpacing, 0, 0)
for index, job in Config.Jobs do
	local plot = Plots.new(index, origin1, city1.Plots, fakePlayer(index), job.name, function() end)
	plot:sync(viewFor(index, job))
end

-------------------------------------------------------------------------------
-- 4. Catalog (not part of the real world, only for the inventory and as size templates)
-------------------------------------------------------------------------------
local catalog = R.Instance.new("Folder")
catalog.Name = "Catalog"
catalog.Parent = R.workspace
local catalogOrigin = R.Vector3.new(-1400, 0, 0)

-- a: the luxury Fast Track workplace with the locked dream (plot 1) and a won dream (plot 2)
local lux = R.Instance.new("Folder")
lux.Name = "FastTrack"
lux.Parent = catalog
do
	local job = Config.Jobs[1]
	local plot = Plots.new(1, catalogOrigin, lux, fakePlayer(1), job.name, function() end)
	plot:sync(viewFor(1, job))
	plot:sync(viewFor(1, job, { escaped = true, debts = {}, makers = {}, offer = nil }))
	local plot2 = Plots.new(2, catalogOrigin, lux, fakePlayer(2), Config.Jobs[2].name, function() end)
	plot2:sync(viewFor(2, Config.Jobs[2], { escaped = true, won = true, debts = {}, makers = {}, offer = nil }))
end

-- b: every Money Maker and investment at normal size, in a row, facing -Z
local makersFolder = R.Instance.new("Folder")
makersFolder.Name = "MoneyMakers"
makersFolder.Parent = catalog
local allMakers = {}
for _, list in { Config.Deals.RatRace.Small, Config.Deals.RatRace.Big, Config.Deals.FastTrack.Small, Config.Deals.FastTrack.Big } do
	for _, deal in list do
		table.insert(allMakers, deal)
	end
end
table.insert(allMakers, { name = "Unknown Maker", price = 1000 })
local makerRow = R.CFrame.new(catalogOrigin + R.Vector3.new(-200, 0, 200))
for index, deal in allMakers do
	local spot = makerRow * R.CFrame.new((index - 1) * 16, 0, 0)
	Props.moneyMaker(makersFolder, spot, deal.name, deal.price)
end
-- PokeBlox cards in every case color
local cases = R.Instance.new("Folder")
cases.Name = "CardCases"
cases.Parent = catalog
for index, value in { 500, 8000, 20000, 60000 } do
	Props.moneyMaker(cases, makerRow * R.CFrame.new((index - 1) * 16, 0, 30), "Rare PokeBlox Card", value)
end

-- c: every debt model, small and big
local debtsFolder = R.Instance.new("Folder")
debtsFolder.Name = "Debts"
debtsFolder.Parent = catalog
local debtRow = R.CFrame.new(catalogOrigin + R.Vector3.new(-200, 0, 260))
local debtKinds = { { "Credit Card", 3000, 20000 }, { "Car Loan", 6000, 20000 }, { "School Loan", 20000, 80000 }, { "Bank Loan", 1000, 20000 }, { "Other Debt", 3000, 60000 } }
for index, kind in debtKinds do
	Props.debtModel(debtsFolder, debtRow * R.CFrame.new((index - 1) * 14, 0, 0), kind[1], kind[2])
	Props.debtModel(debtsFolder, debtRow * R.CFrame.new((index - 1) * 14, 0, 16), kind[1], kind[3])
end

-- d: a kid
Props.kid(catalog, R.CFrame.new(catalogOrigin + R.Vector3.new(-220, 0, 260)), R.Color3.fromRGB(255, 90, 90))

-- e: every dream at full size (like the Model Preview area)
local dreamsFolder = R.Instance.new("Folder")
dreamsFolder.Name = "Dreams"
dreamsFolder.Parent = catalog
for index, dream in DREAMS do
	local model = DreamModels[dream.name].build()
	model:PivotTo(R.CFrame.new(catalogOrigin + R.Vector3.new(-200 + (index - 1) * 70, 0, 340)))
	model.Parent = dreamsFolder
end

-------------------------------------------------------------------------------
-- Dump
-------------------------------------------------------------------------------
local function num(x)
	if x ~= x or x == math.huge or x == -math.huge then
		return "0"
	end
	local s = string.format("%.5f", x)
	s = string.gsub(s, "0+$", "")
	s = string.gsub(s, "%.$", "")
	if s == "-0" then
		s = "0"
	end
	return s
end
local function str(s)
	s = tostring(s)
	s = string.gsub(s, "\\", "\\\\")
	s = string.gsub(s, '"', '\\"')
	s = string.gsub(s, "\n", "\\n")
	s = string.gsub(s, "\r", "")
	s = string.gsub(s, "\t", "\\t")
	return '"' .. s .. '"'
end
local function encode(value)
	local t = R.typeof(value)
	if t == "nil" then
		return "null"
	elseif t == "number" then
		return num(value)
	elseif t == "boolean" then
		return tostring(value)
	elseif t == "string" then
		return str(value)
	elseif t == "Vector3" then
		return "[" .. num(value.X) .. "," .. num(value.Y) .. "," .. num(value.Z) .. "]"
	elseif t == "Color3" then
		return "[" .. num(value.R * 255) .. "," .. num(value.G * 255) .. "," .. num(value.B * 255) .. "]"
	elseif t == "CFrame" then
		local parts = { value:GetComponents() }
		for i, x in parts do
			parts[i] = num(x)
		end
		return "[" .. table.concat(parts, ",") .. "]"
	elseif t == "EnumItem" then
		return str(value.Name)
	elseif t == "Instance" then
		return str(value:GetFullName())
	elseif t == "table" then
		if #value > 0 or next(value) == nil then
			local out = {}
			for _, item in value do
				table.insert(out, encode(item))
			end
			return "[" .. table.concat(out, ",") .. "]"
		end
		local out = {}
		for k, item in value do
			if type(k) == "string" and k ~= "__type" then
				table.insert(out, str(k) .. ":" .. encode(item))
			end
		end
		table.sort(out)
		return "{" .. table.concat(out, ",") .. "}"
	end
	return str(tostring(value))
end

local ids = {}
local nextId = 0
local lines = {}
local PART_PROPS = { "Size", "CFrame", "Color", "Material", "Transparency", "Reflectance", "Anchored", "CanCollide", "CanQuery", "CanTouch", "CastShadow", "Shape" }

local function visit(item)
	nextId += 1
	ids[item] = nextId
	local class = rawget(item, "_class")
	local entry = {
		id = nextId,
		parent = ids[rawget(item, "_parent")] or 0,
		class = class,
		name = item.Name,
		path = item:GetFullName(),
	}
	local tags = {}
	for tag in rawget(item, "_tags") do
		table.insert(tags, tag)
	end
	if #tags > 0 then
		entry.tags = tags
	end
	if next(rawget(item, "_attributes")) then
		entry.attributes = rawget(item, "_attributes")
	end
	if rawget(item, "_chain") then
		entry.chain = rawget(item, "_chain")
	end
	local groups = rawget(item, "_groups")
	if groups and #groups > 0 then
		local list = {}
		for _, g in groups do
			table.insert(list, { label = g.label, seq = g.seq, base = g.base })
		end
		entry.groups = list
	end
	local props = rawget(item, "_props")
	if item:IsA("BasePart") then
		for _, key in PART_PROPS do
			entry[key] = props[key]
		end
	elseif class == "Model" then
		entry.PrimaryPart = props.PrimaryPart
		entry.Pivot = item:GetPivot()
	elseif class == "TextLabel" then
		entry.Text = props.Text
		entry.TextColor3 = props.TextColor3
		entry.Font = props.Font
	elseif class == "SurfaceGui" then
		entry.Face = props.Face
	elseif class == "BillboardGui" then
		entry.Size = props.Size
		entry.MaxDistance = props.MaxDistance
	elseif class == "PointLight" then
		entry.Range = props.Range
		entry.Brightness = props.Brightness
		entry.Color = props.Color
	elseif class == "ProximityPrompt" then
		entry.ActionText = props.ActionText
		entry.ObjectText = props.ObjectText
	elseif class == "SpawnLocation" then
		entry.Neutral = props.Neutral
	end
	table.insert(lines, encode(entry))
	for _, child in rawget(item, "_children") do
		visit(child)
	end
end
for _, child in rawget(R.workspace, "_children") do
	visit(child)
end
__writefile(outPath, "[\n" .. table.concat(lines, ",\n") .. "\n]\n")
print("instances:", nextId)

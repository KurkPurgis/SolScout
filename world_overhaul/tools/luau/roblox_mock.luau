--[[
	roblox_mock.luau - a small, faithful-enough copy of the Roblox engine API, so the game's
	world-building scripts can run outside Roblox and we can dump every Part they create.

	Only what the server world code uses is implemented:
	Vector3, Vector2, CFrame (full rotation math), Color3, UDim/UDim2, Enum, Instance (properties,
	children, attributes, tags), Model pivots / ScaleTo / GetBoundingBox, services, a fake raycast.

	Every BasePart remembers the call chain that created it (file:line list), so the dump can
	group parts into logical objects (a tree, a fountain, a wall...).
]]

local M = {}

-------------------------------------------------------------------------------
-- Vector3
-------------------------------------------------------------------------------
local V3 = {}
V3.__index = function(self, key)
	if key == "Magnitude" then
		return math.sqrt(self.X * self.X + self.Y * self.Y + self.Z * self.Z)
	elseif key == "Unit" then
		local m = math.sqrt(self.X * self.X + self.Y * self.Y + self.Z * self.Z)
		if m == 0 then
			return M.Vector3.new(0, 0, 0)
		end
		return M.Vector3.new(self.X / m, self.Y / m, self.Z / m)
	elseif key == "x" then
		return self.X
	elseif key == "y" then
		return self.Y
	elseif key == "z" then
		return self.Z
	end
	return V3[key]
end
local function isV3(value)
	return type(value) == "table" and getmetatable(value) == V3
end
V3.__add = function(a, b)
	return M.Vector3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z)
end
V3.__sub = function(a, b)
	return M.Vector3.new(a.X - b.X, a.Y - b.Y, a.Z - b.Z)
end
V3.__mul = function(a, b)
	if type(a) == "number" then
		return M.Vector3.new(a * b.X, a * b.Y, a * b.Z)
	elseif type(b) == "number" then
		return M.Vector3.new(a.X * b, a.Y * b, a.Z * b)
	end
	return M.Vector3.new(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
V3.__div = function(a, b)
	if type(b) == "number" then
		return M.Vector3.new(a.X / b, a.Y / b, a.Z / b)
	end
	return M.Vector3.new(a.X / b.X, a.Y / b.Y, a.Z / b.Z)
end
V3.__unm = function(a)
	return M.Vector3.new(-a.X, -a.Y, -a.Z)
end
V3.__eq = function(a, b)
	return a.X == b.X and a.Y == b.Y and a.Z == b.Z
end
V3.__tostring = function(a)
	return string.format("%g, %g, %g", a.X, a.Y, a.Z)
end
function V3.Dot(a, b)
	return a.X * b.X + a.Y * b.Y + a.Z * b.Z
end
function V3.Cross(a, b)
	return M.Vector3.new(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X)
end
function V3.Lerp(a, b, t)
	return a + (b - a) * t
end
function V3.Abs(a)
	return M.Vector3.new(math.abs(a.X), math.abs(a.Y), math.abs(a.Z))
end
function V3.Max(a, b)
	return M.Vector3.new(math.max(a.X, b.X), math.max(a.Y, b.Y), math.max(a.Z, b.Z))
end
function V3.Min(a, b)
	return M.Vector3.new(math.min(a.X, b.X), math.min(a.Y, b.Y), math.min(a.Z, b.Z))
end
M.Vector3 = {
	new = function(x, y, z)
		return setmetatable({ X = x or 0, Y = y or 0, Z = z or 0, __type = "Vector3" }, V3)
	end,
}
M.Vector3.zero = M.Vector3.new(0, 0, 0)
M.Vector3.one = M.Vector3.new(1, 1, 1)
M.Vector3.xAxis = M.Vector3.new(1, 0, 0)
M.Vector3.yAxis = M.Vector3.new(0, 1, 0)
M.Vector3.zAxis = M.Vector3.new(0, 0, 1)
M.isV3 = isV3

-------------------------------------------------------------------------------
-- Vector2, UDim, UDim2 (only stored, never used for geometry)
-------------------------------------------------------------------------------
M.Vector2 = {
	new = function(x, y)
		return { X = x or 0, Y = y or 0, __type = "Vector2" }
	end,
}
M.Vector2.zero = M.Vector2.new(0, 0)
M.UDim = {
	new = function(s, o)
		return { Scale = s or 0, Offset = o or 0, __type = "UDim" }
	end,
}
M.UDim2 = {
	new = function(xs, xo, ys, yo)
		return { X = M.UDim.new(xs, xo), Y = M.UDim.new(ys, yo), __type = "UDim2" }
	end,
	fromScale = function(x, y)
		return { X = M.UDim.new(x, 0), Y = M.UDim.new(y, 0), __type = "UDim2" }
	end,
	fromOffset = function(x, y)
		return { X = M.UDim.new(0, x), Y = M.UDim.new(0, y), __type = "UDim2" }
	end,
}

-------------------------------------------------------------------------------
-- Color3
-------------------------------------------------------------------------------
local C3 = {}
C3.__index = C3
C3.__eq = function(a, b)
	return a.R == b.R and a.G == b.G and a.B == b.B
end
function C3.Lerp(a, b, t)
	return M.Color3.new(a.R + (b.R - a.R) * t, a.G + (b.G - a.G) * t, a.B + (b.B - a.B) * t)
end
function C3.ToHex(a)
	return string.format("%02X%02X%02X", math.floor(a.R * 255 + 0.5), math.floor(a.G * 255 + 0.5), math.floor(a.B * 255 + 0.5))
end
M.Color3 = {
	new = function(r, g, b)
		return setmetatable({ R = r or 0, G = g or 0, B = b or 0, __type = "Color3" }, C3)
	end,
	fromRGB = function(r, g, b)
		return setmetatable({ R = (r or 0) / 255, G = (g or 0) / 255, B = (b or 0) / 255, __type = "Color3" }, C3)
	end,
}
M.Color3.fromHSV = function(h, s, v)
	local i = math.floor(h * 6)
	local f = h * 6 - i
	local p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
	i = i % 6
	if i == 0 then
		return M.Color3.new(v, t, p)
	elseif i == 1 then
		return M.Color3.new(q, v, p)
	elseif i == 2 then
		return M.Color3.new(p, v, t)
	elseif i == 3 then
		return M.Color3.new(p, q, v)
	elseif i == 4 then
		return M.Color3.new(t, p, v)
	end
	return M.Color3.new(v, p, q)
end

-------------------------------------------------------------------------------
-- CFrame: position p + rotation matrix (rows r[1..3][1..3]).
-- Columns are RightVector, UpVector and -LookVector, like Roblox.
-------------------------------------------------------------------------------
local CF = {}
local function cf(px, py, pz, m)
	return setmetatable({ px = px, py = py, pz = pz, m = m, __type = "CFrame" }, CF)
end
local IDENTITY = { 1, 0, 0, 0, 1, 0, 0, 0, 1 } -- row-major m11 m12 m13 m21 ...
local function mmul(a, b)
	local r = table.create(9, 0)
	for i = 0, 2 do
		for j = 0, 2 do
			r[i * 3 + j + 1] = a[i * 3 + 1] * b[j + 1] + a[i * 3 + 2] * b[3 + j + 1] + a[i * 3 + 3] * b[6 + j + 1]
		end
	end
	return r
end
local function isCF(value)
	return type(value) == "table" and getmetatable(value) == CF
end
M.isCF = isCF
CF.__index = function(self, key)
	local m = self.m
	if key == "Position" or key == "p" then
		return M.Vector3.new(self.px, self.py, self.pz)
	elseif key == "X" then
		return self.px
	elseif key == "Y" then
		return self.py
	elseif key == "Z" then
		return self.pz
	elseif key == "LookVector" then
		return M.Vector3.new(-m[3], -m[6], -m[9])
	elseif key == "RightVector" or key == "XVector" then
		return M.Vector3.new(m[1], m[4], m[7])
	elseif key == "UpVector" or key == "YVector" then
		return M.Vector3.new(m[2], m[5], m[8])
	elseif key == "ZVector" then
		return M.Vector3.new(m[3], m[6], m[9])
	elseif key == "Rotation" then
		return cf(0, 0, 0, m)
	end
	return CF[key]
end
CF.__mul = function(a, b)
	if isCF(b) then
		local m = mmul(a.m, b.m)
		local am = a.m
		local x = am[1] * b.px + am[2] * b.py + am[3] * b.pz + a.px
		local y = am[4] * b.px + am[5] * b.py + am[6] * b.pz + a.py
		local z = am[7] * b.px + am[8] * b.py + am[9] * b.pz + a.pz
		return cf(x, y, z, m)
	end
	-- CFrame * Vector3 = point in world space
	local am = a.m
	return M.Vector3.new(
		am[1] * b.X + am[2] * b.Y + am[3] * b.Z + a.px,
		am[4] * b.X + am[5] * b.Y + am[6] * b.Z + a.py,
		am[7] * b.X + am[8] * b.Y + am[9] * b.Z + a.pz
	)
end
CF.__add = function(a, b)
	return cf(a.px + b.X, a.py + b.Y, a.pz + b.Z, a.m)
end
CF.__sub = function(a, b)
	return cf(a.px - b.X, a.py - b.Y, a.pz - b.Z, a.m)
end
CF.__tostring = function(a)
	return string.format("CFrame(%g, %g, %g)", a.px, a.py, a.pz)
end
function CF.Inverse(a)
	local m = a.m
	local t = { m[1], m[4], m[7], m[2], m[5], m[8], m[3], m[6], m[9] }
	local x = -(t[1] * a.px + t[2] * a.py + t[3] * a.pz)
	local y = -(t[4] * a.px + t[5] * a.py + t[6] * a.pz)
	local z = -(t[7] * a.px + t[8] * a.py + t[9] * a.pz)
	return cf(x, y, z, t)
end
function CF.GetComponents(a)
	local m = a.m
	return a.px, a.py, a.pz, m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9]
end
CF.components = CF.GetComponents
function CF.PointToWorldSpace(a, v)
	return a * v
end
function CF.PointToObjectSpace(a, v)
	return a:Inverse() * v
end
function CF.VectorToWorldSpace(a, v)
	return a.Rotation * v
end
function CF.VectorToObjectSpace(a, v)
	return a.Rotation:Inverse() * v
end
function CF.ToWorldSpace(a, b)
	return a * b
end
function CF.ToObjectSpace(a, b)
	return a:Inverse() * b
end
function CF.ToEulerAnglesXYZ(a)
	local m = a.m
	local y = math.asin(math.clamp(m[3], -1, 1))
	local x = math.atan2(-m[6], m[9])
	local z = math.atan2(-m[2], m[1])
	return x, y, z
end
function CF.Lerp(a, b, t)
	-- only used for positions in this code base
	return cf(a.px + (b.px - a.px) * t, a.py + (b.py - a.py) * t, a.pz + (b.pz - a.pz) * t, if t < 0.5 then a.m else b.m)
end

local function lookAt(at, target, up)
	up = up or M.Vector3.new(0, 1, 0)
	local look = (target - at).Unit
	if look.Magnitude == 0 then
		return cf(at.X, at.Y, at.Z, IDENTITY)
	end
	local right = look:Cross(up)
	if right.Magnitude < 1e-6 then
		right = look:Cross(M.Vector3.new(0, 0, if look.Y > 0 then -1 else 1))
	end
	right = right.Unit
	local up2 = right:Cross(look).Unit
	-- columns: right, up2, -look
	return cf(at.X, at.Y, at.Z, { right.X, up2.X, -look.X, right.Y, up2.Y, -look.Y, right.Z, up2.Z, -look.Z })
end

local function rx(a)
	local c, s = math.cos(a), math.sin(a)
	return { 1, 0, 0, 0, c, -s, 0, s, c }
end
local function ry(a)
	local c, s = math.cos(a), math.sin(a)
	return { c, 0, s, 0, 1, 0, -s, 0, c }
end
local function rz(a)
	local c, s = math.cos(a), math.sin(a)
	return { c, -s, 0, s, c, 0, 0, 0, 1 }
end

M.CFrame = {
	new = function(a, b, c, ...)
		if a == nil then
			return cf(0, 0, 0, IDENTITY)
		end
		if isV3(a) then
			if b ~= nil and isV3(b) then
				return lookAt(a, b)
			end
			return cf(a.X, a.Y, a.Z, IDENTITY)
		end
		local extra = { ... }
		if #extra == 9 then
			return cf(a, b, c, extra)
		end
		return cf(a, b, c, IDENTITY)
	end,
	lookAt = lookAt,
	Angles = function(x, y, z)
		return cf(0, 0, 0, mmul(mmul(rx(x or 0), ry(y or 0)), rz(z or 0)))
	end,
	fromAxisAngle = function(axis, angle)
		local u = axis.Unit
		local c, s, t = math.cos(angle), math.sin(angle), 1 - math.cos(angle)
		local x, y, z = u.X, u.Y, u.Z
		return cf(0, 0, 0, {
			t * x * x + c, t * x * y - s * z, t * x * z + s * y,
			t * x * y + s * z, t * y * y + c, t * y * z - s * x,
			t * x * z - s * y, t * y * z + s * x, t * z * z + c,
		})
	end,
	fromMatrix = function(pos, vx, vy, vz)
		vz = vz or vx:Cross(vy)
		return cf(pos.X, pos.Y, pos.Z, { vx.X, vy.X, vz.X, vx.Y, vy.Y, vz.Y, vx.Z, vy.Z, vz.Z })
	end,
}
M.CFrame.fromEulerAnglesXYZ = M.CFrame.Angles
M.CFrame.identity = M.CFrame.new()

-------------------------------------------------------------------------------
-- Enum: Enum.Material.Grass -> a unique item { Name = "Grass", EnumType = "Material" }
-------------------------------------------------------------------------------
local enumItems = {}
M.Enum = setmetatable({}, {
	__index = function(_, enumType)
		local items = setmetatable({}, {
			__index = function(t, name)
				local key = enumType .. "." .. name
				local item = enumItems[key]
				if item == nil then
					item = setmetatable({ Name = name, EnumType = enumType, __type = "EnumItem" }, {
						__tostring = function()
							return "Enum." .. key
						end,
					})
					enumItems[key] = item
				end
				return item
			end,
		})
		rawset(M.Enum, enumType, items)
		return items
	end,
})

-------------------------------------------------------------------------------
-- Signals (events never fire here)
-------------------------------------------------------------------------------
local function newSignal()
	return {
		Connect = function()
			return { Disconnect = function() end, Connected = true }
		end,
		Once = function()
			return { Disconnect = function() end }
		end,
		Wait = function() end,
	}
end

local EVENTS = {
	Touched = true, TouchEnded = true, Triggered = true, PlayerAdded = true, PlayerRemoving = true,
	CharacterAdded = true, CharacterRemoving = true, OnServerEvent = true, OnClientEvent = true,
	Changed = true, ChildAdded = true, ChildRemoved = true, DescendantAdded = true,
	DescendantRemoving = true, Heartbeat = true, Stepped = true, RenderStepped = true,
	AncestryChanged = true, Died = true, MouseButton1Click = true, Activated = true,
	PromptTriggered = true, Destroying = true,
}

-------------------------------------------------------------------------------
-- Instances
-------------------------------------------------------------------------------
local PARENT_CLASS = {
	Part = "BasePart", WedgePart = "BasePart", CornerWedgePart = "BasePart", SpawnLocation = "Part",
	MeshPart = "BasePart", TrussPart = "BasePart", BasePart = "PVInstance",
	Model = "PVInstance", Workspace = "Model", PVInstance = "Instance",
	Folder = "Instance", Script = "BaseScript", LocalScript = "BaseScript", ModuleScript = "LuaSourceContainer",
	BaseScript = "LuaSourceContainer", LuaSourceContainer = "Instance",
	Frame = "GuiObject", TextLabel = "GuiObject", TextButton = "GuiObject", ImageLabel = "GuiObject",
	ImageButton = "GuiObject", GuiObject = "GuiBase2d", GuiBase2d = "Instance",
	SurfaceGui = "LayerCollector", BillboardGui = "LayerCollector", ScreenGui = "LayerCollector",
	LayerCollector = "GuiBase2d", PointLight = "Light", SpotLight = "Light", SurfaceLight = "Light",
	Light = "Instance",
}

local function isA(className, wanted)
	local c = className
	while c do
		if c == wanted then
			return true
		end
		c = PARENT_CLASS[c]
	end
	return wanted == "Instance"
end

local function defaultsFor(className)
	local d = {}
	if isA(className, "BasePart") then
		d.Size = M.Vector3.new(4, 1, 2)
		d.CFrame = M.CFrame.new()
		d.Color = M.Color3.fromRGB(163, 162, 165)
		d.Material = M.Enum.Material.Plastic
		d.Transparency = 0
		d.Reflectance = 0
		d.Anchored = false
		d.CanCollide = true
		d.CanQuery = true
		d.CanTouch = true
		d.CastShadow = true
		d.Locked = false
		d.Massless = false
		d.Shape = M.Enum.PartType.Block
		d.PivotOffset = M.CFrame.new()
		d.CollisionGroup = "Default"
	end
	if className == "Model" then
		d.PrimaryPart = nil
	end
	return d
end

local Instance = {}
local InstanceMethods = {}
M.allInstances = {}

-- Group stack: the driver wraps builder functions (Props.tree, Props.moneyMaker...) so every
-- part knows which builder call made it, and the base CFrame that builder got.
M.groupStack = {}
M.groupSeq = 0
function M.pushGroup(label, base)
	M.groupSeq += 1
	table.insert(M.groupStack, { label = label, seq = M.groupSeq, base = base })
end
function M.popGroup()
	table.remove(M.groupStack)
end
local function snapshotGroups()
	local out = {}
	for i, g in M.groupStack do
		out[i] = g
	end
	return out
end

-- The call chain that created something: { "Props.luau:353", "Plaza.luau:47", ... }
local function callChain()
	local chain = {}
	for level = 3, 30 do
		local source, line, name = debug.info(level, "sln")
		if source == nil then
			break
		end
		if line and line > 0 and not string.find(source, "roblox_mock", 1, true) then
			local short = string.match(source, "([^/\\]+)$") or source
			table.insert(chain, short .. ":" .. line .. (if name and name ~= "" then "(" .. name .. ")" else ""))
		end
	end
	return chain
end

local instanceMt = {}
instanceMt.__index = function(self, key)
	local props = rawget(self, "_props")
	local value = props[key]
	if value ~= nil then
		return value
	end
	if key == "Parent" then
		return rawget(self, "_parent")
	elseif key == "ClassName" then
		return rawget(self, "_class")
	elseif key == "Position" and props.CFrame then
		return props.CFrame.Position
	elseif key == "Orientation" and props.CFrame then
		local x, y, z = props.CFrame:ToEulerAnglesXYZ()
		return M.Vector3.new(math.deg(x), math.deg(y), math.deg(z))
	elseif key == "WorldPivot" and rawget(self, "_class") == "Model" then
		return InstanceMethods.GetPivot(self)
	end
	local method = InstanceMethods[key]
	if method then
		return method
	end
	if EVENTS[key] then
		local signals = rawget(self, "_signals")
		signals[key] = signals[key] or newSignal()
		return signals[key]
	end
	-- a child with this name (Roblox lets you write folder.ChildName)
	for _, child in rawget(self, "_children") do
		if rawget(child, "_props").Name == key then
			return child
		end
	end
	if rawget(self, "_service") then
		-- unknown service methods do nothing (PhysicsService:RegisterCollisionGroup...)
		return function()
			return nil
		end
	end
	return nil
end

local function setParent(self, parent)
	local old = rawget(self, "_parent")
	if old == parent then
		return
	end
	if old then
		local list = rawget(old, "_children")
		for i, child in list do
			if child == self then
				table.remove(list, i)
				break
			end
		end
	end
	rawset(self, "_parent", parent)
	if parent then
		table.insert(rawget(parent, "_children"), self)
		-- Roblox: a Model without PrimaryPart and without a set WorldPivot gets its pivot at the
		-- bounding box center when needed; we compute that lazily in GetPivot.
	end
end

instanceMt.__newindex = function(self, key, value)
	if key == "Parent" then
		setParent(self, value)
		return
	end
	local props = rawget(self, "_props")
	if key == "Position" then
		local old = props.CFrame or M.CFrame.new()
		props.CFrame = M.CFrame.new(value.X, value.Y, value.Z, old.m[1], old.m[2], old.m[3], old.m[4], old.m[5], old.m[6], old.m[7], old.m[8], old.m[9])
		return
	end
	if key == "WorldPivot" then
		rawset(self, "_worldPivot", value)
		return
	end
	props[key] = value
end
instanceMt.__tostring = function(self)
	return rawget(self, "_props").Name
end

function Instance.new(className, parent)
	local self = setmetatable({
		_class = className,
		_props = defaultsFor(className),
		_children = {},
		_attributes = {},
		_tags = {},
		_signals = {},
		_parent = nil,
		__type = "Instance",
	}, instanceMt)
	rawget(self, "_props").Name = className
	if isA(className, "BasePart") or className == "Model" or className == "Folder" then
		rawset(self, "_chain", callChain())
		rawset(self, "_groups", snapshotGroups())
	end
	table.insert(M.allInstances, self)
	if parent then
		self.Parent = parent
	end
	return self
end
M.Instance = Instance

function InstanceMethods.IsA(self, className)
	return isA(rawget(self, "_class"), className)
end
function InstanceMethods.GetChildren(self)
	return table.clone(rawget(self, "_children"))
end
function InstanceMethods.GetDescendants(self)
	local out = {}
	local function walk(node)
		for _, child in rawget(node, "_children") do
			table.insert(out, child)
			walk(child)
		end
	end
	walk(self)
	return out
end
function InstanceMethods.FindFirstChild(self, name, recursive)
	for _, child in rawget(self, "_children") do
		if rawget(child, "_props").Name == name then
			return child
		end
	end
	if recursive then
		for _, child in rawget(self, "_children") do
			local found = InstanceMethods.FindFirstChild(child, name, true)
			if found then
				return found
			end
		end
	end
	return nil
end
function InstanceMethods.WaitForChild(self, name)
	local found = InstanceMethods.FindFirstChild(self, name)
	if found == nil then
		error("WaitForChild would wait forever: " .. tostring(name))
	end
	return found
end
function InstanceMethods.FindFirstChildOfClass(self, className)
	for _, child in rawget(self, "_children") do
		if rawget(child, "_class") == className then
			return child
		end
	end
	return nil
end
function InstanceMethods.FindFirstChildWhichIsA(self, className)
	for _, child in rawget(self, "_children") do
		if isA(rawget(child, "_class"), className) then
			return child
		end
	end
	return nil
end
function InstanceMethods.FindFirstAncestorOfClass(self, className)
	local node = rawget(self, "_parent")
	while node do
		if rawget(node, "_class") == className then
			return node
		end
		node = rawget(node, "_parent")
	end
	return nil
end
function InstanceMethods.IsDescendantOf(self, other)
	local node = rawget(self, "_parent")
	while node do
		if node == other then
			return true
		end
		node = rawget(node, "_parent")
	end
	return false
end
function InstanceMethods.ClearAllChildren(self)
	for _, child in table.clone(rawget(self, "_children")) do
		InstanceMethods.Destroy(child)
	end
end
function InstanceMethods.Destroy(self)
	setParent(self, nil)
	rawset(self, "_destroyed", true)
	for _, child in table.clone(rawget(self, "_children")) do
		InstanceMethods.Destroy(child)
	end
end
function InstanceMethods.Clone(self)
	local copy = Instance.new(rawget(self, "_class"))
	for k, v in rawget(self, "_props") do
		rawget(copy, "_props")[k] = v
	end
	for k, v in rawget(self, "_attributes") do
		rawget(copy, "_attributes")[k] = v
	end
	for k, v in rawget(self, "_tags") do
		rawget(copy, "_tags")[k] = v
	end
	rawset(copy, "_chain", rawget(self, "_chain"))
	rawset(copy, "_groups", rawget(self, "_groups"))
	for _, child in rawget(self, "_children") do
		InstanceMethods.Clone(child).Parent = copy
	end
	return copy
end
function InstanceMethods.SetAttribute(self, name, value)
	rawget(self, "_attributes")[name] = value
end
function InstanceMethods.GetAttribute(self, name)
	return rawget(self, "_attributes")[name]
end
function InstanceMethods.GetAttributes(self)
	return table.clone(rawget(self, "_attributes"))
end
function InstanceMethods.GetFullName(self)
	local names = {}
	local node = self
	while node and rawget(node, "_class") ~= "DataModel" do
		table.insert(names, 1, rawget(node, "_props").Name)
		node = rawget(node, "_parent")
	end
	return table.concat(names, ".")
end
function InstanceMethods.GetService(self, name)
	return M.getService(name)
end
function InstanceMethods.SetNetworkOwner() end
function InstanceMethods.BreakJoints() end

-- every BasePart below (and including) this instance
local function partsOf(self)
	local parts = {}
	if isA(rawget(self, "_class"), "BasePart") then
		table.insert(parts, self)
	end
	for _, item in InstanceMethods.GetDescendants(self) do
		if isA(rawget(item, "_class"), "BasePart") then
			table.insert(parts, item)
		end
	end
	return parts
end

-- the 8 corners of a part, in world space
local function corners(part)
	local props = rawget(part, "_props")
	local s, c = props.Size, props.CFrame
	local out = {}
	for _, x in { -1, 1 } do
		for _, y in { -1, 1 } do
			for _, z in { -1, 1 } do
				table.insert(out, c * M.Vector3.new(x * s.X / 2, y * s.Y / 2, z * s.Z / 2))
			end
		end
	end
	return out
end
M.corners = corners

-- bounding box of parts, measured in the orientation of `frame` (a CFrame)
local function boxIn(parts, frame)
	local inv = frame:Inverse()
	local lo = M.Vector3.new(math.huge, math.huge, math.huge)
	local hi = M.Vector3.new(-math.huge, -math.huge, -math.huge)
	for _, part in parts do
		for _, p in corners(part) do
			local q = inv * p
			lo = lo:Min(q)
			hi = hi:Max(q)
		end
	end
	return lo, hi
end

function InstanceMethods.GetPivot(self)
	local props = rawget(self, "_props")
	if isA(rawget(self, "_class"), "BasePart") then
		return props.CFrame * props.PivotOffset
	end
	local primary = props.PrimaryPart
	if primary then
		local pp = rawget(primary, "_props")
		return pp.CFrame * pp.PivotOffset
	end
	local pivot = rawget(self, "_worldPivot")
	if pivot then
		return pivot
	end
	-- Roblox default: the center of the bounding box (world aligned)
	local parts = partsOf(self)
	if #parts == 0 then
		return M.CFrame.new()
	end
	local lo, hi = boxIn(parts, M.CFrame.new())
	local center = (lo + hi) / 2
	return M.CFrame.new(center.X, center.Y, center.Z)
end

function InstanceMethods.PivotTo(self, target)
	local current = InstanceMethods.GetPivot(self)
	local delta = target * current:Inverse()
	for _, part in partsOf(self) do
		local props = rawget(part, "_props")
		props.CFrame = delta * props.CFrame
	end
	if rawget(self, "_class") == "Model" and rawget(self, "_props").PrimaryPart == nil then
		rawset(self, "_worldPivot", target)
	end
end

function InstanceMethods.GetBoundingBox(self)
	local parts = partsOf(self)
	local pivot = InstanceMethods.GetPivot(self)
	local frame = pivot.Rotation
	local lo, hi = boxIn(parts, frame)
	local center = frame * ((lo + hi) / 2)
	return M.CFrame.new(center.X, center.Y, center.Z) * frame, hi - lo
end
function InstanceMethods.GetExtentsSize(self)
	local _, size = InstanceMethods.GetBoundingBox(self)
	return size
end

function InstanceMethods.GetScale(self)
	return rawget(self, "_scale") or 1
end
function InstanceMethods.ScaleTo(self, newScale)
	local old = rawget(self, "_scale") or 1
	local factor = newScale / old
	local pivot = InstanceMethods.GetPivot(self)
	for _, part in partsOf(self) do
		local props = rawget(part, "_props")
		local localCf = pivot:Inverse() * props.CFrame
		local p = localCf.Position * factor
		props.CFrame = pivot * (M.CFrame.new(p.X, p.Y, p.Z) * localCf.Rotation)
		props.Size = props.Size * factor
		props.PivotOffset = M.CFrame.new(props.PivotOffset.Position.X * factor, props.PivotOffset.Position.Y * factor, props.PivotOffset.Position.Z * factor) * props.PivotOffset.Rotation
	end
	rawset(self, "_scale", newScale)
end

-------------------------------------------------------------------------------
-- The DataModel and services
-------------------------------------------------------------------------------
M.game = Instance.new("DataModel")
rawget(M.game, "_props").Name = "Game"
local services = {}
function M.getService(name)
	local service = services[name]
	if service == nil then
		service = Instance.new(name)
		rawset(service, "_service", true)
		service.Name = name
		service.Parent = M.game
		services[name] = service
	end
	return service
end
M.workspace = M.getService("Workspace")
rawset(M.workspace, "_class", "Workspace")
local terrain = Instance.new("Terrain")
terrain.Name = "Terrain"
terrain.Parent = M.workspace

-- Raycast: only hits the Baseplate (that is what Props.groundY asks for)
function InstanceMethods.Raycast(self, origin, direction, params)
	local baseplate = InstanceMethods.FindFirstChild(M.workspace, "Baseplate")
	if baseplate then
		local props = rawget(baseplate, "_props")
		local top = props.CFrame.Y + props.Size.Y / 2
		return { Position = M.Vector3.new(origin.X, top, origin.Z), Instance = baseplate, Normal = M.Vector3.new(0, 1, 0) }
	end
	return nil
end
function InstanceMethods.GetServerTimeNow()
	return 0
end
function InstanceMethods.GetPlayers()
	return {}
end
function InstanceMethods.GetPlayerFromCharacter()
	return nil
end
function InstanceMethods.GetDataStore()
	return {
		GetAsync = function()
			return nil
		end,
		SetAsync = function() end,
		ListKeysAsync = function()
			error("no datastore")
		end,
	}
end

-- CollectionService
function InstanceMethods.AddTag(self, item, tag)
	if tag == nil then -- item:AddTag(tag)
		rawget(self, "_tags")[item] = true
		return
	end
	rawget(item, "_tags")[tag] = true
end
function InstanceMethods.HasTag(self, item, tag)
	if tag == nil then
		return rawget(self, "_tags")[item] == true
	end
	return rawget(item, "_tags")[tag] == true
end
function InstanceMethods.GetTagged(self, tag)
	local out = {}
	for _, item in M.allInstances do
		if rawget(item, "_tags")[tag] and not rawget(item, "_destroyed") then
			table.insert(out, item)
		end
	end
	return out
end
function InstanceMethods.GetInstanceAddedSignal()
	return newSignal()
end
function InstanceMethods.GetInstanceRemovedSignal()
	return newSignal()
end

-------------------------------------------------------------------------------
-- Other globals
-------------------------------------------------------------------------------
M.RaycastParams = {
	new = function()
		return {}
	end,
}
M.OverlapParams = M.RaycastParams
M.task = {
	spawn = function() end, -- game loops are not run: we only want the world
	defer = function() end,
	delay = function() end,
	wait = function()
		return 0
	end,
}
M.typeof = function(value)
	if type(value) == "table" then
		local t = rawget(value, "__type")
		if t then
			return t
		end
	end
	return type(value)
end
M.NumberRange = {
	new = function(a, b)
		return { Min = a, Max = b or a }
	end,
}
M.NumberSequence = {
	new = function(a)
		return { a }
	end,
}
M.ColorSequence = M.NumberSequence
M.TweenInfo = {
	new = function()
		return {}
	end,
}
M.BrickColor = {
	new = function(name)
		return { Name = name }
	end,
}
M.PhysicalProperties = M.TweenInfo

-- Random: deterministic (same world every run)
M.Random = {
	new = function(seed)
		local state = (seed or 12345) % 2147483647
		if state <= 0 then
			state = state + 2147483646
		end
		local rng = {}
		local function nextRaw()
			state = (state * 16807) % 2147483647
			return state / 2147483647
		end
		function rng.NextNumber(_, a, b)
			a, b = a or 0, b or 1
			return a + (b - a) * nextRaw()
		end
		function rng.NextInteger(_, a, b)
			return a + math.floor(nextRaw() * (b - a + 1))
		end
		function rng.Shuffle(_, list)
			for i = #list, 2, -1 do
				local j = 1 + math.floor(nextRaw() * i)
				list[i], list[j] = list[j], list[i]
			end
		end
		return rng
	end,
}

return M

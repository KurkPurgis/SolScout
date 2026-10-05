# Import plan - how to swap the new look into the game (NOT executed)

Written 2026-10-05 09:33. Nothing here has been done: nothing was uploaded, published or changed in `src/`.

## The idea in one paragraph

The world is built by Luau code when the server starts (and while a game runs), so the swap also happens in code: right after the game builds something, a small module (`WorldSkin`) makes the old parts invisible and puts a copy of the new model on exactly the same spot. The old parts keep **all** their jobs - collision, prompts, SurfaceGui text, lights, the invisible barriers and buy buttons - so gameplay cannot change. The new MeshParts are visual only. One switch (`WorldSkin.ENABLED = false`) brings the old look back.

## Step 1 - safety first

1. Make a git branch in the game repo (e.g. `new-look`). Do the steps below in a copy of the place, not the live game.
2. You will add 2 files to `src/`, a `require` line in 6 files and 15 one-line calls (Step 6; one of them replaces a line); everything else happens in Studio.

## Step 2 - upload the palette (2 images)

Upload `world_overhaul/palette/palette_color.png` and `palette_roughness.png` (Asset Manager > Import, or Bulk Import). Note both asset ids. These two images color **every** model in the world.

## Step 3 - import the meshes

Import every file in `world_overhaul/export/<category>/*.fbx` - 128 files: all of them except `export/props/Dream_Chains.fbx`, the one-piece chains that your link-by-link decision replaced - with the 3D Importer (File > Import 3D). Settings ([Roblox: Blender to Studio settings](https://github.com/Roblox/creator-docs/blob/main/content/en-us/art/blender.md)):

| section | setting | value | why |
|---|---|---|---|
| File General | Import Only as a Model | on | body + glow + glass meshes stay together in one Model |
| File General | Upload to Roblox | on | gives the MeshIds |
| File General | Insert Using Scene Position | **on** | the FBX origin IS the original object's frame - it must not move |
| File Transform | World Forward / World Up | Front / Top | (see the check below) |
| File Geometry | Scale Unit | **Stud** | 1 Blender unit = 1 stud |

**Check on the first model before importing the rest:** import `export/buildings/Workplace_Building_PIZZERIA.fbx` at the origin. Its box must span x -24.8..24.8, y -1.0..18.5, z 2.5..24.8 (from `data/model_status.json` -> `bbox_new`): the open front (awning edge at z 2.5) and the big sign (near z 6.5) on the low-z side. If the box spans z -24.8..-2.5 instead (and x -24.8..24.8), the file came in turned 180 degrees about the origin: set World Forward to **Back** for every import. The FBX files were exported with Blender's default axes (forward -Z, up Y), so the coordinates in the files already are Roblox coordinates.

## Step 4 - the WorldKit folder

Put every imported model in `ServerStorage/WorldKit`, **renamed to its template name** (the table at the end lists FBX file -> template name). Then run this once in the command bar (fill in the two asset ids):

```lua
local COLOR, ROUGH = "rbxassetid://<palette_color id>", "rbxassetid://<palette_roughness id>"
local GLOW = {
	CREAM = Color3.fromRGB(250, 240, 220),
	GOLD_LIGHT = Color3.fromRGB(255, 214, 92),
	GOLD = Color3.fromRGB(255, 182, 34),
	ORANGE = Color3.fromRGB(244, 136, 20),
	RED = Color3.fromRGB(236, 66, 78),
	BRICK = Color3.fromRGB(186, 40, 48),
	PINK = Color3.fromRGB(255, 120, 170),
	SKIN = Color3.fromRGB(245, 200, 160),
	WHITE = Color3.fromRGB(234, 238, 248),
	SKY = Color3.fromRGB(110, 190, 250),
	BLUE = Color3.fromRGB(44, 116, 222),
	NAVY = Color3.fromRGB(34, 52, 120),
	TEAL = Color3.fromRGB(40, 186, 176),
	PURPLE = Color3.fromRGB(146, 84, 226),
	WINDOW = Color3.fromRGB(160, 214, 250),
	STEEL = Color3.fromRGB(128, 130, 154),
	LEAF = Color3.fromRGB(52, 170, 74),
	GREEN = Color3.fromRGB(88, 208, 96),
	GRASS = Color3.fromRGB(104, 186, 84),
	GREEN_DARK = Color3.fromRGB(38, 132, 64),
	SAND = Color3.fromRGB(236, 200, 128),
	TAN = Color3.fromRGB(214, 150, 80),
	WOOD = Color3.fromRGB(170, 98, 44),
	WOOD_DARK = Color3.fromRGB(112, 60, 26),
	STONE = Color3.fromRGB(214, 203, 180),
	STONE_DARK = Color3.fromRGB(166, 154, 136),
	SLATE = Color3.fromRGB(104, 108, 132),
	CHARCOAL = Color3.fromRGB(58, 52, 76),
	INK = Color3.fromRGB(40, 26, 58),
	WATER = Color3.fromRGB(60, 160, 240),
	GLOW_WARM = Color3.fromRGB(255, 236, 160),
	GLOW_COOL = Color3.fromRGB(130, 230, 255),
}
local template = Instance.new("SurfaceAppearance")
template.ColorMap, template.RoughnessMap = COLOR, ROUGH
for _, kit in game.ServerStorage.WorldKit:GetChildren() do
	kit.WorldPivot = CFrame.new() -- the FBX origin = the original object's frame
	local lo, hi = Vector3.one * math.huge, -Vector3.one * math.huge
	for _, p in kit:GetDescendants() do
		if p:IsA("MeshPart") then
			p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
			p.CollisionFidelity = Enum.CollisionFidelity.Box
			p.Massless = true
			p.CastShadow = p.Size.X * p.Size.Y * p.Size.Z > 6 -- tiny details cast no shadow
			local glow = p.Name:match("_Glow_([%w_]+)$")
			if glow then
				local color, t = glow:match("^(.-)_T(%d+)$")
				p.Material = Enum.Material.Neon
				local c = GLOW[color or glow]
				if c then p.Color = c else warn("no glow color for " .. p:GetFullName()) end
				p.Transparency = if t then tonumber(t) / 100 else 0.35 -- the game's NEON_SOFTNESS
				p.CastShadow = false
			elseif p.Name:match("_Glass$") then
				p.Material, p.Color, p.Transparency = Enum.Material.Glass, GLOW.WINDOW, 0.3
			else
				p.Material, p.Reflectance = Enum.Material.SmoothPlastic, 0
				for _, old in p:GetChildren() do if old:IsA("SurfaceAppearance") then old:Destroy() end end
				template:Clone().Parent = p
			end
			local half = p.Size / 2
			lo, hi = lo:Min(p.Position - half), hi:Max(p.Position + half)
		end
	end
	kit:SetAttribute("BoxMin", lo) -- used to stretch debts to their size
	kit:SetAttribute("BoxMax", hi)
end
```

(The glow color table lists the whole palette; a glow mesh is named `<model>_Glow_<COLOR>` or `<model>_Glow_<COLOR>_T<transparency %>`; `_T100` = hidden until a script shows it.)

## Step 5 - add the two modules

Copy `world_overhaul/export/roblox/WorldSkin.luau` and `WorldSkinPlacements.luau` to `src/server/World/`. `WorldSkinPlacements` is generated from the world data: every kit model's frame relative to the base CFrame of the code that builds it (one built copy of each context is the pattern). Checked with `tools/verify_placements.py`, independently: it takes each place's base CFrame from the world dump and checks, in world space, that the list puts exactly the objects that are there, turned the same way, with the kit's box on the object's box. All 38 places the snapshot built pass (0 mismatches): 10 workplaces, 10 furniture sets, 4 plazas, 4 auction rooms, 4 podium rooms, 3 showcases, 2 dream pedestals, 1 lobby. The chains are not in this check: `WorldSkin.chains` follows the chain bars the game makes (tested in `tools/luau/test_worldskin_chains.luau`).

`WorldSkin` never hides anything without its replacement: if a kit model is missing from `WorldKit`, it warns in the output and leaves that object (or that whole context) in the old look. Without a `WorldKit` folder it switches itself off.

## Step 6 - the calls (one line each)

`local WorldSkin = require(script.Parent.WorldSkin)` at the top of `Plaza.luau`, `AuctionRoom.luau`, `PodiumRoom.luau`, `Plots.luau` and `Props.luau` (all in `World/`), and `local WorldSkin = require(script.Parent.World.WorldSkin)` in `Lobby.luau` (adjust to your Rojo tree), then:

| file / function | where | line |
|---|---|---|
| `Lobby.luau` (start-up) | right before `buildHall()` is called (line 476) | `WorldSkin.object(workspace:FindFirstChild("Baseplate"), "Baseplate", CFrame.new())`: the grass baseplate of the place (Rojo `default.project.json`); the old Part stays, invisible, so `Props.groundY` still raycasts against it |
| `Lobby.luau` `buildHall()` | at the end | `WorldSkin.context("Lobby", hallBase, folder)` |
| `World/Plaza.luau` `Plaza.new` | before `return self` | `WorldSkin.context("Plaza", base, folder)` |
| `World/AuctionRoom.luau` `AuctionRoom.new` | before `return self` | `WorldSkin.context("AuctionRoom", BASE, folder)` |
| `World/PodiumRoom.luau` `PodiumRoom.new` | before `return self` | `WorldSkin.context("PodiumRoom", base, folder)` |
| `World/Plots.luau` `Plots:buildWorkplace(theme)` | at the very end of the function: after the `if theme.luxury ... else ... end` block (sandbox, Fast Track gate / debt pad), just before its `end` | `WorldSkin.context({ "Workplace:" .. theme.title, "Furnish:" .. theme.title }, self.base, self.workplaceFolder)` (one call for both: they share the folder; the keys use the sign title, e.g. `Workplace:BUS DEPOT`) |
| `World/Plots.luau` `Plots:syncCollection` | right after the two `Props.box` lines of the showcase table (before the loop) | `WorldSkin.context("Collection", self.base, self.collectionFolder)` |
| `World/Plots.luau` `Plots:syncDream` | in the `else` branch (locked or won dream), right after the two `Props.box` lines of the marble pedestal (before `Props.dream`) | `WorldSkin.context("DreamArea", self.base, self.dreamFolder)` |
| `World/Plots.luau` `addChains(folder, model)` | at the end | `WorldSkin.chains(folder)`: the chains **link by link** (your decision): `Dream_ChainSegment` pieces tiled along every chain bar + `Dream_Padlock` |
| `World/Props.luau` `Props.kid` | after `model.PrimaryPart = body` | `WorldSkin.object(model, WorldSkin.kidTemplate(shirtColor), base)` (4 shirts: `Kid`, `Kid_v2`, `Kid_v3`, `Kid_v4`) |
| `World/Props.luau` `Props.moneyMaker` | before `model.Parent = parent` | `WorldSkin.object(model, WorldSkin.makerTemplate(name, value), base)` (PokeBlox cards: the model with the case color of `Props.cardCase(value)`) |
| `World/Props.luau` `Props.debtModel` | before `model.Parent = parent` | `WorldSkin.stretched(model, WorldSkin.debtTemplate(debtName, amount), base)` (School Loan: the model with the right number of books) |
| `World/Props.luau` `Props.dream` | right after `local model = builder.build()` | `WorldSkin.object(model, "Dream_" .. model.Name, model:GetPivot())` (`model.Name` is `BeachVilla`, `PrivateJet`...; not `dreamName`, which has spaces) |
| `World/AuctionRoom.luau` `AuctionRoom:highlight` | inside the loop, after the two lines | `WorldSkin.setGlow(WorldSkin.nearest(self.folder, "AuctionRoom_BidderDesk", podium.Position), isTop)`: the old desk (now hidden) turns gold Neon; the new desk shows its gold glow shell (`_Glow_GOLD_T100`) |
| `World/PodiumRoom.luau` `PodiumRoom:fillBoard` | **replace** line 158 `self.board.Transparency = if #standings > 3 then 0 else 1` | `WorldSkin.show(self.board, self.folder, "PodiumRoom_Board", #standings > 3)` (shows/hides the new board and keeps the old one hidden; without WorldSkin it does exactly what line 158 did) |

Trees need no call of their own: `Props.tree` puts its parts straight into the plaza folder, so the `Plaza` context hides them and places the 8 `Tree` models around the plaza with the rest of it.

Why these places: the ghost FOR SALE copies (`Props.makeGhost`), the 0.4x collection minis (`model:ScaleTo(0.4)`), the floating dreams (`ScaleTo` + `PivotTo`), the kids' hop and the dream spin (`PivotTo`) all run **after** these builders return, so they automatically include the new MeshParts (they are BaseParts inside the same Model).

## Step 7 - test in Studio (Play Solo, then 2-4 players)

- [ ] Lobby: walk around, the room booths still open, the spawn still works, the trophy and palms look right; the grass baseplate has the new look and you still stand on it.
- [ ] Start a game: your workplace appears with the new building, furniture, fence, lamps and yard; you still walk on the same floor heights, the Pay/Buy prompts still appear on the debts and the FOR SALE item.
- [ ] Buy a Money Maker: it stands on the lot, the next one stacks on top at the same height as before (`GetBoundingBox`), its label floats at the same spot.
- [ ] The FOR SALE copy looks see-through (ForceField) - also the new meshes.
- [ ] Add investments: the minis in the showcase are 0.4x and sit on the table; a PokeBlox card whose value crosses a case boundary (1000 / 10000 / 30000) changes its case color.
- [ ] Have 4 kids: all 4 have the new look (red, blue, yellow, green shirts) and still hop.
- [ ] Your dream floats and spins; it fades in/out as before (the old parts must stay hidden while it fades).
- [ ] Escape: the workplace turns into the Fast Track version (new look too), pedestal + chains.
- [ ] Auction: only the top bidder's desk glows gold. Podium: the board shows only with more than 3 players.
- [ ] Output: no `WorldSkin:` warnings (a warning names a kit model that is missing from `WorldKit`).
- [ ] Text: every sign still shows its text (prices, names, job names) in front of the new boards.
- [ ] Performance: open the MicroProfiler / Stats on a phone-sized client: triangles and draw calls.

## Switch back

Set `WorldSkin.ENABLED = false` (or remove the calls): nothing is hidden and no kit model is added, so the game looks exactly like today. Nothing else was changed.

## Collision and materials per object type

| type | new MeshParts | old parts |
|---|---|---|
| everything | Anchored, CanCollide/CanQuery/CanTouch **off**, CollisionFidelity Box, Massless | stay, invisible (Transparency 1), collide/prompt/trigger exactly as today |
| body mesh | SmoothPlastic + SurfaceAppearance (palette color + roughness) | |
| `_Glow_<COLOR>` | Neon, palette color, Transparency 0.35 (or `_T..`), no shadow | |
| `_Glass` | Glass, WINDOW color, Transparency 0.3 | |
| tiny details (< 6 cubic studs) | CastShadow off | |

## Every model: file, name and where it goes

*name in the game*: the Model name for objects the game makes as a named Model (Money Makers, debts, dreams, `Kid`; the kit goes inside that Model, so the name stays); otherwise the inventory name of a group of plain `Part`s (`INVENTORY.md`), which keep their own names. *script-referenced*: some game script finds the object type by name, measures it or changes it (`data/script_refs.json`).

| template (= WorldKit name) | name in the game | FBX | meshes | how it is placed | built by (game code) | script-referenced |
|---|---|---|---|---|---|---|
| Workplace_Building_PIZZERIA | Workplace_Building | `export/buildings/Workplace_Building_PIZZERIA.fbx` | `Workplace_Building_PIZZERIA`, `Workplace_Building_PIZZERIA_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:PIZZERIA | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_BUSDEPOT | Workplace_Building | `export/buildings/Workplace_Building_BUSDEPOT.fbx` | `Workplace_Building_BUSDEPOT`, `Workplace_Building_BUSDEPOT_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:BUS DEPOT | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_HOSPITAL | Workplace_Building | `export/buildings/Workplace_Building_HOSPITAL.fbx` | `Workplace_Building_HOSPITAL`, `Workplace_Building_HOSPITAL_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:HOSPITAL | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_CLINIC | Workplace_Building | `export/buildings/Workplace_Building_CLINIC.fbx` | `Workplace_Building_CLINIC`, `Workplace_Building_CLINIC_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:CLINIC | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_SCHOOL | Workplace_Building | `export/buildings/Workplace_Building_SCHOOL.fbx` | `Workplace_Building_SCHOOL`, `Workplace_Building_SCHOOL_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:SCHOOL | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_POLICE | Workplace_Building | `export/buildings/Workplace_Building_POLICE.fbx` | `Workplace_Building_POLICE`, `Workplace_Building_POLICE_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:POLICE | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_OFFICE | Workplace_Building | `export/buildings/Workplace_Building_OFFICE.fbx` | `Workplace_Building_OFFICE`, `Workplace_Building_OFFICE_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:OFFICE | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_GARAGE | Workplace_Building | `export/buildings/Workplace_Building_GARAGE.fbx` | `Workplace_Building_GARAGE`, `Workplace_Building_GARAGE_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:GARAGE | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Building_FASTTRACK | Workplace_Building | `export/buildings/Workplace_Building_FASTTRACK.fbx` | `Workplace_Building_FASTTRACK`, `Workplace_Building_FASTTRACK_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:FAST TRACK | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 | yes |
| Workplace_Yard_v2 | Workplace_Yard | `export/ground/Workplace_Yard_v2.fbx` | `Workplace_Yard_v2` | `WorldSkin.context` in Workplace:* (8) | Plots.luau:130,132 | yes |
| Workplace_Yard | Workplace_Yard | `export/ground/Workplace_Yard.fbx` | `Workplace_Yard` | `WorldSkin.context` in Workplace:FAST TRACK | Plots.luau:130,132 | yes |
| Workplace_MakerLot | Workplace_MakerLot | `export/ground/Workplace_MakerLot.fbx` | `Workplace_MakerLot` | `WorldSkin.context` in Workplace:* (9) | Plots.luau:176 | yes |
| Workplace_Fence | Workplace_Fence | `export/decoration/Workplace_Fence.fbx` | `Workplace_Fence` | `WorldSkin.context` in Workplace:* (9) | Plots.luau:183,186 | yes |
| Workplace_LampPost | Workplace_LampPost | `export/decoration/Workplace_LampPost.fbx` | `Workplace_LampPost`, `Workplace_LampPost_Glow_GLOW_WARM` | `WorldSkin.context` in Workplace:* (9) | Plots.luau:189,190 | yes |
| Workplace_FlowerBox | Workplace_FlowerBox | `export/decoration/Workplace_FlowerBox.fbx` | `Workplace_FlowerBox` | `WorldSkin.context` in Workplace:* (9) | Plots.luau:200,202 | yes |
| Workplace_Sandbox | Workplace_Sandbox | `export/props/Workplace_Sandbox.fbx` | `Workplace_Sandbox` | `WorldSkin.context` in Workplace:* (9) | Plots.luau:207,209 | yes |
| Workplace_DebtPad | Workplace_DebtPad | `export/ground/Workplace_DebtPad.fbx` | `Workplace_DebtPad` | `WorldSkin.context` in Workplace:* (8) | Plots.luau:218 | yes |
| Plaza_Fountain | Plaza_Fountain | `export/decoration/Plaza_Fountain.fbx` | `Plaza_Fountain`, `Plaza_Fountain_Glass`, `Plaza_Fountain_Glow_GLOW_COOL` | `WorldSkin.context` in Plaza | Plaza.luau:69,70,71,72 |  |
| Tree | Tree | `export/nature/Tree.fbx` | `Tree` | `WorldSkin.context` in Plaza | Plaza.luau:65 |  |
| Plaza_Disc | Plaza_Disc | `export/ground/Plaza_Disc.fbx` | `Plaza_Disc` | `WorldSkin.context` in Plaza | Plaza.luau:52 |  |
| Plaza_Path | Plaza_Path | `export/ground/Plaza_Path.fbx` | `Plaza_Path` | `WorldSkin.context` in Plaza | Plaza.luau:58 |  |
| City_Ground | City_Ground | `export/ground/City_Ground.fbx` | `City_Ground` | `WorldSkin.context` in Plaza | Plaza.luau:35 |  |
| City_Wall | City_Wall | `export/decoration/City_Wall.fbx` | `City_Wall` | `WorldSkin.context` in Plaza | Plaza.luau:43,44 |  |
| Dream_Supercar | Supercar | `export/vehicles/Supercar.fbx` | `Supercar`, `Supercar_Glow_GLOW_WARM` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_Yacht | Yacht | `export/vehicles/Yacht.fbx` | `Yacht` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_BeachVilla | BeachVilla | `export/buildings/BeachVilla.fbx` | `BeachVilla`, `BeachVilla_Glass`, `BeachVilla_Glow_GLOW_WARM` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_PrivateJet | PrivateJet | `export/vehicles/PrivateJet.fbx` | `PrivateJet` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_PrivateIsland | PrivateIsland | `export/nature/PrivateIsland.fbx` | `PrivateIsland` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Maker_LemonadeStand | Lemonade Stand | `export/props/Lemonade Stand.fbx` | `Maker_LemonadeStand` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_VendingMachine | Vending Machine | `export/props/Vending Machine.fbx` | `Maker_VendingMachine`, `Maker_VendingMachine_Glow_GLOW_COOL` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_Apartment | Apartment | `export/buildings/Apartment.fbx` | `Maker_Apartment`, `Maker_Apartment_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_CarWash | Car Wash | `export/buildings/Car Wash.fbx` | `Maker_CarWash`, `Maker_CarWash_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_FoodTruck | Food Truck | `export/vehicles/Food Truck.fbx` | `Maker_FoodTruck`, `Maker_FoodTruck_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ToyShop | Toy Shop | `export/buildings/Toy Shop.fbx` | `Maker_ToyShop` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_MiniGolf | Mini Golf | `export/props/Mini Golf.fbx` | `Maker_MiniGolf` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_HouseToRent | House to Rent | `export/buildings/House to Rent.fbx` | `Maker_HouseToRent` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_PizzaRestaurant | Pizza Restaurant | `export/buildings/Pizza Restaurant.fbx` | `Maker_PizzaRestaurant`, `Maker_PizzaRestaurant_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_CoffeeShop | Coffee Shop | `export/buildings/Coffee Shop.fbx` | `Maker_CoffeeShop`, `Maker_CoffeeShop_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_BowlingAlley | Bowling Alley | `export/buildings/Bowling Alley.fbx` | `Maker_BowlingAlley`, `Maker_BowlingAlley_Glow_GLOW_COOL` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_Hotel | Hotel | `export/buildings/Hotel.fbx` | `Maker_Hotel`, `Maker_Hotel_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GameStudio | Game Studio | `export/buildings/Game Studio.fbx` | `Maker_GameStudio`, `Maker_GameStudio_Glow_GLOW_COOL` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ShoppingMall | Shopping Mall | `export/buildings/Shopping Mall.fbx` | `Maker_ShoppingMall` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ApartmentBuilding | Apartment Building | `export/buildings/Apartment Building.fbx` | `Maker_ApartmentBuilding`, `Maker_ApartmentBuilding_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ThemePark | Theme Park | `export/props/Theme Park.fbx` | `Maker_ThemePark` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_PokeBloxCard | PokeBlox Card | `export/props/PokeBlox Card.fbx` | `Maker_PokeBloxCard`, `Maker_PokeBloxCard_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_RarePokeBloxCard | Rare PokeBlox Card | `export/props/Rare PokeBlox Card.fbx` | `Maker_RarePokeBloxCard`, `Maker_RarePokeBloxCard_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_RarePokeBloxCard_v2 | Rare PokeBlox Card | `export/props/Rare PokeBlox Card (case 2).fbx` | `Maker_RarePokeBloxCard_v2`, `Maker_RarePokeBloxCard_v2_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_RarePokeBloxCard_v3 | Rare PokeBlox Card | `export/props/Rare PokeBlox Card (case 3).fbx` | `Maker_RarePokeBloxCard_v3`, `Maker_RarePokeBloxCard_v3_Glass`, `Maker_RarePokeBloxCard_v3_Glow_PURPLE` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_RarePokeBloxCard_v4 | Rare PokeBlox Card | `export/props/Rare PokeBlox Card (case 4).fbx` | `Maker_RarePokeBloxCard_v4`, `Maker_RarePokeBloxCard_v4_Glass`, `Maker_RarePokeBloxCard_v4_Glow_GOLD` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ShinyPokeBloxCard | Shiny PokeBlox Card | `export/props/Shiny PokeBlox Card.fbx` | `Maker_ShinyPokeBloxCard`, `Maker_ShinyPokeBloxCard_Glass`, `Maker_ShinyPokeBloxCard_Glow_GLOW_COOL`, `Maker_ShinyPokeBloxCard_Glow_PURPLE` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GoldCoin | Gold Coin | `export/props/Gold Coin.fbx` | `Maker_GoldCoin` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GoldBar | Gold Bar | `export/props/Gold Bar.fbx` | `Maker_GoldBar` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GoldTreasureChest | Gold Treasure Chest | `export/props/Gold Treasure Chest.fbx` | `Maker_GoldTreasureChest` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_UnknownMaker | Unknown Maker | `export/props/Unknown Maker.fbx` | `Maker_UnknownMaker` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Kid | Kid | `export/props/Kid.fbx` | `Kid` | `WorldSkin.object` | Props.kid (Props.luau:220) | yes |
| Kid_v2 | Kid | `export/props/Kid (blue).fbx` | `Kid_v2` | `WorldSkin.object` | Props.kid (Props.luau:220) | yes |
| Kid_v3 | Kid | `export/props/Kid (yellow).fbx` | `Kid_v3` | `WorldSkin.object` | Props.kid (Props.luau:220) | yes |
| Debt_CreditCard | Credit Card | `export/props/Credit Card.fbx` | `Debt_CreditCard` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_CarLoan | Car Loan | `export/props/Car Loan.fbx` | `Debt_CarLoan` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_SchoolLoan | School Loan | `export/props/School Loan.fbx` | `Debt_SchoolLoan` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_BankLoan | Bank Loan | `export/props/Bank Loan.fbx` | `Debt_BankLoan` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_OtherDebt | Other Debt | `export/props/Debt Crate.fbx` | `Debt_OtherDebt` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Depot_Bus | Depot_Bus | `export/vehicles/Depot_Bus.fbx` | `Depot_Bus`, `Depot_Bus_Glow_GLOW_WARM` | `WorldSkin.context` in Furnish:BUS DEPOT | Themes.luau:71,73,77 |  |
| Police_Car | Police_Car | `export/vehicles/Police_Car.fbx` | `Police_Car`, `Police_Car_Glow_BLUE`, `Police_Car_Glow_GLOW_WARM`, `Police_Car_Glow_RED` | `WorldSkin.context` in Furnish:POLICE | Themes.luau:143,144,145 |  |
| Garage_CarLift | Garage_CarLift | `export/vehicles/Garage_CarLift.fbx` | `Garage_CarLift`, `Garage_CarLift_Glow_GLOW_WARM` | `WorldSkin.context` in Furnish:GARAGE | Themes.luau:175,176,177 |  |
| Computer | Computer | `export/props/Computer.fbx` | `Computer`, `Computer_Glow_GLOW_COOL` | `WorldSkin.context` in Furnish:* (3) | Themes.luau:31,36,37 |  |
| HospitalBed | HospitalBed | `export/props/HospitalBed.fbx` | `HospitalBed` | `WorldSkin.context` in Furnish:CLINIC, Furnish:HOSPITAL | Themes.luau:41,42,43 |  |
| Pizzeria_Counter | Pizzeria_Counter | `export/props/Pizzeria_Counter.fbx` | `Pizzeria_Counter` | `WorldSkin.context` in Furnish:PIZZERIA | Themes.luau:54,55,58 |  |
| Pizzeria_Oven | Pizzeria_Oven | `export/props/Pizzeria_Oven.fbx` | `Pizzeria_Oven`, `Pizzeria_Oven_Glow_ORANGE` | `WorldSkin.context` in Furnish:PIZZERIA | Themes.luau:56,57 |  |
| School_Blackboard | School_Blackboard | `export/decoration/School_Blackboard.fbx` | `School_Blackboard` | `WorldSkin.context` in Furnish:SCHOOL | Themes.luau:124 |  |
| School_TeacherDesk | School_TeacherDesk | `export/props/School_TeacherDesk.fbx` | `School_TeacherDesk` | `WorldSkin.context` in Furnish:SCHOOL | Themes.luau:31 |  |
| School_StudentDesk | School_StudentDesk | `export/props/School_StudentDesk.fbx` | `School_StudentDesk` | `WorldSkin.context` in Furnish:SCHOOL | Themes.luau:128 |  |
| Clinic_Chair | Clinic_Chair | `export/props/Clinic_Chair.fbx` | `Clinic_Chair` | `WorldSkin.context` in Furnish:CLINIC | Themes.luau:109 |  |
| Clinic_Cabinet | Clinic_Cabinet | `export/props/Clinic_Cabinet.fbx` | `Clinic_Cabinet` | `WorldSkin.context` in Furnish:CLINIC | Themes.luau:110 |  |
| Clinic_WallScreen | Clinic_WallScreen | `export/decoration/Clinic_WallScreen.fbx` | `Clinic_WallScreen`, `Clinic_WallScreen_Glow_GREEN` | `WorldSkin.context` in Furnish:CLINIC | Themes.luau:111,112 |  |
| Hospital_WallCross | Hospital_WallCross | `export/decoration/Hospital_WallCross.fbx` | `Hospital_WallCross` | `WorldSkin.context` in Furnish:HOSPITAL | Themes.luau:94,95 |  |
| Office_Screen | Office_Screen | `export/decoration/Office_Screen.fbx` | `Office_Screen`, `Office_Screen_Glow_GLOW_COOL` | `WorldSkin.context` in Furnish:OFFICE | Themes.luau:162,163 |  |
| Garage_ToolBoard | Garage_ToolBoard | `export/decoration/Garage_ToolBoard.fbx` | `Garage_ToolBoard` | `WorldSkin.context` in Furnish:GARAGE | Themes.luau:178 |  |
| Garage_TireStack | Garage_TireStack | `export/props/Garage_TireStack.fbx` | `Garage_TireStack` | `WorldSkin.context` in Furnish:GARAGE | Themes.luau:180 |  |
| Lobby_RoomBooth | Lobby_RoomBooth | `export/buildings/Lobby_RoomBooth.fbx` | `Lobby_RoomBooth`, `Lobby_RoomBooth_Glow_GOLD`, `Lobby_RoomBooth_Glow_RED_T45`, `Lobby_RoomBooth_Glow_RED_T70` | `WorldSkin.context` in Lobby | Lobby.luau:420,421,426,427,429,430,432,433 | yes |
| Lobby_RoomBooth_v2 | Lobby_RoomBooth | `export/buildings/Lobby_RoomBooth_v2.fbx` | `Lobby_RoomBooth_v2`, `Lobby_RoomBooth_v2_Glow_BLUE_T45`, `Lobby_RoomBooth_v2_Glow_BLUE_T70`, `Lobby_RoomBooth_v2_Glow_GOLD` | `WorldSkin.context` in Lobby | Lobby.luau:420,421,426,427,429,430,432,433 | yes |
| Lobby_RoomBooth_v3 | Lobby_RoomBooth | `export/buildings/Lobby_RoomBooth_v3.fbx` | `Lobby_RoomBooth_v3`, `Lobby_RoomBooth_v3_Glow_GOLD`, `Lobby_RoomBooth_v3_Glow_GREEN_T45`, `Lobby_RoomBooth_v3_Glow_GREEN_T70` | `WorldSkin.context` in Lobby | Lobby.luau:420,421,426,427,429,430,432,433 | yes |
| Lobby_RoomBooth_v4 | Lobby_RoomBooth | `export/buildings/Lobby_RoomBooth_v4.fbx` | `Lobby_RoomBooth_v4`, `Lobby_RoomBooth_v4_Glow_GOLD`, `Lobby_RoomBooth_v4_Glow_GOLD_T45`, `Lobby_RoomBooth_v4_Glow_GOLD_T70` | `WorldSkin.context` in Lobby | Lobby.luau:420,421,426,427,429,430,432,433 | yes |
| Lobby_Pillar | Lobby_Pillar | `export/decoration/Lobby_Pillar.fbx` | `Lobby_Pillar`, `Lobby_Pillar_Glow_GLOW_WARM` | `WorldSkin.context` in Lobby | Lobby.luau:358,359,360 |  |
| Lobby_Trophy | Lobby_Trophy | `export/props/Lobby_Trophy.fbx` | `Lobby_Trophy`, `Lobby_Trophy_Glow_GOLD_LIGHT` | `WorldSkin.context` in Lobby | Lobby.luau:393,394,395,396,397,398 |  |
| Lobby_PottedPalm | Lobby_PottedPalm | `export/nature/Lobby_PottedPalm.fbx` | `Lobby_PottedPalm` | `WorldSkin.context` in Lobby | Lobby.luau:386,387 |  |
| Lobby_Bench | Lobby_Bench | `export/props/Lobby_Bench.fbx` | `Lobby_Bench` | `WorldSkin.context` in Lobby | Lobby.luau:373,374,375 |  |
| Lobby_Walls | Lobby_Walls | `export/buildings/Lobby_Walls.fbx` | `Lobby_Walls` | `WorldSkin.context` in Lobby | Lobby.luau:345,346 |  |
| Lobby_Floor | Lobby_Floor | `export/ground/Lobby_Floor.fbx` | `Lobby_Floor` | `WorldSkin.context` in Lobby | Lobby.luau:332 |  |
| Lobby_Carpet | Lobby_Carpet | `export/ground/Lobby_Carpet.fbx` | `Lobby_Carpet` | `WorldSkin.context` in Lobby | Lobby.luau:333,334 |  |
| Lobby_TitleSign | Lobby_TitleSign | `export/signs/Lobby_TitleSign.fbx` | `Lobby_TitleSign` | `WorldSkin.context` in Lobby | Lobby.luau:351 |  |
| Lobby_Window | Lobby_Window | `export/buildings/Lobby_Window.fbx` | `Lobby_Window`, `Lobby_Window_Glass` | `WorldSkin.context` in Lobby | Lobby.luau:368 |  |
| Lobby_Spawn | Lobby_Spawn | `export/ground/Lobby_Spawn.fbx` | `Lobby_Spawn` | `WorldSkin.context` in Lobby | Lobby.luau:406 | yes |
| FastTrack_Gate | FastTrack_Gate | `export/decoration/FastTrack_Gate.fbx` | `FastTrack_Gate` | `WorldSkin.context` in Workplace:FAST TRACK | Plots.luau:214,215,216 |  |
| Lux_Sofa | Lux_Sofa | `export/props/Lux_Sofa.fbx` | `Lux_Sofa` | `WorldSkin.context` in Furnish:FAST TRACK | Themes.luau:202,203 |  |
| Lux_GlassTable | Lux_GlassTable | `export/props/Lux_GlassTable.fbx` | `Lux_GlassTable`, `Lux_GlassTable_Glass` | `WorldSkin.context` in Furnish:FAST TRACK | Themes.luau:205 |  |
| Lux_Safe | Lux_Safe | `export/props/Lux_Safe.fbx` | `Lux_Safe` | `WorldSkin.context` in Furnish:FAST TRACK | Themes.luau:207,208,209 |  |
| Lux_Piano | Lux_Piano | `export/props/Lux_Piano.fbx` | `Lux_Piano` | `WorldSkin.context` in Furnish:FAST TRACK | Themes.luau:211,212 |  |
| Lux_Chandelier | Lux_Chandelier | `export/decoration/Lux_Chandelier.fbx` | `Lux_Chandelier`, `Lux_Chandelier_Glow_GLOW_WARM` | `WorldSkin.context` in Furnish:FAST TRACK | Themes.luau:214,219 |  |
| Dream_Pedestal | Dream_Pedestal | `export/props/Dream_Pedestal.fbx` | `Dream_Pedestal` | `WorldSkin.context` in DreamArea | Plots.luau:490,491 |  |
| Dream_Chains | Dream_Chains | `export/props/Dream_Chains.fbx` | `Dream_Chains` | **not imported**: replaced link by link by `Dream_ChainSegment` + `Dream_Padlock` (`WorldSkin.chains`, your decision) | Plots.luau:460,461,462,466,467,469,471 |  |
| Collection_Showcase | Collection_Showcase | `export/props/Collection_Showcase.fbx` | `Collection_Showcase` | `WorldSkin.context` in Collection | Plots.luau:556,557 |  |
| AuctionRoom_Shell | AuctionRoom_Shell | `export/buildings/AuctionRoom_Shell.fbx` | `AuctionRoom_Shell` | `WorldSkin.context` in AuctionRoom | AuctionRoom.luau:44,45,46,47,48,49 |  |
| AuctionRoom_Stage | AuctionRoom_Stage | `export/props/AuctionRoom_Stage.fbx` | `AuctionRoom_Stage`, `AuctionRoom_Stage_Glow_GOLD` | `WorldSkin.context` in AuctionRoom | AuctionRoom.luau:63,64 |  |
| AuctionRoom_BidderDesk | AuctionRoom_BidderDesk | `export/props/AuctionRoom_BidderDesk.fbx` | `AuctionRoom_BidderDesk`, `AuctionRoom_BidderDesk_Glow_GOLD_T100` | `WorldSkin.context` in AuctionRoom | AuctionRoom.luau:80 | yes |
| AuctionRoom_BidderPad | AuctionRoom_BidderPad | `export/ground/AuctionRoom_BidderPad.fbx` | `AuctionRoom_BidderPad` | `WorldSkin.context` in AuctionRoom | AuctionRoom.luau:81 |  |
| AuctionRoom_Lamp | AuctionRoom_Lamp | `export/decoration/AuctionRoom_Lamp.fbx` | `AuctionRoom_Lamp`, `AuctionRoom_Lamp_Glow_GLOW_WARM` | `WorldSkin.context` in AuctionRoom | AuctionRoom.luau:53 |  |
| AuctionRoom_TitleSign | AuctionRoom_TitleSign | `export/signs/AuctionRoom_TitleSign.fbx` | `AuctionRoom_TitleSign` | `WorldSkin.context` in AuctionRoom | AuctionRoom.luau:71 |  |
| AuctionRoom_InfoBoard | AuctionRoom_InfoBoard | `export/signs/AuctionRoom_InfoBoard.fbx` | `AuctionRoom_InfoBoard` | `WorldSkin.context` in AuctionRoom | AuctionRoom.luau:73 | yes |
| PodiumRoom_Shell | PodiumRoom_Shell | `export/buildings/PodiumRoom_Shell.fbx` | `PodiumRoom_Shell` | `WorldSkin.context` in PodiumRoom | PodiumRoom.luau:66,67 |  |
| PodiumRoom_Block | PodiumRoom_Block | `export/props/PodiumRoom_Block.fbx` | `PodiumRoom_Block` | `WorldSkin.context` in PodiumRoom | PodiumRoom.luau:79,80 | yes |
| PodiumRoom_LightStrip | PodiumRoom_LightStrip | `export/decoration/PodiumRoom_LightStrip.fbx` | `PodiumRoom_LightStrip`, `PodiumRoom_LightStrip_Glow_GOLD_T55` | `WorldSkin.context` in PodiumRoom | PodiumRoom.luau:69 |  |
| PodiumRoom_TitleSign | PodiumRoom_TitleSign | `export/signs/PodiumRoom_TitleSign.fbx` | `PodiumRoom_TitleSign` | `WorldSkin.context` in PodiumRoom | PodiumRoom.luau:72 | yes |
| PodiumRoom_Board | PodiumRoom_Board | `export/signs/PodiumRoom_Board.fbx` | `PodiumRoom_Board` | `WorldSkin.context` in PodiumRoom | PodiumRoom.luau:90 | yes |
| Baseplate | Baseplate | `export/ground/Baseplate.fbx` | `Baseplate` | `WorldSkin.object` (Step 6, `Lobby.luau`) | the place (Rojo `default.project.json`) | yes |
| Debt_BankLoan_v2 | Bank Loan | uses `Debt_BankLoan` (`export/props/Bank Loan.fbx`) | | `Debt_BankLoan`, stretched to its size by `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_CarLoan_v2 | Car Loan | uses `Debt_CarLoan` (`export/props/Car Loan.fbx`) | | `Debt_CarLoan`, stretched to its size by `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_CarLoan_v3 | Car Loan | uses `Debt_CarLoan` (`export/props/Car Loan.fbx`) | | `Debt_CarLoan`, stretched to its size by `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_CarLoan_v4 | Car Loan | uses `Debt_CarLoan` (`export/props/Car Loan.fbx`) | | `Debt_CarLoan`, stretched to its size by `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_CreditCard_v2 | Credit Card | uses `Debt_CreditCard` (`export/props/Credit Card.fbx`) | | `Debt_CreditCard`, stretched to its size by `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_CreditCard_v3 | Credit Card | uses `Debt_CreditCard` (`export/props/Credit Card.fbx`) | | `Debt_CreditCard`, stretched to its size by `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_OtherDebt_v2 | Other Debt | uses `Debt_OtherDebt` (`export/props/Debt Crate.fbx`) | | `Debt_OtherDebt`, stretched to its size by `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_SchoolLoan_v2 | School Loan | uses `Debt_SchoolLoan_books7` (`export/props/School Loan (7 books).fbx`) | | its own 7-book model, picked by `WorldSkin.debtTemplate` | Props.debtModel (Props.luau:325) | yes |
| Debt_SchoolLoan_v3 | School Loan | uses `Debt_SchoolLoan_books4` (`export/props/School Loan (4 books).fbx`) | | its own 4-book model, picked by `WorldSkin.debtTemplate` | Props.debtModel (Props.luau:325) | yes |
| Lobby_PottedPalm_v2 | Lobby_PottedPalm | uses `Lobby_PottedPalm` (`export/nature/Lobby_PottedPalm.fbx`) | | `Lobby_PottedPalm`, placed turned / moved by `WorldSkin.context` (same size) | Lobby.luau:386,387 |  |

Extra kit meshes: `Debt_SchoolLoan_books2` (`export/props/School Loan (2 books).fbx`), `Debt_SchoolLoan_books4` (`export/props/School Loan (4 books).fbx`), `Debt_SchoolLoan_books5` (`export/props/School Loan (5 books).fbx`), `Debt_SchoolLoan_books6` (`export/props/School Loan (6 books).fbx`), `Debt_SchoolLoan_books7` (`export/props/School Loan (7 books).fbx`), `Dream_ChainSegment` (`export/props/ChainSegment.fbx`), `Dream_Padlock` (`export/props/Padlock.fbx`), `Kid_v4` (`export/props/Kid (green).fbx`), `Maker_PokeBloxCard_case2` (`export/props/PokeBlox Card (case 2).fbx`), `Maker_PokeBloxCard_case3` (`export/props/PokeBlox Card (case 3).fbx`), `Maker_PokeBloxCard_case4` (`export/props/PokeBlox Card (case 4).fbx`), `Maker_ShinyPokeBloxCard_case1` (`export/props/Shiny PokeBlox Card (case 1).fbx`), `Maker_ShinyPokeBloxCard_case2` (`export/props/Shiny PokeBlox Card (case 2).fbx`), `Maker_ShinyPokeBloxCard_case4` (`export/props/Shiny PokeBlox Card (case 4).fbx`). `Dream_ChainSegment` and `Dream_Padlock` are used by `WorldSkin.chains`; `WorldSkin.debtTemplate` picks the `Debt_SchoolLoan_books<n>` meshes by the number of books, `WorldSkin.makerTemplate` the `..._case<n>` PokeBlox cards by the case color of the card's value, `WorldSkin.kidTemplate` `Kid_v4` for the 4th (green) shirt. The card cases and `Kid_v4` were not in the snapshot, but the game makes them; the 4- and 7-book School Loans were (`Debt_SchoolLoan_v3`, `_v2`).


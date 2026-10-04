# Import plan - how to swap the new look into the game (NOT executed)

Written 2026-10-04 21:49. Nothing here has been done: nothing was uploaded, published or changed in `src/`.

## The idea in one paragraph

The world is built by Luau code when the server starts (and while a game runs), so the swap also happens in code: right after the game builds something, a small module (`WorldSkin`) makes the old parts invisible and puts a copy of the new model on exactly the same spot. The old parts keep **all** their jobs - collision, prompts, SurfaceGui text, lights, the invisible barriers and buy buttons - so gameplay cannot change. The new MeshParts are visual only. One switch (`WorldSkin.ENABLED = false`) brings the old look back.

## Step 1 - safety first

1. Make a git branch in the game repo (e.g. `new-look`). Do the steps below in a copy of the place, not the live game.
2. You will add 2 files to `src/` and ~12 one-line calls; everything else happens in Studio.

## Step 2 - upload the palette (2 images)

Upload `world_overhaul/palette/palette_color.png` and `palette_roughness.png` (Asset Manager > Import, or Bulk Import). Note both asset ids. These two images color **every** model in the world.

## Step 3 - import the meshes

Import every file in `world_overhaul/export/<category>/*.fbx` with the 3D Importer (File > Import 3D). Settings ([Roblox: Blender to Studio settings](https://github.com/Roblox/creator-docs/blob/main/content/en-us/art/blender.md)):

| section | setting | value | why |
|---|---|---|---|
| File General | Import Only as a Model | on | body + glow + glass meshes stay together in one Model |
| File General | Upload to Roblox | on | gives the MeshIds |
| File General | Insert Using Scene Position | **on** | the FBX origin IS the original object's frame - it must not move |
| File Transform | World Forward / World Up | Front / Top | (see the check below) |
| File Geometry | Scale Unit | **Stud** | 1 Blender unit = 1 stud |

**Check on the first model before importing the rest:** import `export/buildings/Workplace_Building_PIZZERIA.fbx` at the origin and compare with the numbers in `data/model_status.json` -> `bbox_new` (Roblox x, y, z): the open front of the building must be on the **-Z** side and the box must span x -23..23, y 0..~20. If the building is turned 180 degrees, set World Forward to **Back** for every import (the FBX files were exported with Blender's default axes: forward -Z, up Y, so the file coordinates are already Roblox coordinates).

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
			local glow = p.Name:match("_Glow_([A-Z_]+)")
			if glow then
				local color, t = glow:match("^(.-)_T(%d+)$")
				p.Material = Enum.Material.Neon
				p.Color = GLOW[color or glow]
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

Copy `world_overhaul/export/roblox/WorldSkin.luau` and `WorldSkinPlacements.luau` to `src/server/World/`. `WorldSkinPlacements` is generated from the world data: every kit model's frame relative to the base CFrame of the code that builds it.

## Step 6 - the calls (one line each)

`local WorldSkin = require(script.Parent.WorldSkin)` at the top of each file (path as needed), then:

| file / function | where | add |
|---|---|---|
| `Lobby.luau` `buildHall()` | at the end | `WorldSkin.context("Lobby", <hall origin CFrame>, <hall folder>)` |
| `World/Plaza.luau` `Plaza.new` | at the end | `WorldSkin.context("Plaza", <city base>, <city plaza folder>)` |
| `World/AuctionRoom.luau` `AuctionRoom.new` | at the end | `WorldSkin.context("AuctionRoom", self.base, <room folder>)` |
| `World/PodiumRoom.luau` `PodiumRoom.new` | at the end | `WorldSkin.context("PodiumRoom", self.base, <room folder>)` |
| `World/Plots.luau` `Plots:buildWorkplace(theme)` | at the end | `WorldSkin.context("Workplace:" .. theme.name, self.base, self.workplaceFolder)` and `WorldSkin.context("Furnish:" .. theme.name, self.base, self.workplaceFolder)` |
| `World/Plots.luau` `Plots:syncCollection` | after the showcase table is made | `WorldSkin.context("Collection", self.base, <showcase part or folder>)` |
| `World/Plots.luau` `syncDream` / `addChains` (Fast Track) | after the pedestal / chains are made | `WorldSkin.context("DreamArea", self.base, <pedestal + chains>)` |
| `World/Props.luau` `Props.kid` | before `return model` | `WorldSkin.object(model, <Kid / Kid_v2 / Kid_v3 by shirt color>, base)` |
| `World/Props.luau` `Props.moneyMaker` | before `model.Parent = parent` | `WorldSkin.object(model, <template for name>, base)` |
| `World/Props.luau` `Props.debtModel` | before `model.Parent = parent` | `WorldSkin.stretched(model, <template for debtName>, base)` (School Loan: `Debt_SchoolLoan_books<n>`) |
| `World/Props.luau` `Props.dream` | right after `builder.build()` | `WorldSkin.object(model, "Dream_" .. <name>, model:GetPivot())` |
| `World/Props.luau` `Props.tree` | before it returns | `WorldSkin.object(<tree model>, "Tree", base)` |
| `World/AuctionRoom.luau` `AuctionRoom:highlight` | inside the loop | `WorldSkin.setVisible(<desk glow shell>, isTop)`: the old desk turns gold Neon, the new desk has a hidden gold shell (`_Glow_GOLD_T100`) for that |
| `World/PodiumRoom.luau` `fillBoard` (line 158) | next to `self.board.Transparency = ...` | `WorldSkin.setVisible(<board kit copy>, #standings > 3)` |

Why these places: the ghost FOR SALE copies (`Props.makeGhost`), the 0.4x collection minis (`model:ScaleTo(0.4)`), the floating dreams (`ScaleTo` + `PivotTo`), the kids' hop and the dream spin (`PivotTo`) all run **after** these builders return, so they automatically include the new MeshParts (they are BaseParts inside the same Model).

## Step 7 - test in Studio (Play Solo, then 2-4 players)

- [ ] Lobby: walk around, the room booths still open, the spawn still works, the trophy and palms look right.
- [ ] Start a game: your workplace appears with the new building, furniture, fence, lamps and yard; you still walk on the same floor heights, the Pay/Buy prompts still appear on the debts and the FOR SALE item.
- [ ] Buy a Money Maker: it stands on the lot, the next one stacks on top at the same height as before (`GetBoundingBox`), its label floats at the same spot.
- [ ] The FOR SALE copy looks see-through (ForceField) - also the new meshes.
- [ ] Add investments: the minis in the showcase are 0.4x and sit on the table.
- [ ] Your dream floats and spins; it fades in/out as before (the old parts must stay hidden while it fades).
- [ ] Escape: the workplace turns into the Fast Track version (new look too), pedestal + chains.
- [ ] Auction: the top bidder's desk glows gold. Podium: the board shows only with more than 3 players.
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

| template (= WorldKit name) | FBX | meshes | how it is placed | built by (game code) | script-referenced |
|---|---|---|---|---|---|
| Workplace_Building_PIZZERIA | `export/buildings/Workplace_Building_PIZZERIA.fbx` | `Workplace_Building_PIZZERIA`, `Workplace_Building_PIZZERIA_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:PIZZERIA")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_BUSDEPOT | `export/buildings/Workplace_Building_BUSDEPOT.fbx` | `Workplace_Building_BUSDEPOT`, `Workplace_Building_BUSDEPOT_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:BUS DEPOT")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_HOSPITAL | `export/buildings/Workplace_Building_HOSPITAL.fbx` | `Workplace_Building_HOSPITAL`, `Workplace_Building_HOSPITAL_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:HOSPITAL")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_CLINIC | `export/buildings/Workplace_Building_CLINIC.fbx` | `Workplace_Building_CLINIC`, `Workplace_Building_CLINIC_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:CLINIC")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_SCHOOL | `export/buildings/Workplace_Building_SCHOOL.fbx` | `Workplace_Building_SCHOOL`, `Workplace_Building_SCHOOL_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:SCHOOL")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_POLICE | `export/buildings/Workplace_Building_POLICE.fbx` | `Workplace_Building_POLICE`, `Workplace_Building_POLICE_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:POLICE")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_OFFICE | `export/buildings/Workplace_Building_OFFICE.fbx` | `Workplace_Building_OFFICE`, `Workplace_Building_OFFICE_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:OFFICE")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_GARAGE | `export/buildings/Workplace_Building_GARAGE.fbx` | `Workplace_Building_GARAGE`, `Workplace_Building_GARAGE_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:GARAGE")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Building_FASTTRACK | `export/buildings/Workplace_Building_FASTTRACK.fbx` | `Workplace_Building_FASTTRACK`, `Workplace_Building_FASTTRACK_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:FAST TRACK")` | Plots.luau:131,135,136,137,138,143,144,147,148,153,154,155,162,166,167,169 |  |
| Workplace_Yard_v2 | `export/ground/Workplace_Yard_v2.fbx` | `Workplace_Yard_v2` | `WorldSkin.context("Workplace:PIZZERIA")` | Plots.luau:130,132 |  |
| Workplace_Yard | `export/ground/Workplace_Yard.fbx` | `Workplace_Yard` | `WorldSkin.context("Workplace:FAST TRACK")` | Plots.luau:130,132 | yes |
| Workplace_MakerLot | `export/ground/Workplace_MakerLot.fbx` | `Workplace_MakerLot` | `WorldSkin.context("Workplace:FAST TRACK")` | Plots.luau:176 | yes |
| Workplace_Fence | `export/decoration/Workplace_Fence.fbx` | `Workplace_Fence` | `WorldSkin.context("Workplace:FAST TRACK")` | Plots.luau:183,186 | yes |
| Workplace_LampPost | `export/decoration/Workplace_LampPost.fbx` | `Workplace_LampPost`, `Workplace_LampPost_Glow_GLOW_WARM` | `WorldSkin.context("Workplace:FAST TRACK")` | Plots.luau:189,190 | yes |
| Workplace_FlowerBox | `export/decoration/Workplace_FlowerBox.fbx` | `Workplace_FlowerBox` | `WorldSkin.context("Workplace:FAST TRACK")` | Plots.luau:200,202 | yes |
| Workplace_Sandbox | `export/props/Workplace_Sandbox.fbx` | `Workplace_Sandbox` | `WorldSkin.context("Workplace:FAST TRACK")` | Plots.luau:207,209 | yes |
| Workplace_DebtPad | `export/ground/Workplace_DebtPad.fbx` | `Workplace_DebtPad` | `WorldSkin.context("Workplace:PIZZERIA")` | Plots.luau:218 | yes |
| Plaza_Fountain | `export/decoration/Plaza_Fountain.fbx` | `Plaza_Fountain`, `Plaza_Fountain_Glass`, `Plaza_Fountain_Glow_GLOW_COOL` | `WorldSkin.context("Plaza")` | Plaza.luau:69,70,71,72 |  |
| Tree | `export/nature/Tree.fbx` | `Tree` | `WorldSkin.object` | Props.tree (Props.luau:352) |  |
| Plaza_Disc | `export/ground/Plaza_Disc.fbx` | `Plaza_Disc` | `WorldSkin.context("Plaza")` | Plaza.luau:52 |  |
| Plaza_Path | `export/ground/Plaza_Path.fbx` | `Plaza_Path` | `WorldSkin.context("Plaza")` | Plaza.luau:58 |  |
| City_Ground | `export/ground/City_Ground.fbx` | `City_Ground` | `WorldSkin.context("Plaza")` | Plaza.luau:35 |  |
| City_Wall | `export/decoration/City_Wall.fbx` | `City_Wall` | `WorldSkin.context("Plaza")` | Plaza.luau:43,44 |  |
| Dream_Supercar | `export/vehicles/Supercar.fbx` | `Supercar`, `Supercar_Glow_GLOW_WARM` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_Yacht | `export/vehicles/Yacht.fbx` | `Yacht` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_BeachVilla | `export/buildings/BeachVilla.fbx` | `BeachVilla`, `BeachVilla_Glass`, `BeachVilla_Glow_GLOW_WARM` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_PrivateJet | `export/vehicles/PrivateJet.fbx` | `PrivateJet` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Dream_PrivateIsland | `export/nature/PrivateIsland.fbx` | `PrivateIsland` | `WorldSkin.object` | Props.dream (Props.luau:604) | yes |
| Maker_LemonadeStand | `export/props/Lemonade Stand.fbx` | `Maker_LemonadeStand` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_VendingMachine | `export/props/Vending Machine.fbx` | `Maker_VendingMachine`, `Maker_VendingMachine_Glow_GLOW_COOL` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_Apartment | `export/buildings/Apartment.fbx` | `Maker_Apartment`, `Maker_Apartment_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_CarWash | `export/buildings/Car Wash.fbx` | `Maker_CarWash`, `Maker_CarWash_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_FoodTruck | `export/vehicles/Food Truck.fbx` | `Maker_FoodTruck`, `Maker_FoodTruck_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ToyShop | `export/buildings/Toy Shop.fbx` | `Maker_ToyShop` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_MiniGolf | `export/props/Mini Golf.fbx` | `Maker_MiniGolf` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_HouseToRent | `export/buildings/House to Rent.fbx` | `Maker_HouseToRent` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_PizzaRestaurant | `export/buildings/Pizza Restaurant.fbx` | `Maker_PizzaRestaurant`, `Maker_PizzaRestaurant_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_CoffeeShop | `export/buildings/Coffee Shop.fbx` | `Maker_CoffeeShop`, `Maker_CoffeeShop_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_BowlingAlley | `export/buildings/Bowling Alley.fbx` | `Maker_BowlingAlley`, `Maker_BowlingAlley_Glow_GLOW_COOL` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_Hotel | `export/buildings/Hotel.fbx` | `Maker_Hotel`, `Maker_Hotel_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GameStudio | `export/buildings/Game Studio.fbx` | `Maker_GameStudio`, `Maker_GameStudio_Glow_GLOW_COOL` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ShoppingMall | `export/buildings/Shopping Mall.fbx` | `Maker_ShoppingMall` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ApartmentBuilding | `export/buildings/Apartment Building.fbx` | `Maker_ApartmentBuilding`, `Maker_ApartmentBuilding_Glow_GLOW_WARM` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_ThemePark | `export/props/Theme Park.fbx` | `Maker_ThemePark` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_PokeBloxCard | `export/props/PokeBlox Card.fbx` | `Maker_PokeBloxCard`, `Maker_PokeBloxCard_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_RarePokeBloxCard | `export/props/Rare PokeBlox Card.fbx` | `Maker_RarePokeBloxCard`, `Maker_RarePokeBloxCard_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_RarePokeBloxCard_v2 | `export/props/Rare PokeBlox Card (case 2).fbx` | `Maker_RarePokeBloxCard_v2`, `Maker_RarePokeBloxCard_v2_Glass` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) |  |
| Maker_RarePokeBloxCard_v3 | `export/props/Rare PokeBlox Card (case 3).fbx` | `Maker_RarePokeBloxCard_v3`, `Maker_RarePokeBloxCard_v3_Glass`, `Maker_RarePokeBloxCard_v3_Glow_PURPLE` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) |  |
| Maker_RarePokeBloxCard_v4 | `export/props/Rare PokeBlox Card (case 4).fbx` | `Maker_RarePokeBloxCard_v4`, `Maker_RarePokeBloxCard_v4_Glass`, `Maker_RarePokeBloxCard_v4_Glow_GOLD` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) |  |
| Maker_ShinyPokeBloxCard | `export/props/Shiny PokeBlox Card.fbx` | `Maker_ShinyPokeBloxCard`, `Maker_ShinyPokeBloxCard_Glass`, `Maker_ShinyPokeBloxCard_Glow_GLOW_COOL`, `Maker_ShinyPokeBloxCard_Glow_PURPLE` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GoldCoin | `export/props/Gold Coin.fbx` | `Maker_GoldCoin` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GoldBar | `export/props/Gold Bar.fbx` | `Maker_GoldBar` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_GoldTreasureChest | `export/props/Gold Treasure Chest.fbx` | `Maker_GoldTreasureChest` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Maker_UnknownMaker | `export/props/Unknown Maker.fbx` | `Maker_UnknownMaker` | `WorldSkin.object` | Props.moneyMaker (Props.luau:583) | yes |
| Kid | `export/props/Kid.fbx` | `Kid` | `WorldSkin.object` | Props.kid (Props.luau:220) | yes |
| Kid_v2 | `export/props/Kid (blue).fbx` | `Kid_v2` | `WorldSkin.object` | Props.kid (Props.luau:220) |  |
| Kid_v3 | `export/props/Kid (yellow).fbx` | `Kid_v3` | `WorldSkin.object` | Props.kid (Props.luau:220) |  |
| Debt_CreditCard | `export/props/Credit Card.fbx` | `Debt_CreditCard` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_CarLoan | `export/props/Car Loan.fbx` | `Debt_CarLoan` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_SchoolLoan | `export/props/School Loan.fbx` | `Debt_SchoolLoan` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_BankLoan | `export/props/Bank Loan.fbx` | `Debt_BankLoan` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Debt_OtherDebt | `export/props/Debt Crate.fbx` | `Debt_OtherDebt` | `WorldSkin.stretched` | Props.debtModel (Props.luau:325) | yes |
| Depot_Bus | `export/vehicles/Depot_Bus.fbx` | `Depot_Bus`, `Depot_Bus_Glow_GLOW_WARM` | `WorldSkin.context("Furnish:BUS DEPOT")` | Themes.luau:71,73,77 |  |
| Police_Car | `export/vehicles/Police_Car.fbx` | `Police_Car`, `Police_Car_Glow_BLUE`, `Police_Car_Glow_GLOW_WARM`, `Police_Car_Glow_RED` | `WorldSkin.context("Furnish:POLICE")` | Themes.luau:144,145 |  |
| Garage_CarLift | `export/vehicles/Garage_CarLift.fbx` | `Garage_CarLift`, `Garage_CarLift_Glow_GLOW_WARM` | `WorldSkin.context("Furnish:GARAGE")` | Themes.luau:175,176 |  |
| Computer | `export/props/Computer.fbx` | `Computer`, `Computer_Glow_GLOW_COOL` | `WorldSkin.context("Furnish:CLINIC")` | Themes.luau:31,36,37 |  |
| HospitalBed | `export/props/HospitalBed.fbx` | `HospitalBed` | `WorldSkin.context("Furnish:HOSPITAL")` | Themes.luau:41,42,43 |  |
| Pizzeria_Counter | `export/props/Pizzeria_Counter.fbx` | `Pizzeria_Counter` | `WorldSkin.context("Furnish:PIZZERIA")` | Themes.luau:54,55,58 |  |
| Pizzeria_Oven | `export/props/Pizzeria_Oven.fbx` | `Pizzeria_Oven`, `Pizzeria_Oven_Glow_ORANGE` | `WorldSkin.context("Furnish:PIZZERIA")` | Themes.luau:56,57 |  |
| School_Blackboard | `export/decoration/School_Blackboard.fbx` | `School_Blackboard` | `WorldSkin.context("Furnish:SCHOOL")` | Themes.luau:124 |  |
| School_TeacherDesk | `export/props/School_TeacherDesk.fbx` | `School_TeacherDesk` | `WorldSkin.context("Furnish:SCHOOL")` | Themes.luau:31 |  |
| School_StudentDesk | `export/props/School_StudentDesk.fbx` | `School_StudentDesk` | `WorldSkin.context("Furnish:SCHOOL")` | Themes.luau:128 |  |
| Clinic_Chair | `export/props/Clinic_Chair.fbx` | `Clinic_Chair` | `WorldSkin.context("Furnish:CLINIC")` | Themes.luau:109 |  |
| Clinic_Cabinet | `export/props/Clinic_Cabinet.fbx` | `Clinic_Cabinet` | `WorldSkin.context("Furnish:CLINIC")` | Themes.luau:110 |  |
| Clinic_WallScreen | `export/decoration/Clinic_WallScreen.fbx` | `Clinic_WallScreen`, `Clinic_WallScreen_Glow_GREEN` | `WorldSkin.context("Furnish:CLINIC")` | Themes.luau:111,112 |  |
| Hospital_WallCross | `export/decoration/Hospital_WallCross.fbx` | `Hospital_WallCross` | `WorldSkin.context("Furnish:HOSPITAL")` | Themes.luau:94,95 |  |
| Office_Screen | `export/decoration/Office_Screen.fbx` | `Office_Screen`, `Office_Screen_Glow_GLOW_COOL` | `WorldSkin.context("Furnish:OFFICE")` | Themes.luau:162,163 |  |
| Garage_ToolBoard | `export/decoration/Garage_ToolBoard.fbx` | `Garage_ToolBoard` | `WorldSkin.context("Furnish:GARAGE")` | Themes.luau:178 |  |
| Garage_TireStack | `export/props/Garage_TireStack.fbx` | `Garage_TireStack` | `WorldSkin.context("Furnish:GARAGE")` | Themes.luau:180 |  |
| Lobby_RoomBooth | (not modelled) | | | | |
| Lobby_RoomBooth_v2 | (not modelled) | | | | |
| Lobby_RoomBooth_v3 | (not modelled) | | | | |
| Lobby_RoomBooth_v4 | (not modelled) | | | | |
| Lobby_Pillar | (not modelled) | | | | |
| Lobby_Trophy | (not modelled) | | | | |
| Lobby_PottedPalm | (not modelled) | | | | |
| Lobby_Bench | (not modelled) | | | | |
| Lobby_Walls | (not modelled) | | | | |
| Lobby_Floor | (not modelled) | | | | |
| Lobby_Carpet | (not modelled) | | | | |
| Lobby_TitleSign | (not modelled) | | | | |
| Lobby_Window | (not modelled) | | | | |
| Lobby_Spawn | (not modelled) | | | | |
| FastTrack_Gate | (not modelled) | | | | |
| Lux_Sofa | (not modelled) | | | | |
| Lux_GlassTable | (not modelled) | | | | |
| Lux_Safe | (not modelled) | | | | |
| Lux_Piano | (not modelled) | | | | |
| Lux_Chandelier | (not modelled) | | | | |
| Dream_Pedestal | (not modelled) | | | | |
| Dream_Chains | (not modelled) | | | | |
| Collection_Showcase | (not modelled) | | | | |
| AuctionRoom_Shell | (not modelled) | | | | |
| AuctionRoom_Stage | (not modelled) | | | | |
| AuctionRoom_BidderDesk | (not modelled) | | | | |
| AuctionRoom_BidderPad | (not modelled) | | | | |
| AuctionRoom_Lamp | (not modelled) | | | | |
| AuctionRoom_TitleSign | (not modelled) | | | | |
| AuctionRoom_InfoBoard | (not modelled) | | | | |
| PodiumRoom_Shell | (not modelled) | | | | |
| PodiumRoom_Block | (not modelled) | | | | |
| PodiumRoom_LightStrip | (not modelled) | | | | |
| PodiumRoom_TitleSign | (not modelled) | | | | |
| PodiumRoom_Board | (not modelled) | | | | |
| Baseplate | (not modelled) | | | | |
| Debt_BankLoan_v2 | uses `Debt_BankLoan` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_CarLoan_v2 | uses `Debt_CarLoan` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_CarLoan_v3 | uses `Debt_CarLoan` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_CarLoan_v4 | uses `Debt_CarLoan` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_CreditCard_v2 | uses `Debt_CreditCard` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_CreditCard_v3 | uses `Debt_CreditCard` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_OtherDebt_v2 | uses `Debt_OtherDebt` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_SchoolLoan_v2 | uses `Debt_SchoolLoan` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Debt_SchoolLoan_v3 | uses `Debt_SchoolLoan` | | stretched to its own size | Props.debtModel (Props.luau:325) |  |
| Lobby_PottedPalm_v2 | uses `Lobby_PottedPalm` | | stretched to its own size |  |  |

Extra kit meshes: `Debt_SchoolLoan_books2` (`export/props/School Loan (2 books).fbx`), `Debt_SchoolLoan_books4` (`export/props/School Loan (4 books).fbx`), `Debt_SchoolLoan_books5` (`export/props/School Loan (5 books).fbx`), `Debt_SchoolLoan_books6` (`export/props/School Loan (6 books).fbx`), `Debt_SchoolLoan_books7` (`export/props/School Loan (7 books).fbx`).


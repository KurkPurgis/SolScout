# Progress

If you (or I after a restart) pick this up: read this file and STYLE_GUIDE.md first.
Updated: 2026-10-05 09:33

## Current step

Done. All 125 templates (98 object types) are covered (115 own models + 10 that reuse another kit model), plus 14 extra kit models (chain segment, padlock, School Loan sizes, PokeBlox card cases, the 4th kid): 129 kit models, all reviewed. Your answers of 2026-10-05 are in (no outline, chains link by link, warm glow kept, bbox exceptions accepted); questions 4, 6 and 7 in REPORT.md are still open. The import plan was fixed after a review (tree frames, Fast Track duplicates, glow script, missing-kit safety) and is checked by tools/verify_placements.py and the two Luau tests in tools/luau/.

## How to continue

- Build/render/export one category: `/home/user/bvenv/bin/python tools/blender/make_models.py <category> [templates]`
- Look at `renders/objects/strips/<template>.jpg`, then `python3 tools/set_status.py <template> done|needs_review "note"`
- Model code: `tools/blender/models/<category>.py`; kit: `tools/blender/kit.py`, `tools/blender/parts.py`
- Blueprint of the original parts: `python3 tools/blueprint.py <template> [ctx]`

## Summary

alias: 10, done: 115, extra done: 14 (129 kit models in all, 129 FBX files)

## Phases

- [x] Phase 1 - inventory (world extracted, INVENTORY.md, BEFORE renders)
- [x] Phase 2 - style guide, palette, kit
- [x] Phase 3 - model everything
- [x] Phase 4 - whole world check (AFTER renders)
- [x] Phase 5 - handover (REPORT.md, IMPORT_PLAN.md)

## Models (in modelling order: most visible first)

| # | template | category | status | triangles | bbox dev | note |
|---|---|---|---|---|---|---|
| 1 | Workplace_Building_PIZZERIA | buildings | done | 5188 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 2 | Workplace_Building_BUSDEPOT | buildings | done | 5076 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 3 | Workplace_Building_HOSPITAL | buildings | done | 5252 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 4 | Workplace_Building_CLINIC | buildings | done | 5076 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 5 | Workplace_Building_SCHOOL | buildings | done | 5164 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 6 | Workplace_Building_POLICE | buildings | done | 5184 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 7 | Workplace_Building_OFFICE | buildings | done | 5076 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 8 | Workplace_Building_GARAGE | buildings | done | 5076 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 9 | Workplace_Building_FASTTRACK | buildings | done | 5260 | 0.09 | open-front workplace in the job colors: pillars, striped awning, big sign, lit side windows, two sign lamps, a roof detail |
| 10 | Workplace_Yard_v2 | ground | done | 716 | 0.0 | workplace yard: warm grey slab with a tiled path to the door |
| 11 | Workplace_Yard | ground | done | 256 | 0.0 | Fast Track yard: cream marble with a red carpet and gold edges (the luxury version) |
| 12 | Workplace_MakerLot | ground | done | 188 | 0.15 | sand lot with a gold coin marker |
| 13 | Workplace_Fence | decoration | done | 912 | 0.073 | white rounded fence |
| 14 | Workplace_LampPost | decoration | done | 404 | 0.06 | steel post with a warm glowing bulb |
| 15 | Workplace_FlowerBox | decoration | done | 752 | 0.06 | wooden box with three flower bushes |
| 16 | Workplace_Sandbox | props | done | 768 | 0.15 | wooden sandbox with a bucket and a toy |
| 17 | Workplace_DebtPad | ground | done | 152 | 0.1 | slate pad with a lighter rim |
| 18 | Plaza_Fountain | decoration | done | 2816 | 0.0 | round stone basin, water, glowing ball on a pedestal |
| 19 | Tree | nature | done | 1064 | 0.05 | round icon tree with two greens and a few apples on a tall trunk |
| 20 | Plaza_Disc | ground | done | 2744 | 0.0 | stone plaza disc with a darker rim and gold studs |
| 21 | Plaza_Path | ground | done | 684 | 0.0 | stone path tiles with a darker edge |
| 22 | City_Ground | ground | done | 76 | 0.0 | matte grass slab (the city ground) |
| 23 | City_Wall | decoration | done | 1728 | 0.1 | stone wall with a lighter cap, corner pillars with gold balls |
| 24 | Dream_Supercar | vehicles | done | 2696 | 0.125 | wheels inside the original box |
| 25 | Dream_Yacht | vehicles | done | 3856 | 0.15 | chunky white yacht, navy hull, wood deck, sun loungers |
| 26 | Dream_BeachVilla | buildings | done | 5528 | 0.218 | front edge 0.22 shallower than the original box (the old stair parts); villa, pool, palms |
| 27 | Dream_PrivateJet | vehicles | done | 3600 | 0.098 | tailplane inside the box |
| 28 | Dream_PrivateIsland | nature | done | 5608 | 0.15 | island, palms, dock, hut; water ring |
| 29 | Maker_LemonadeStand | props | done | 1064 | 0.023 | umbrella, lemons and glasses |
| 30 | Maker_VendingMachine | props | done | 720 | 0.13 | snacks on lit shelves, no z-fight on the top |
| 31 | Maker_Apartment | buildings | done | 900 | 0.12 | stone plinth instead of a step that stuck out |
| 32 | Maker_CarWash | buildings | done | 1132 | 0.06 | brushes and soap bubbles; sign fits the roof beam |
| 33 | Maker_FoodTruck | vehicles | done | 2344 | 0.13 | rebuilt inside the original box: cab, windshield, hatch, taco |
| 34 | Maker_ToyShop | buildings | done | 1308 | 0.027 | roof rim no longer z-fights; toy blocks by the door |
| 35 | Maker_MiniGolf | props | done | 828 | 0.0 | green with flag, windmill obstacle |
| 36 | Maker_HouseToRent | buildings | done | 1276 | 0.133 | door and windows sunk into the wall to keep the box; chimney with cap |
| 37 | Maker_PizzaRestaurant | buildings | done | 1268 | 0.027 | pizza slice on the wall beside the sign |
| 38 | Maker_CoffeeShop | buildings | done | 1280 | 0.05 | wood shop, cream awning, cafe table with a cup |
| 39 | Maker_BowlingAlley | buildings | done | 1516 | 0.027 | giant bowling ball and pin on the roof |
| 40 | Maker_Hotel | buildings | done | 2124 | 0.05 | lit window grid, gold frames, red entrance canopy |
| 41 | Maker_GameStudio | buildings | done | 1424 | 0.027 | game controller in front of the glowing window |
| 42 | Maker_ShoppingMall | buildings | done | 1228 | 0.027 | banners above the awning |
| 43 | Maker_ApartmentBuilding | buildings | done | 1712 | 0.05 | brick tower with lit windows |
| 44 | Maker_ThemePark | props | done | 1136 | 0.08 | ferris wheel with colorful gondolas |
| 45 | Maker_PokeBloxCard | props | done | 936 | 0.043 | icon card in a glass case |
| 46 | Maker_RarePokeBloxCard | props | done | 936 | 0.043 | same model, case color per rarity |
| 47 | Maker_RarePokeBloxCard_v2 | props | done | 936 | 0.043 | same model, case color per rarity |
| 48 | Maker_RarePokeBloxCard_v3 | props | done | 936 | 0.043 | same model, case color per rarity |
| 49 | Maker_RarePokeBloxCard_v4 | props | done | 936 | 0.043 | same model, case color per rarity |
| 50 | Maker_ShinyPokeBloxCard | props | done | 936 | 0.043 | glowing card, purple (EPIC) case |
| 51 | Maker_GoldCoin | props | done | 580 | 0.0 | icon coin on a stand |
| 52 | Maker_GoldBar | props | done | 648 | 0.029 | icon gold bars stacked 3-2-1 |
| 53 | Maker_GoldTreasureChest | props | done | 856 | 0.077 | lock moved inside the box |
| 54 | Maker_UnknownMaker | props | done | 752 | 0.14 | orange question marks on the sides |
| 55 | Kid | props | done | 538 | 0.113 | hair fixed (was z-fighting), smaller eyes |
| 56 | Kid_v2 | props | done | 538 | 0.113 | blue shirt variant |
| 57 | Kid_v3 | props | done | 538 | 0.113 | yellow shirt variant |
| 58 | Debt_CreditCard | props | done | 320 | 0.015 | rebuilt at the copy's size (amount scale) |
| 59 | Debt_CarLoan | props | done | 1052 | 0.06 | grey toy car with red LOAN tag |
| 60 | Debt_SchoolLoan | props | done | 512 | 0.042 | cap lowered to the original height |
| 61 | Debt_BankLoan | props | done | 384 | 0.017 | rebuilt at the copy's size |
| 62 | Debt_OtherDebt | props | done | 336 | 0.12 | straps no longer coplanar |
| 63 | Depot_Bus | vehicles | done | 2832 | 0.13 | yellow bus, windows, door, lights |
| 64 | Police_Car | vehicles | done | 1700 | 0.12 | white toy car, navy doors with a gold star, red/blue lights |
| 65 | Garage_CarLift | vehicles | done | 1744 | 0.06 | red car up on a two-post lift with hazard stripes |
| 66 | Computer | props | done | 468 | 0.1 | desk with monitor and a red mug |
| 67 | HospitalBed | props | done | 496 | 0.025 | cross moved onto the blanket |
| 68 | Pizzeria_Counter | props | done | 516 | 0.07 | white counter with red and green stripes, a pizza on the green top and a pizza box |
| 69 | Pizzeria_Oven | props | done | 462 | 0.1 | clay dome, brick mouth, fire glow, logs; fits the original box now |
| 70 | School_Blackboard | decoration | done | 272 | 0.275 | 1 + 1 = 2 reads left to right from the room |
| 71 | School_TeacherDesk | props | done | 264 | 0.13 | top at the original height; apple badge and exercise book |
| 72 | School_StudentDesk | props | done | 264 | 0.13 | desk with a pencil |
| 73 | Clinic_Chair | props | done | 272 | 0.05 | swivel chair |
| 74 | Clinic_Cabinet | props | done | 288 | 0.0 | red cross from non-overlapping pieces; doors inside the box |
| 75 | Clinic_WallScreen | decoration | done | 184 | 0.245 | heartbeat line, no overlapping bars |
| 76 | Hospital_WallCross | decoration | done | 332 | 0.0 | chunky red cross |
| 77 | Office_Screen | decoration | done | 232 | 0.25 | bar chart grows to the right |
| 78 | Garage_ToolBoard | decoration | done | 372 | 0.3 | wrench, hammer, screwdriver |
| 79 | Garage_TireStack | props | done | 1052 | 0.05 | 4 fat tires |
| 80 | Lobby_RoomBooth | buildings | done | 1440 | 0.065 | platform, two pillars, glowing portal pane, name beam with a star |
| 81 | Lobby_RoomBooth_v2 | buildings | done | 1440 | 0.065 | room color variant |
| 82 | Lobby_RoomBooth_v3 | buildings | done | 1440 | 0.065 | room color variant |
| 83 | Lobby_RoomBooth_v4 | buildings | done | 1440 | 0.065 | room color variant |
| 84 | Lobby_Pillar | decoration | done | 628 | 0.034 | marble column with gold cap, base and a lamp |
| 85 | Lobby_Trophy | props | done | 1040 | 0.055 | icon trophy on a marble pedestal |
| 86 | Lobby_PottedPalm | nature | done | 1176 | 0.134 | icon palm in a terracotta pot, leaves sized to the original |
| 87 | Lobby_Bench | props | done | 564 | 0.05 | wooden bench, dark legs, gold plaque |
| 88 | Lobby_Walls | buildings | done | 896 | 0.0 | navy walls, gold caps, dark wainscot and a gold rail; corners without overlaps |
| 89 | Lobby_Floor | ground | done | 2596 | 0.03 | marble checker floor |
| 90 | Lobby_Carpet | ground | done | 200 | 0.2 | red carpets with gold edges; sunk 0.2 into the floor (DECISIONS #13) |
| 91 | Lobby_TitleSign | signs | done | 360 | 0.1 | navy board in a gold frame with bolts; text stays on the old part |
| 92 | Lobby_Window | buildings | done | 148 | 0.15 | white frame, glass, cross bars in non-overlapping pieces |
| 93 | Lobby_Spawn | ground | done | 608 | 0.123 | marble disc with a gold ring and star |
| 94 | FastTrack_Gate | decoration | done | 736 | 0.12 | gold FREE! gate with stars, plinths inside the box |
| 95 | Lux_Sofa | props | done | 612 | 0.05 | cream sofa with gold feet and pillow |
| 96 | Lux_GlassTable | props | done | 228 | 0.0 | glass top on a gold frame |
| 97 | Lux_Safe | props | done | 400 | 0.125 | gold safe with a dial and bolts |
| 98 | Lux_Piano | props | done | 344 | 0.1 | upright piano inside the original block: cabinet, keys, gold ledge and pedals |
| 99 | Lux_Chandelier | decoration | done | 600 | 0.03 | glowing ball with a gold ring, small bulbs and a drop finial |
| 100 | Dream_Pedestal | props | done | 408 | 0.083 | marble pedestal with a gold top (the dream stands at 1.8) |
| 101 | Dream_Chains | props | done | 6916 | 0.476 | reference look only, not imported: your decision (2026-10-05) is link by link (Dream_ChainSegment + Dream_Padlock, WorldSkin.chains) |
| 102 | Collection_Showcase | props | done | 488 | 0.12 | wooden table with drawers and gold knobs, gold top at 2.6 |
| 103 | AuctionRoom_Shell | buildings | done | 1752 | 0.0 | wood plank floor, dark red walls, slate ceiling |
| 104 | AuctionRoom_Stage | props | done | 336 | 0.15 | wooden stage with a glowing gold edge and stars |
| 105 | AuctionRoom_BidderDesk | props | done | 240 | 0.12 | wooden desk with a gold line; hidden gold glow shell for the top bidder |
| 106 | AuctionRoom_BidderPad | ground | done | 152 | 0.02 | wood pad with a gold rim |
| 107 | AuctionRoom_Lamp | decoration | done | 112 | 0.0 | ceiling panel with a warm glow underneath |
| 108 | AuctionRoom_TitleSign | signs | done | 360 | 0.06 | dark board in a gold frame; text stays on the old part |
| 109 | AuctionRoom_InfoBoard | signs | done | 360 | 0.06 | dark board in a gold frame; text set by the game stays on the old part |
| 110 | PodiumRoom_Shell | buildings | done | 916 | 0.0 | navy floor, dark backdrop with a glow arc |
| 111 | PodiumRoom_Block | props | done | 756 | 0.055 | gold / white / bronze blocks with stars, tops at 9, 7, 5.5 |
| 112 | PodiumRoom_LightStrip | decoration | done | 72 | 0.03 | gold glowing strip on a dark rail |
| 113 | PodiumRoom_TitleSign | signs | done | 360 | 0.06 | ink board in a gold frame; text stays on the old part |
| 114 | PodiumRoom_Board | signs | done | 216 | 0.06 | ink scoreboard in a purple frame; frame kept inside the original depth |
| 115 | Baseplate | ground | done | 76 | 0.0 | plain grass slab (it is under everything) |
| 116 | Debt_BankLoan_v2 | props | uses Debt_BankLoan |  |  |  |
| 117 | Debt_CarLoan_v2 | props | uses Debt_CarLoan |  |  |  |
| 118 | Debt_CarLoan_v3 | props | uses Debt_CarLoan |  |  |  |
| 119 | Debt_CarLoan_v4 | props | uses Debt_CarLoan |  |  |  |
| 120 | Debt_CreditCard_v2 | props | uses Debt_CreditCard |  |  |  |
| 121 | Debt_CreditCard_v3 | props | uses Debt_CreditCard |  |  |  |
| 122 | Debt_OtherDebt_v2 | props | uses Debt_OtherDebt |  |  |  |
| 123 | Debt_SchoolLoan_v2 | props | uses Debt_SchoolLoan_books7 |  |  |  |
| 124 | Debt_SchoolLoan_v3 | props | uses Debt_SchoolLoan_books4 |  |  |  |
| 125 | Lobby_PottedPalm_v2 | nature | uses Lobby_PottedPalm |  |  |  |

## Extra kit models (pieces and variants the game makes, not object types of their own)

| template | category | status | triangles | bbox dev | note |
|---|---|---|---|---|---|
| Debt_SchoolLoan_books2 | props | done | 392 |  | size step: 2 books + cap |
| Debt_SchoolLoan_books4 | props | done | 632 |  | size step: 4 books + cap |
| Debt_SchoolLoan_books5 | props | done | 752 |  | size step: 5 books + cap |
| Debt_SchoolLoan_books6 | props | done | 872 |  | size step: 6 books + cap |
| Debt_SchoolLoan_books7 | props | done | 992 |  | size step: 7 books + cap |
| Dream_ChainSegment | props | done | 144 |  | kit piece: two chunky links (3 studs) |
| Dream_Padlock | props | done | 292 |  | kit piece: icon padlock |
| Kid_v4 | props | done | 538 | 0.113 | green shirt: the 4th kid (KID_SHIRTS[4], not in the snapshot) |
| Maker_PokeBloxCard_case2 | props | done | 936 | 0.043 | RARE (blue) case: the card's value moves with the market, so the case color changes |
| Maker_PokeBloxCard_case3 | props | done | 936 | 0.043 | EPIC (purple, glowing) case |
| Maker_PokeBloxCard_case4 | props | done | 936 | 0.043 | LEGENDARY (gold, glowing) case |
| Maker_ShinyPokeBloxCard_case1 | props | done | 936 | 0.043 | COMMON (steel) case |
| Maker_ShinyPokeBloxCard_case2 | props | done | 936 | 0.043 | RARE (blue) case |
| Maker_ShinyPokeBloxCard_case4 | props | done | 936 | 0.043 | LEGENDARY (gold, glowing) case |

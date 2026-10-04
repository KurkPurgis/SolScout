# Progress

If you (or I after a restart) pick this up: read this file and STYLE_GUIDE.md first.
Updated: 2026-10-04 20:54

## Current step

Phase 3 - modelling the workplace buildings (9 job themes).

## How to continue

- Build/render/export one category: `/home/user/bvenv/bin/python tools/blender/make_models.py <category> [templates]`
- Look at `renders/objects/strips/<template>.png`, then `python3 tools/set_status.py <template> done|needs_review "note"`
- Model code: `tools/blender/models/<category>.py`; kit: `tools/blender/kit.py`, `tools/blender/parts.py`
- Blueprint of the original parts: `python3 tools/blueprint.py <template> [ctx]`

## Summary

alias: 10, built: 1, not_started: 124

## Phases

- [x] Phase 1 - inventory (world extracted, INVENTORY.md, BEFORE renders)
- [x] Phase 2 - style guide, palette, kit
- [ ] Phase 3 - model everything
- [ ] Phase 4 - whole world check (AFTER renders)
- [ ] Phase 5 - handover (REPORT.md, IMPORT_PLAN.md)

## Models (in modelling order: most visible first)

| # | template | category | status | triangles | bbox dev | note |
|---|---|---|---|---|---|---|
| 1 | Workplace_Building_PIZZERIA | buildings | built | 5324 | 0.04 |  |
| 2 | Workplace_Building_BUSDEPOT | buildings | not_started |  |  |  |
| 3 | Workplace_Building_HOSPITAL | buildings | not_started |  |  |  |
| 4 | Workplace_Building_CLINIC | buildings | not_started |  |  |  |
| 5 | Workplace_Building_SCHOOL | buildings | not_started |  |  |  |
| 6 | Workplace_Building_POLICE | buildings | not_started |  |  |  |
| 7 | Workplace_Building_OFFICE | buildings | not_started |  |  |  |
| 8 | Workplace_Building_GARAGE | buildings | not_started |  |  |  |
| 9 | Workplace_Building_FASTTRACK | buildings | not_started |  |  |  |
| 10 | Workplace_Yard_v2 | ground | not_started |  |  |  |
| 11 | Workplace_Yard | ground | not_started |  |  |  |
| 12 | Workplace_MakerLot | ground | not_started |  |  |  |
| 13 | Workplace_Fence | decoration | not_started |  |  |  |
| 14 | Workplace_LampPost | decoration | not_started |  |  |  |
| 15 | Workplace_FlowerBox | decoration | not_started |  |  |  |
| 16 | Workplace_Sandbox | props | not_started |  |  |  |
| 17 | Workplace_DebtPad | ground | not_started |  |  |  |
| 18 | Plaza_Fountain | decoration | not_started |  |  |  |
| 19 | Tree | nature | not_started |  |  |  |
| 20 | Plaza_Disc | ground | not_started |  |  |  |
| 21 | Plaza_Path | ground | not_started |  |  |  |
| 22 | City_Ground | ground | not_started |  |  |  |
| 23 | City_Wall | decoration | not_started |  |  |  |
| 24 | Dream_Supercar | vehicles | not_started |  |  |  |
| 25 | Dream_Yacht | vehicles | not_started |  |  |  |
| 26 | Dream_BeachVilla | buildings | not_started |  |  |  |
| 27 | Dream_PrivateJet | vehicles | not_started |  |  |  |
| 28 | Dream_PrivateIsland | nature | not_started |  |  |  |
| 29 | Maker_LemonadeStand | props | not_started |  |  |  |
| 30 | Maker_VendingMachine | props | not_started |  |  |  |
| 31 | Maker_Apartment | buildings | not_started |  |  |  |
| 32 | Maker_CarWash | buildings | not_started |  |  |  |
| 33 | Maker_FoodTruck | vehicles | not_started |  |  |  |
| 34 | Maker_ToyShop | buildings | not_started |  |  |  |
| 35 | Maker_MiniGolf | props | not_started |  |  |  |
| 36 | Maker_HouseToRent | buildings | not_started |  |  |  |
| 37 | Maker_PizzaRestaurant | buildings | not_started |  |  |  |
| 38 | Maker_CoffeeShop | buildings | not_started |  |  |  |
| 39 | Maker_BowlingAlley | buildings | not_started |  |  |  |
| 40 | Maker_Hotel | buildings | not_started |  |  |  |
| 41 | Maker_GameStudio | buildings | not_started |  |  |  |
| 42 | Maker_ShoppingMall | buildings | not_started |  |  |  |
| 43 | Maker_ApartmentBuilding | buildings | not_started |  |  |  |
| 44 | Maker_ThemePark | props | not_started |  |  |  |
| 45 | Maker_PokeBloxCard | props | not_started |  |  |  |
| 46 | Maker_RarePokeBloxCard | props | not_started |  |  |  |
| 47 | Maker_RarePokeBloxCard_v2 | props | not_started |  |  |  |
| 48 | Maker_RarePokeBloxCard_v3 | props | not_started |  |  |  |
| 49 | Maker_RarePokeBloxCard_v4 | props | not_started |  |  |  |
| 50 | Maker_ShinyPokeBloxCard | props | not_started |  |  |  |
| 51 | Maker_GoldCoin | props | not_started |  |  |  |
| 52 | Maker_GoldBar | props | not_started |  |  |  |
| 53 | Maker_GoldTreasureChest | props | not_started |  |  |  |
| 54 | Maker_UnknownMaker | props | not_started |  |  |  |
| 55 | Kid | props | not_started |  |  |  |
| 56 | Kid_v2 | props | not_started |  |  |  |
| 57 | Kid_v3 | props | not_started |  |  |  |
| 58 | Debt_CreditCard | props | not_started |  |  |  |
| 59 | Debt_CarLoan | props | not_started |  |  |  |
| 60 | Debt_SchoolLoan | props | not_started |  |  |  |
| 61 | Debt_BankLoan | props | not_started |  |  |  |
| 62 | Debt_OtherDebt | props | not_started |  |  |  |
| 63 | Depot_Bus | vehicles | not_started |  |  |  |
| 64 | Police_Car | vehicles | not_started |  |  |  |
| 65 | Garage_CarLift | vehicles | not_started |  |  |  |
| 66 | Computer | props | not_started |  |  |  |
| 67 | HospitalBed | props | not_started |  |  |  |
| 68 | Pizzeria_Counter | props | not_started |  |  |  |
| 69 | Pizzeria_Oven | props | not_started |  |  |  |
| 70 | School_Blackboard | decoration | not_started |  |  |  |
| 71 | School_TeacherDesk | props | not_started |  |  |  |
| 72 | School_StudentDesk | props | not_started |  |  |  |
| 73 | Clinic_Chair | props | not_started |  |  |  |
| 74 | Clinic_Cabinet | props | not_started |  |  |  |
| 75 | Clinic_WallScreen | decoration | not_started |  |  |  |
| 76 | Hospital_WallCross | decoration | not_started |  |  |  |
| 77 | Office_Screen | decoration | not_started |  |  |  |
| 78 | Garage_ToolBoard | decoration | not_started |  |  |  |
| 79 | Garage_TireStack | props | not_started |  |  |  |
| 80 | Lobby_RoomBooth | buildings | not_started |  |  |  |
| 81 | Lobby_RoomBooth_v2 | buildings | not_started |  |  |  |
| 82 | Lobby_RoomBooth_v3 | buildings | not_started |  |  |  |
| 83 | Lobby_RoomBooth_v4 | buildings | not_started |  |  |  |
| 84 | Lobby_Pillar | decoration | not_started |  |  |  |
| 85 | Lobby_Trophy | props | not_started |  |  |  |
| 86 | Lobby_PottedPalm | nature | not_started |  |  |  |
| 87 | Lobby_Bench | props | not_started |  |  |  |
| 88 | Lobby_Walls | buildings | not_started |  |  |  |
| 89 | Lobby_Floor | ground | not_started |  |  |  |
| 90 | Lobby_Carpet | ground | not_started |  |  |  |
| 91 | Lobby_TitleSign | signs | not_started |  |  |  |
| 92 | Lobby_Window | buildings | not_started |  |  |  |
| 93 | Lobby_Spawn | ground | not_started |  |  |  |
| 94 | FastTrack_Gate | decoration | not_started |  |  |  |
| 95 | Lux_Sofa | props | not_started |  |  |  |
| 96 | Lux_GlassTable | props | not_started |  |  |  |
| 97 | Lux_Safe | props | not_started |  |  |  |
| 98 | Lux_Piano | props | not_started |  |  |  |
| 99 | Lux_Chandelier | decoration | not_started |  |  |  |
| 100 | Dream_Pedestal | props | not_started |  |  |  |
| 101 | Dream_Chains | props | not_started |  |  |  |
| 102 | Collection_Showcase | props | not_started |  |  |  |
| 103 | AuctionRoom_Shell | buildings | not_started |  |  |  |
| 104 | AuctionRoom_Stage | props | not_started |  |  |  |
| 105 | AuctionRoom_BidderDesk | props | not_started |  |  |  |
| 106 | AuctionRoom_BidderPad | ground | not_started |  |  |  |
| 107 | AuctionRoom_Lamp | decoration | not_started |  |  |  |
| 108 | AuctionRoom_TitleSign | signs | not_started |  |  |  |
| 109 | AuctionRoom_InfoBoard | signs | not_started |  |  |  |
| 110 | PodiumRoom_Shell | buildings | not_started |  |  |  |
| 111 | PodiumRoom_Block | props | not_started |  |  |  |
| 112 | PodiumRoom_LightStrip | decoration | not_started |  |  |  |
| 113 | PodiumRoom_TitleSign | signs | not_started |  |  |  |
| 114 | PodiumRoom_Board | signs | not_started |  |  |  |
| 115 | Baseplate | ground | not_started |  |  |  |
| 116 | Debt_BankLoan_v2 | props | uses Debt_BankLoan |  |  |  |
| 117 | Debt_CarLoan_v2 | props | uses Debt_CarLoan |  |  |  |
| 118 | Debt_CarLoan_v3 | props | uses Debt_CarLoan |  |  |  |
| 119 | Debt_CarLoan_v4 | props | uses Debt_CarLoan |  |  |  |
| 120 | Debt_CreditCard_v2 | props | uses Debt_CreditCard |  |  |  |
| 121 | Debt_CreditCard_v3 | props | uses Debt_CreditCard |  |  |  |
| 122 | Debt_OtherDebt_v2 | props | uses Debt_OtherDebt |  |  |  |
| 123 | Debt_SchoolLoan_v2 | props | uses Debt_SchoolLoan |  |  |  |
| 124 | Debt_SchoolLoan_v3 | props | uses Debt_SchoolLoan |  |  |  |
| 125 | Lobby_PottedPalm_v2 | nature | uses Lobby_PottedPalm |  |  |  |

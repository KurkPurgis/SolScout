# Progress

If you (or I after a restart) pick this up: read this file and STYLE_GUIDE.md first.
Updated: 2026-10-04 21:42

## Current step

Phase 3 - reviewing built models and fixing (bbox, z-fighting, mirrored details); new models for lobby/rooms/signs in the build queue; then a full rebuild with the final kit. Phase 4 assembly script (tools/blender/build_after.py) and fixed lineup cameras are written.

## How to continue

- Build/render/export one category: `/home/user/bvenv/bin/python tools/blender/make_models.py <category> [templates]`
- Look at `renders/objects/strips/<template>.jpg`, then `python3 tools/set_status.py <template> done|needs_review "note"`
- Model code: `tools/blender/models/<category>.py`; kit: `tools/blender/kit.py`, `tools/blender/parts.py`
- Blueprint of the original parts: `python3 tools/blueprint.py <template> [ctx]`

## Summary

alias: 10, built: 79, not_started: 46

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
| 2 | Workplace_Building_BUSDEPOT | buildings | built | 5180 | 0.04 |  |
| 3 | Workplace_Building_HOSPITAL | buildings | built | 5340 | 0.04 |  |
| 4 | Workplace_Building_CLINIC | buildings | built | 5180 | 0.04 |  |
| 5 | Workplace_Building_SCHOOL | buildings | built | 5252 | 0.04 |  |
| 6 | Workplace_Building_POLICE | buildings | built | 5272 | 0.04 |  |
| 7 | Workplace_Building_OFFICE | buildings | built | 5180 | 0.04 |  |
| 8 | Workplace_Building_GARAGE | buildings | built | 5180 | 0.04 |  |
| 9 | Workplace_Building_FASTTRACK | buildings | built | 5348 | 0.04 |  |
| 10 | Workplace_Yard_v2 | ground | built | 716 | 0.0 |  |
| 11 | Workplace_Yard | ground | built | 256 | 0.0 |  |
| 12 | Workplace_MakerLot | ground | built | 260 | 0.15 |  |
| 13 | Workplace_Fence | decoration | built | 912 | 0.073 |  |
| 14 | Workplace_LampPost | decoration | built | 576 | 0.03 |  |
| 15 | Workplace_FlowerBox | decoration | built | 1400 | 0.06 |  |
| 16 | Workplace_Sandbox | props | built | 736 | 0.15 |  |
| 17 | Workplace_DebtPad | ground | built | 152 | 0.1 |  |
| 18 | Plaza_Fountain | decoration | built | 2944 | 0.0 |  |
| 19 | Tree | nature | built | 1064 | 0.05 |  |
| 20 | Plaza_Disc | ground | built | 3000 | 0.0 |  |
| 21 | Plaza_Path | ground | built | 684 | 0.0 |  |
| 22 | City_Ground | ground | built | 76 | 0.0 |  |
| 23 | City_Wall | decoration | built | 2016 | 0.1 |  |
| 24 | Dream_Supercar | vehicles | built | 3896 | 0.125 |  |
| 25 | Dream_Yacht | vehicles | built | 3856 | 0.15 |  |
| 26 | Dream_BeachVilla | buildings | built | 5528 | 0.218 |  |
| 27 | Dream_PrivateJet | vehicles | built | 3600 | 0.3 |  |
| 28 | Dream_PrivateIsland | nature | built | 5608 | 0.15 |  |
| 29 | Maker_LemonadeStand | props | built | 1340 | 0.023 |  |
| 30 | Maker_VendingMachine | props | built | 720 | 0.08 |  |
| 31 | Maker_Apartment | buildings | built | 860 | 0.3 |  |
| 32 | Maker_CarWash | buildings | built | 1132 | 0.25 |  |
| 33 | Maker_FoodTruck | vehicles | built | 2280 | 0.63 |  |
| 34 | Maker_ToyShop | buildings | built | 1308 | 0.027 |  |
| 35 | Maker_MiniGolf | props | built | 952 | 0.0 |  |
| 36 | Maker_HouseToRent | buildings | built | 1492 | 0.5 |  |
| 37 | Maker_PizzaRestaurant | buildings | built | 1268 | 0.027 |  |
| 38 | Maker_CoffeeShop | buildings | built | 1280 | 0.05 |  |
| 39 | Maker_BowlingAlley | buildings | built | 1516 | 0.027 |  |
| 40 | Maker_Hotel | buildings | built | 2124 | 0.05 |  |
| 41 | Maker_GameStudio | buildings | built | 1380 | 0.027 |  |
| 42 | Maker_ShoppingMall | buildings | built | 1228 | 0.027 |  |
| 43 | Maker_ApartmentBuilding | buildings | built | 1712 | 0.05 |  |
| 44 | Maker_ThemePark | props | built | 1136 | 0.08 |  |
| 45 | Maker_PokeBloxCard | props | built | 936 | 0.043 |  |
| 46 | Maker_RarePokeBloxCard | props | built | 936 | 0.043 |  |
| 47 | Maker_RarePokeBloxCard_v2 | props | built | 936 | 0.043 |  |
| 48 | Maker_RarePokeBloxCard_v3 | props | built | 936 | 0.043 |  |
| 49 | Maker_RarePokeBloxCard_v4 | props | built | 936 | 0.043 |  |
| 50 | Maker_ShinyPokeBloxCard | props | built | 936 | 0.043 |  |
| 51 | Maker_GoldCoin | props | built | 884 | 0.0 |  |
| 52 | Maker_GoldBar | props | built | 648 | 0.029 |  |
| 53 | Maker_GoldTreasureChest | props | built | 856 | 0.077 |  |
| 54 | Maker_UnknownMaker | props | built | 752 | 0.19 |  |
| 55 | Kid | props | built | 538 | 0.113 |  |
| 56 | Kid_v2 | props | built | 538 | 0.113 |  |
| 57 | Kid_v3 | props | built | 538 | 0.113 |  |
| 58 | Debt_CreditCard | props | built | 320 | 0.015 |  |
| 59 | Debt_CarLoan | props | built | 1052 | 0.06 |  |
| 60 | Debt_SchoolLoan | props | built | 512 | 0.042 |  |
| 61 | Debt_BankLoan | props | built | 384 | 0.017 |  |
| 62 | Debt_OtherDebt | props | built | 336 | 0.12 |  |
| 63 | Depot_Bus | vehicles | built | 2832 | 0.29 |  |
| 64 | Police_Car | vehicles | built | 1700 | 0.17 |  |
| 65 | Garage_CarLift | vehicles | built | 1744 | 0.06 |  |
| 66 | Computer | props | built | 468 | 0.0 |  |
| 67 | HospitalBed | props | built | 496 | 0.025 |  |
| 68 | Pizzeria_Counter | props | built | 516 | 0.16 |  |
| 69 | Pizzeria_Oven | props | built | 462 | 0.1 |  |
| 70 | School_Blackboard | decoration | built | 256 | 0.45 |  |
| 71 | School_TeacherDesk | props | built | 264 | 0.13 |  |
| 72 | School_StudentDesk | props | built | 264 | 0.13 |  |
| 73 | Clinic_Chair | props | built | 272 | 0.05 |  |
| 74 | Clinic_Cabinet | props | built | 288 | 0.0 |  |
| 75 | Clinic_WallScreen | decoration | built | 184 | 0.275 |  |
| 76 | Hospital_WallCross | decoration | built | 332 | 0.0 |  |
| 77 | Office_Screen | decoration | built | 232 | 0.37 |  |
| 78 | Garage_ToolBoard | decoration | built | 372 | 0.375 |  |
| 79 | Garage_TireStack | props | built | 1052 | 0.05 |  |
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

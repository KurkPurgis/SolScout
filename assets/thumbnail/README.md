# Rags to Riches – game thumbnail

| File | What it is |
|---|---|
| `thumbnail_1920x1080.png` | Main thumbnail, no text |
| `thumbnail_text.png` | Same image with "CAN YOU ESCAPE?" top left |
| `icon_512x512.png` | Square icon: the chained yacht and padlock, the player's head in the corner |
| `thumbnail.blend` | The scene, every model and texture packed (Blender 5.2) |
| `check_256x144.png`, `check_text_256x144.png`, `check_icon.png` | Readability checks: full size next to the small size |
| `blockout/` | Step 1 composition blockouts (boxes only) |
| `thumbnail/` | The player's avatar as exported from Roblox Studio (`avatar.obj`, `.mtl`, textures) |
| `scripts/` | Everything that builds and renders the images |

## What is in the picture

Real game models from `world_overhaul/blend/` (branch `claude/rags-to-riches-visual-overhaul-dey2rr`):
- **The dream:** `Yacht`, `Dream_ChainSegment` (tiled link by link around the hull, as the game's
  `WorldSkin.chains` does) and `Dream_Padlock`.
- **Props:** `Maker_GoldCoin` (the falling coins, without its display stand) and `Debt_CreditCard`.
- **The city:** `Workplace_Building_PIZZERIA`, `Tree`, `Workplace_LampPost`, `Plaza_Disc`,
  `Plaza_Fountain`, `City_Ground` and three Money Maker shops.
- **Background dreams:** `Supercar` and `PrivateJet`.

All of them use the game's one palette material.

Built here, because the game has no such model, with the game's own model kit
(`world_overhaul/tools/blender/kit.py`) and palette so they match:
- the cash stacks (palette GREEN bundles with a CREAM band)
- the price tag (GOLD)
- the iron ball and ankle cuff
- the clouds

The ball's chain is the real `Dream_ChainSegment`, scaled down.

The player is the real avatar from `thumbnail/avatar.obj` (R15). The script rigs it with joints found
from the mesh: shoulders, elbows, wrists, waist, neck, hips, knees and ankles. It then poses the
avatar by rotating those joints, with two-bone IK for both arms.

The numbers and the title use **Fredoka Bold** (`scripts/fonts`, SIL Open Font License). The game's
title font is FredokaOne; Fredoka is its current version. The static Bold instance was cut from the
Google Fonts variable font with fontTools.

## Rebuild

```sh
pip install bpy==5.2.* numpy scipy pillow
mkdir -p /tmp/wo && git archive origin/claude/rags-to-riches-visual-overhaul-dey2rr world_overhaul | tar -x -C /tmp/wo
cd assets/thumbnail/scripts
python build_thumbnail.py --wo /tmp/wo/world_overhaul --out /tmp/passes      # scene + EXR passes
python finish.py --passes /tmp/passes --out ..                               # main + text version
python finish.py --passes /tmp/passes --out .. --prefix icon --name icon_512x512.png --text-name "" --size 512x512
python check_small.py ../thumbnail_1920x1080.png ../check_256x144.png
python check_small.py ../thumbnail_text.png ../check_text_256x144.png
python check_small.py --icon ../icon_512x512.png ../check_icon.png
```

Add `--quick` to `build_thumbnail.py` for a 960x540 preview in about 30 seconds.

`layout.py` holds every position:
- the camera, including its 6° roll
- the avatar's pose angles
- the number sizes, given as cap height (a fraction of the frame height)
- the yacht, chains, tag and coins
- the middle ground

`finish.py` does the 2D finishing on the linear passes:
- bloom from the glow
- a soft highlight roll-off
- a contrast and saturation grade
- the INK outline (palette colour `#281A3A`, the icon outline colour) around the character, the
  dream and the debt number, kept off anything in front of them using the depth pass
- the blurred near coins
- the title

"""
write_report.py - writes REPORT.md from the data (run it again after any change).

    python3 tools/write_report.py

Needs: data/model_status.json, data/templates.json, data/script_refs.json, data/plan.json,
renders/compare/*.jpg (tools/compare.py) and renders/contact_sheet_*.jpg (tools/contact_sheet.py --all).
The fixed text (decisions for you, what could not be done) is in this file.
"""

import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def load(*p):
    return json.load(open(os.path.join(ROOT, *p)))


WORLD_SHOTS = [
    ("overview_city", "City 1 from above, in the middle of a game (8 players, one per job)"),
    ("city_plot_watchcam", "A workplace through the game's own camera"),
    ("city_player_eye", "What a player sees, standing on the plaza"),
    ("lobby", "The lobby"),
    ("auction_room", "The auction room"),
    ("podium_room", "The podium room"),
    ("overview_world", "The whole world (lobby + 4 cities)"),
]

# the owner's answers (2026-10-05); questions without an answer stay open
ANSWERS = {
    1: "No outline. Nothing to build; the comparison render stays as a record.",
    2: "Link by link. `WorldSkin.chains` (called at the end of `addChains`) tiles the `Dream_ChainSegment` "
       "piece along every chain bar the game makes and puts `Dream_Padlock` on the padlock; the one-piece "
       "`Dream_Chains` model is not imported (IMPORT_PLAN step 6).",
    3: "Keep the warm glow. No change.",
    5: "Close enough. The listed exceptions stay as they are.",
}

QUESTIONS = [
    "**Outline or no outline?** The world has no outline (the icons have one). One building with and without an "
    "outline is in `renders/outline_comparison.png`. An outline doubles the triangles of every model and Roblox has "
    "no cheap way to draw it, so I recommend: no outline.",
    "**Chains on the locked dream.** The game builds them link by link in code. I made one finished chain model "
    "AND two kit pieces (one link, the padlock) - see DECISIONS #15. Which one do you want to use?",
    "**Lit windows.** Workplace and Money Maker windows that were Neon in the game are still Neon (warm yellow). "
    "In bright daylight they look almost white. Keep them glowing, or switch them to the shiny blue WINDOW color "
    "(the icon look)?",
    "**FOR SALE copies.** The game makes every part of a FOR SALE Money Maker see-through ForceField. The new meshes "
    "will get the same treatment automatically (they are BaseParts inside the same Model). Check in Studio that "
    "the ForceField look on a textured mesh is what you want (it shows the texture's colors, not one flat color).",
    "**Bounding boxes.** Every new mesh stays within 0.15 studs of the original box, except: %(bbox_exceptions)s. "
    "The game measures some models with `GetBoundingBox` (Money Maker stacking, labels, tutorial arrow), so a "
    "0.1 stud difference can move a label by 0.1 stud. Is that close enough, or do you want those exact?",
    "**Text.** All words stay on the old parts (now invisible), so prices and names still update. The new sign "
    "boards were made to sit right behind that text. Please look at one sign in Studio to check the text is not "
    "hidden or floating.",
    "**Texture size.** The whole world uses ONE 256 x 128 palette texture (32 flat color swatches; every face "
    "samples the middle of one swatch). If the colors bleed into each other on low-end phones, use the same "
    "image scaled 4x with nearest-neighbour (1024 x 512): the UVs stay the same. Keep it small, or go 4x?",
]

NOT_DONE = [
    "**No Blender window and no Blender MCP connection** were available in this cloud session, and Blender "
    "downloads were blocked. I used Blender 5.0.1 as a Python module (same engine, no window) and drove everything "
    "with scripts (`tools/blender/`). You can open every `.blend` in normal Blender.",
    "**No place file with the world in it.** The world is made by the game's Luau code while it runs, so I ran "
    "that code on a small copy of the Roblox engine to get every part (DECISIONS #2-#3). Things that only exist "
    "during a game (workplaces, Money Makers, debts, dreams) come from a mid-game snapshot I set up.",
    "**Nothing was tested inside Roblox Studio** (no Studio here, and I was not allowed to upload). Renders are "
    "from Blender with lighting similar to the game; Studio's Future lighting will look a bit different.",
    "**Words on signs** are drawn in the renders as simple 3D text so the pictures make sense; in the game the "
    "real SurfaceGui text stays on the old parts.",
    "**Particle effects, sounds, UI and the players' avatars** are not part of this overhaul. The ball and chain "
    "on a player's leg (`DebtChain.luau`) is a physics object attached to the character during a match; it is "
    "not part of the world and was left as it is.",
    "**The swap itself was not run** (not allowed tonight). What I could check without Studio: the generated "
    "`WorldSkin` modules compile with the Luau compiler, and the placement lists reproduce all 35 places the game "
    "builds exactly (`tools/verify_placements.py`).",
]


def table_rows(status, templates, refs, plan):
    aliases = plan["aliases"]
    rows = []
    order = plan["order"]
    for i, name in enumerate(order, 1):
        t = templates.get(name, {})
        e = status.get(name)
        alias = aliases.get(name)
        if e is None and alias:
            st = "uses %s" % alias
            tris = status.get(alias, {}).get("triangles", "")
            fbx = status.get(alias, {}).get("fbx", "")
        elif e is None:
            st, tris, fbx = "not modelled", "", ""
        else:
            st = {"done": "done", "needs_review": "**NEEDS REVIEW**", "built": "built (not reviewed)"}.get(
                e.get("status"), e.get("status"))
            tris = "%s / %s" % (e.get("triangles", ""), e.get("budget", ""))
            fbx = e.get("fbx", "")
        sref = "yes" if name in refs["script_referenced"] else ""
        count = t.get("instances", "")
        fbx_link = "[fbx](%s)" % fbx.replace(" ", "%20") if fbx else ""
        rows.append("| %d | %s | %s | %s | %s | %s | %s | %s |" % (
            i, name, t.get("category", ""), count, st, tris, sref, fbx_link))
    return rows


def main():
    status = load("data", "model_status.json")
    templates = load("data", "templates.json")
    refs = load("data", "script_refs.json")
    plan = load("data", "plan.json")
    decisions = open(os.path.join(ROOT, "DECISIONS.md")).read()
    n_decisions = sum(1 for line in decisions.splitlines() if line.startswith("| ") and line[2:3].isdigit())

    built = [n for n, e in status.items() if e.get("fbx")]
    done = [n for n, e in status.items() if e.get("status") == "done"]
    review = [n for n, e in status.items() if e.get("status") == "needs_review"]
    total_tris = sum(e.get("triangles", 0) for e in status.values())
    lines = []
    w = lines.append
    w("# Rags to Riches - new look for the whole world (report)")
    w("")
    w("Written %s. Start here; everything else is linked from this page." % time.strftime("%Y-%m-%d %H:%M"))
    w("")
    w("## In short")
    w("")
    w("- I rebuilt **every visible object** of the world in the style of the 3D icons: chunky, rounded, bright, "
      "one palette, the same bevels and parts everywhere.")
    own = sum(1 for n in plan["order"] if n in status and status[n].get("fbx"))
    copies = sum(1 for n in plan["order"] if n not in status and n in plan["aliases"])
    w("- All **%d object types** are covered: %d have their own model and %d are size or color copies that reuse "
      "one. With %d extra pieces (book-stack sizes, chain link, padlock) that is **%d FBX models**; %d are "
      "reviewed and done%s." % (own + copies, own, copies, len(built) - own, len(built), len(done),
                                (", %d need your review (listed below)" % len(review)) if review else
                                ", none is left waiting for review"))
    w("- Counted once each, the models have %d triangles together; the biggest single model has %d (Roblox "
      "allows 20,000 per mesh)." % (total_tris, max(e.get("triangles", 0) for e in status.values())))
    w("- **Nothing in the game was changed.** Every new model has the same name, position and rotation as the "
      "original object and the same size (within 0.15 studs, exceptions in question 5), so swapping it in is "
      "mechanical (`IMPORT_PLAN.md`, not executed).")
    w("- The whole world uses **one small texture** (`palette/palette_color.png`, 32 colors). See `STYLE_GUIDE.md`.")
    w("- %d decisions I took on my own are in `DECISIONS.md` (one line of reasoning each); the ones I need you "
      "for are below." % n_decisions)
    w("")
    w("## Before and after (same cameras)")
    w("")
    for name, caption in WORLD_SHOTS:
        path = "renders/compare/%s.jpg" % name
        if os.path.exists(os.path.join(ROOT, path)):
            w("**%s**" % caption)
            w("")
            w("![%s](%s)" % (name, path))
            w("")
    lineups = sorted(glob.glob(os.path.join(ROOT, "renders", "compare", "lineup_*.jpg")))
    if lineups:
        w("### Every object type, category by category (before | after)")
        w("")
        for p in lineups:
            rel = os.path.relpath(p, ROOT)
            w("- [%s](%s)" % (os.path.splitext(os.path.basename(p))[0].replace("lineup_", ""), rel))
        w("")
    sheets = sorted(glob.glob(os.path.join(ROOT, "renders", "contact_sheet_*.jpg")))
    if sheets:
        w("## All models at a glance (contact sheet)")
        w("")
        for p in sheets:
            rel = os.path.relpath(p, ROOT)
            w("![contact sheet](%s)" % rel)
            w("")
        w("Each model also has 3 renders (front 3/4, back 3/4, eye level with a 5-stud player) in "
          "`renders/objects/<name>/`.")
        w("")
    w("## Your decisions")
    w("")
    w("Answered on 2026-10-05 (recorded in `DECISIONS.md`); the ones without an answer are still open.")
    w("")
    why = {"Dream_BeachVilla": "0.22 shallower at the front", "Dream_Chains": "chunky links, up to 0.48 out",
           "Lobby_Carpet": "0.2 deeper, hidden in the floor"}
    exc = ["`%s` (%s)" % (n, why.get(n, "wall board, details stand up to %.2f out from the wall" % e["bbox_max_dev"]))
           for n, e in sorted(status.items()) if (e.get("bbox_max_dev") or 0) > 0.15]
    for i, q in enumerate(QUESTIONS, 1):
        text = q % {"bbox_exceptions": ", ".join(exc) or "none"} if "%(" in q else q
        if i in ANSWERS:
            w("%d. ~~%s~~  \n   **Your answer: %s**" % (i, text.split("**")[1] if "**" in text else text, ANSWERS[i]))
        else:
            w("%d. **Still open.** %s" % (i, text))
    if review:
        w("%d. **Models marked NEEDS REVIEW:** %s." % (len(QUESTIONS) + 1, ", ".join(
            "%s (%s)" % (n, "; ".join(status[n].get("notes", [])[-1:])) for n in sorted(review))))
    w("")
    w("## What I could not do")
    w("")
    for item in NOT_DONE:
        w("- " + item)
    w("")
    w("## Every object type")
    w("")
    w("`template` = one model (variants in color or size count separately, see INVENTORY.md). "
      "*Script-referenced* = some game script finds it by name, measures it or changes it; those keep the "
      "original names and boxes exactly, see `data/script_refs.json` for the evidence.")
    w("")
    w("| # | template | category | copies | status | triangles / budget | script-referenced | file |")
    w("|---|---|---|---|---|---|---|---|")
    lines.extend(table_rows(status, templates, refs, plan))
    extra = sorted(n for n in status if n not in plan["order"])
    if extra:
        w("")
        w("Extra meshes (kit pieces and size steps the game builds in code): " + ", ".join(
            "`%s` (%s tris)" % (n, status[n].get("triangles")) for n in extra) + ".")
    w("")
    w("## Where things are")
    w("")
    w("| what | where |")
    w("|---|---|")
    w("| style rules, palette, kit, budgets, Roblox settings | `STYLE_GUIDE.md` |")
    w("| list of every object in the world | `INVENTORY.md`, `data/objects.csv` |")
    w("| how to swap the new models in (not executed) | `IMPORT_PLAN.md` |")
    w("| my decisions | `DECISIONS.md` |")
    w("| progress log | `PROGRESS.md` |")
    w("| FBX files | `export/<category>/<name>.fbx` |")
    w("| Blender files (one per category, plus before/after scenes) | `blend/` |")
    w("| renders | `renders/before`, `renders/after`, `renders/compare`, `renders/objects` |")
    w("| all scripts (re-run everything) | `tools/` |")
    w("")
    open(os.path.join(ROOT, "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print("REPORT.md written:", len(lines), "lines")


if __name__ == "__main__":
    main()

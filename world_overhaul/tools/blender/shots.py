"""
shots.py - the fixed cameras used for BEFORE and AFTER images (same cameras = fair comparison),
the 5-stud player dummies, and the category lineups.

All positions are Blender coordinates (Roblox X, -Z, Y). City 1 is centered at x = 700.
"""

import json
import math
import os

import bpy
from mathutils import Vector

import wo

CITY = 700.0  # city 1 center (Roblox x = 700, z = 0)


def plot_base(index):
    """Blender position of workplace number `index` (1..8) in city 1, and the direction it faces."""
    a = (index - 1) / 8 * 2 * math.pi
    rx, rz = 115 * math.sin(a), 115 * math.cos(a)
    return Vector((CITY + rx, -rz, 1.0))


# name, location, facing (radians around Z)
DUMMIES = [
    ("PlayerDummy_Lobby", (4.0, -34.0, 1.0), math.radians(180)),
    ("PlayerDummy_Plaza", (CITY + 14.0, 8.0, 0.4), math.radians(160)),
    ("PlayerDummy_Plot5", (CITY + 4.0, 98.0, 1.0), math.radians(0)),
    ("PlayerDummy_Auction", (CITY - 3.25, -8.0, 400.4), math.radians(0)),
    ("PlayerDummy_Podium", (CITY, 8.0, 259.0), math.radians(180)),
]

# name: (location, target, lens, width, height)
WORLD_SHOTS = {
    "overview_world": ((1450, -3100, 1750), (1450, 150, 60), 35, 1920, 1080),
    "overview_city": ((CITY, -150, 150), (CITY, 95, 0), 26, 1920, 1080),
    "city_plot_watchcam": ((CITY, 57, 29), (CITY, 117, 7), 35, 1600, 900),  # the game's own turn camera
    "city_player_eye": ((CITY + 9, 30, 4.6), (CITY - 2, 112, 7.5), 30, 1600, 900),
    "lobby": ((0, -47, 19), (0, 20, 6), 22, 1600, 900),
    "auction_room": ((CITY, -23, 413), (CITY, 12, 406), 30, 1600, 900),
    "podium_room": ((CITY, -32, 264), (CITY, 8, 258), 30, 1600, 900),
}


# Closed rooms get a soft ceiling fill that stands in for the game's Lighting.Ambient (0.16, 0.16, 0.18),
# which Blender does not have. Same light for BEFORE and AFTER. name: (center, size, watts)
FILLS = {
    "auction_room": ((CITY, 0.0, 423.0), (60.0, 46.0), 2000.0),
}


def _fill(name):
    spec = FILLS.get(name)
    if spec is None:
        return None
    obj = bpy.data.objects.get("Fill_" + name)
    if obj is None:
        data = bpy.data.lights.new("Fill_" + name, "AREA")
        data.shape = "RECTANGLE"
        obj = bpy.data.objects.new("Fill_" + name, data)
        bpy.context.scene.collection.objects.link(obj)
    (x, y, z), (sx, sy), watts = spec
    obj.location = (x, y, z)
    obj.rotation_euler = (0, 0, 0)  # an area light shines down (-Z)
    obj.data.size, obj.data.size_y, obj.data.energy = sx, sy, watts
    obj.data.color = (1.0, 0.97, 0.92)
    return obj


def make_cameras():
    for name, (loc, target, lens, _, _) in WORLD_SHOTS.items():
        wo.camera("CAM_" + name, loc, target, lens=lens)


def set_visible(name, visible):
    col = bpy.data.collections.get(name)
    if col is None:
        return
    col.hide_render = not visible
    col.hide_viewport = not visible


def render_world_shots(out_dir, names=None, samples=48):
    set_visible("Catalog", False)
    set_visible("Lineup", False)
    set_visible("World", True)
    scene = bpy.context.scene
    scene.cycles.samples = samples
    for name, (loc, target, lens, w, h) in WORLD_SHOTS.items():
        if names and name not in names:
            continue
        scene.render.resolution_x, scene.render.resolution_y = w, h
        cam = bpy.data.objects.get("CAM_" + name) or wo.camera("CAM_" + name, loc, target, lens=lens)
        fill = _fill(name)
        wo.render(os.path.join(out_dir, name + ".png"), cam)
        if fill is not None:
            fill.hide_render = True
            bpy.data.objects.remove(fill, do_unlink=True)
        print("rendered", name)


# ----------------------------------------------------------------------------
# Category lineups: every template of a category in a row, at true scale, with its name.
# ----------------------------------------------------------------------------

LINEUP_ORIGIN = Vector((0, 8000, 0))
SKIP_IN_LINEUP = {"Baseplate", "City_Ground", "City_Wall", "Lobby_Walls", "Lobby_Floor", "Lobby_Carpet",
                  "Plaza_Disc", "AuctionRoom_Shell", "PodiumRoom_Shell"}


def lineup_templates(templates):
    """category -> list of pages; each page is a list of template names (biggest first)."""
    pages = {}
    by_cat = {}
    for name, t in templates.items():
        if t["type"] in SKIP_IN_LINEUP:
            continue
        # one look per type is enough in the lineup (variants are colors/sizes of the same model),
        # except the workplace buildings, which differ per job
        if "_v" in name.split("_")[-1] or (name != t["type"] and not name.startswith("Workplace_Building")):
            continue
        by_cat.setdefault(t["category"], []).append(name)
    for cat, names in by_cat.items():
        names.sort(key=lambda n: (max(templates[n]["size"][0], templates[n]["size"][2]), n))
        chunks = []
        big = [n for n in names if max(templates[n]["size"]) > 30]
        small = [n for n in names if max(templates[n]["size"]) <= 30]
        for group in (big, small):
            for i in range(0, len(group), 12):
                chunks.append(group[i:i + 12])
        pages[cat] = [c for c in chunks if c]
    return pages


def lineup_layout(templates, names):
    """Positions (Blender) for a page: rows of up to 4, true scale, 3 studs apart."""
    per_row = 4 if len(names) > 6 else max(1, len(names))
    rows = [names[i:i + per_row] for i in range(0, len(names), per_row)]
    placed = []
    y = 0.0
    for row in rows:
        widths = [templates[n]["size"][0] for n in row]
        depths = [templates[n]["size"][2] for n in row]
        gap = max(3.0, 0.15 * max(widths))
        total = sum(widths) + gap * (len(row) - 1)
        x = -total / 2
        for n, w in zip(row, widths):
            t = templates[n]
            # the object's frame origin is not always its bbox center: shift so the bbox is centered
            cx = (t["bbox_min"][0] + t["bbox_max"][0]) / 2
            cz = (t["bbox_min"][2] + t["bbox_max"][2]) / 2  # Roblox local Z (front is -Z)
            pos = LINEUP_ORIGIN + Vector((x + w / 2 - cx, y + cz, -t["bbox_min"][1]))
            placed.append((n, pos))
            x += w + gap
        heights = [templates[n]["size"][1] for n in row]
        # the next row stands behind (front = +Y), far enough that its name labels are not hidden
        y -= max(depths) + 3.0 + 1.1 * max(heights)
    return placed


def fit_camera(name, pts, direction, lens=40.0, aspect=16 / 9, margin=1.06):
    """A camera looking along -direction at the middle of `pts`, as close as possible with every point inside
    the frame (horizontal sensor fit, 36 mm)."""
    xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
    center = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    direction = direction.normalized()
    tan_x = 18.0 / lens
    tan_y = tan_x / aspect
    forward = -direction
    right = forward.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(forward).normalized()

    def fits(d):
        eye = center + direction * d
        for p in pts:
            v = p - eye
            z = v.dot(forward)
            if z <= 0.1:
                return False
            if abs(v.dot(right)) / z > tan_x / margin or abs(v.dot(up)) / z > tan_y / margin:
                return False
        return True

    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))

    def fit_distance():
        lo_d, hi_d = 0.5, span * 20 + 50
        for _ in range(50):
            mid = (lo_d + hi_d) / 2
            if fits(mid):
                hi_d = mid
            else:
                lo_d = mid
        return hi_d

    # perspective: the middle of the box is not the middle of the picture -> shift the aim a few times
    for _ in range(4):
        d = fit_distance()
        eye = center + direction * d
        us = [(p - eye).dot(right) / (p - eye).dot(forward) for p in pts]
        vs = [(p - eye).dot(up) / (p - eye).dot(forward) for p in pts]
        du, dv = (min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2
        center = center + right * du * d + up * dv * d
    d = fit_distance()
    return wo.camera(name, center + direction * d, center, lens=lens)


def lineup_camera(templates, placed, name, extra_points=(), aspect=16 / 9):
    """Front 3/4 view from above that fits every object box, the labels and the dummy exactly."""
    pts = [Vector(p) for p in extra_points]
    for n, pos in placed:
        t = templates[n]
        lo, hi = t["bbox_min"], t["bbox_max"]
        for x in (lo[0], hi[0]):
            for y in (lo[1], hi[1]):
                for z in (lo[2], hi[2]):
                    pts.append(pos + Vector((x, -z, y)))
    return fit_camera("CAM_lineup_" + name, pts, Vector((0.35, 1.0, 0.85)), lens=40, aspect=aspect)

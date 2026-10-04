"""
review.py - the 3 standard views of one model (Phase 3 step 2) and a review strip.

    front 3/4   - from the front (+Y in Blender) and the right, a bit from above
    back 3/4    - from behind and the left
    eye level   - from a player's eye height (4.5 studs) with the 5-stud dummy standing next to it

Same light as the world shots. The strip (all three side by side) is what I look at while reviewing.
"""

import math
import os

import bpy
from mathutils import Vector

import wo

VIEW_W, VIEW_H = 800, 600


def studio(ground_rgb=(150, 156, 162)):
    wo.setup_render(VIEW_W, VIEW_H, samples=24)
    wo.setup_lighting(sun_direction=(0.5, -0.65, -0.62), sky_strength=1.15, sky_rgb=(205, 218, 240))
    ground = bpy.data.objects.get("StudioGround")
    if ground is None:
        mesh = bpy.data.meshes.new("StudioGround")
        s = 3000
        mesh.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
        ground = bpy.data.objects.new("StudioGround", mesh)
        bpy.context.scene.collection.objects.link(ground)
        mesh.materials.append(wo.roblox_material(ground_rgb, "SmoothPlastic", 0))
    return ground


def world_bounds(objs):
    pts = []
    for o in objs:
        if o.type != "MESH":
            continue
        for corner in o.bound_box:
            pts.append(o.matrix_world @ Vector(corner))
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def _fit_camera(name, center, radius, direction, lens=40.0, min_dist=6.0, corners=None, margin=1.08):
    """Places a camera looking at `center` from `direction`, as close as possible with every corner inside."""
    direction = direction.normalized()
    tan_x = 18.0 / lens  # sensor 36 mm, fit = horizontal
    tan_y = tan_x * VIEW_H / VIEW_W
    forward = -direction
    right = forward.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(forward).normalized()
    pts = corners or [center]

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

    lo_d, hi_d = 0.5, max(radius * 20, 50)
    for _ in range(40):
        mid = (lo_d + hi_d) / 2
        if fits(mid):
            hi_d = mid
        else:
            lo_d = mid
    dist = max(hi_d, min_dist)
    return wo.camera(name, center + direction * dist, center, lens=lens)


def render_views(objs, out_dir, name, dummy=None):
    """Renders front/back/eye views of `objs` (already placed at the origin). Returns the 3 paths."""
    lo, hi = world_bounds(objs)
    ground = bpy.data.objects.get("StudioGround")
    if ground is not None:  # the floor sits at the model's lowest point (no coplanar faces = no black acne)
        ground.location.z = min(lo.z, 0.0) - 0.02
    center = (lo + hi) / 2
    size = hi - lo
    radius = 0.5 * size.length
    corners = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    paths = []
    # front 3/4: front is +Y
    cam = _fit_camera("CAM_front34", center, radius, Vector((0.62, 1.0, 0.55)), corners=corners)
    paths.append(os.path.join(out_dir, name + "_front34.png"))
    wo.render(paths[-1], cam)
    cam = _fit_camera("CAM_back34", center, radius, Vector((-0.62, -1.0, 0.55)), corners=corners)
    paths.append(os.path.join(out_dir, name + "_back34.png"))
    wo.render(paths[-1], cam)
    # eye level: a player stands next to it (beside small things, in front of big ones), camera at 4.5 studs
    width = size.x
    if dummy is not None:
        if width > 10:
            dummy.location = (center.x + 0.22 * width, hi.y + 3.0, min(lo.z, 0.0) - 0.02)
        else:
            dummy.location = (lo.x - 2.6, center.y, min(lo.z, 0.0) - 0.02)
        dummy.hide_render = False
        lo2 = Vector((min(lo.x, dummy.location.x - 1.5), lo.y, lo.z))
    else:
        lo2 = lo
    span = max(hi.x - lo2.x, size.z * 1.4, 6.0)
    lens = 24 if width > 10 else 30
    fovh = 2 * math.atan(18.0 / lens)
    dist = span * 0.55 / math.tan(fovh / 2) + 1.5
    target = Vector(((lo2.x + hi.x) / 2, center.y, min(max(2.5, center.z), 5.5 + size.z * 0.25)))
    loc = Vector((target.x - dist * 0.25, hi.y + dist, 4.5))
    cam = wo.camera("CAM_eye", loc, target, lens=lens)
    paths.append(os.path.join(out_dir, name + "_eye.png"))
    wo.render(paths[-1], cam)
    if dummy is not None:
        dummy.hide_render = True
    return paths


def strip(paths, out_path, title=None):
    """Three views side by side (for my own review and the contact sheet)."""
    import numpy as np

    imgs = []
    for p in paths:
        img = bpy.data.images.load(p, check_existing=False)
        w, h = img.size
        arr = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
        imgs.append(arr)
        bpy.data.images.remove(img)
    h = max(a.shape[0] for a in imgs)
    out = np.ones((h, sum(a.shape[1] for a in imgs), 4), dtype=np.float32)
    x = 0
    for a in imgs:
        out[: a.shape[0], x: x + a.shape[1]] = a
        x += a.shape[1]
    img = bpy.data.images.new("strip", out.shape[1], out.shape[0], alpha=True)
    img.pixels.foreach_set(out.ravel())
    img.filepath_raw = out_path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)

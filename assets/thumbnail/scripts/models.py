"""Real game models from world_overhaul/blend/*.blend (branch claude/rags-to-riches-visual-overhaul-dey2rr).

Models are appended once as templates and placed as linked copies (they share mesh data).
Every model uses the one palette material (WO_Palette) and its glow materials; duplicates that come
with each library file are merged back into one, and the palette images point at
world_overhaul/palette/ (they are packed into thumbnail.blend when it is saved).
"""
import os
import sys
import bpy
import bmesh
from mathutils import Matrix, Vector


class Library:
    def __init__(self, wo_root):
        self.root = wo_root
        self.blend_dir = os.path.join(wo_root, "blend")
        self.palette_dir = os.path.join(wo_root, "palette")
        self.templates = {}
        self.hidden = bpy.data.collections.new("_templates")   # not linked to the scene
        sys.path.insert(0, os.path.join(wo_root, "tools", "blender"))

    # ---------------------------------------------------------------- loading
    def template(self, blend, name):
        """The model's objects (body + its _Glow/_Glass meshes), appended once."""
        key = (blend, name)
        if key in self.templates:
            return self.templates[key]
        path = os.path.join(self.blend_dir, blend + ".blend")
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            dst.objects = [n for n in src.objects
                           if n == name or n.startswith(name + "_Glow") or n.startswith(name + "_Glass")]
        objs = [o for o in dst.objects if o is not None]
        if not objs:
            raise KeyError(f"{name} not found in {blend}.blend")
        for o in objs:
            self.hidden.objects.link(o)
        self._fix_materials(objs)
        self.templates[key] = objs
        return objs

    def _fix_materials(self, objs):
        main = self.palette()
        for o in objs:
            for slot in o.material_slots:
                m = slot.material
                if m is None:
                    continue
                base = m.name.split(".")[0]
                if base == "WO_Palette":
                    slot.material = main
                elif base != m.name and bpy.data.materials.get(base):
                    slot.material = bpy.data.materials[base]

    def palette(self):
        """The shared palette material, with absolute image paths."""
        m = bpy.data.materials.get("WO_Palette")
        if m is None:
            import kit  # the game's own model kit makes the material the same way
            m = kit.Materials().palette()
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                fn = os.path.basename(n.image.filepath.replace("\\", "/"))
                n.image.filepath = os.path.join(self.palette_dir, fn)
                n.image.reload()
        return m

    # ---------------------------------------------------------------- placing
    def place(self, blend, name, coll, matrix, tag=None):
        """Linked copies of a model at `matrix` (the model's frame). Returns the new objects."""
        out = []
        for t in self.template(blend, name):
            c = t.copy()
            coll.objects.link(c)
            c.matrix_world = matrix @ t.matrix_world
            c["model"] = name
            if tag:
                c["tag"] = tag
            out.append(c)
        return out

    def mesh_without_part(self, blend, name, new_name, drop, recentre=True):
        """A copy of a model's body mesh without the loose parts `drop(verts)` selects
        (e.g. the display stand under the Gold Coin), origin at the remaining part's centre."""
        src = self.template(blend, name)[0]
        me = src.data.copy()
        me.name = new_name
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        seen, kill = set(), []
        for v in bm.verts:
            if v.index in seen:
                continue
            comp, stack = [], [v]
            seen.add(v.index)
            while stack:
                x = stack.pop()
                comp.append(x)
                for e in x.link_edges:
                    y = e.other_vert(x)
                    if y.index not in seen:
                        seen.add(y.index)
                        stack.append(y)
            if drop(comp):
                kill += comp
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        if recentre:
            c = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
            bmesh.ops.translate(bm, vec=-c, verts=bm.verts)
        bm.to_mesh(me)
        bm.free()
        return me

    # ---------------------------------------------------------------- distant look
    def distant_palette(self, fog=(0.62, 0.76, 0.92), sat=0.55, value=0.82, mix=0.28):
        """Palette variant for the middle ground: duller, darker and pushed toward the sky colour."""
        m = bpy.data.materials.get("WO_Palette_Distant")
        if m:
            return m
        m = self.palette().copy()
        m.name = "WO_Palette_Distant"
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        tex = next(n for n in nt.nodes if n.type == 'TEX_IMAGE' and "color" in n.image.name)
        hsv = nt.nodes.new("ShaderNodeHueSaturation")
        hsv.inputs["Saturation"].default_value = sat
        hsv.inputs["Value"].default_value = value
        mixn = nt.nodes.new("ShaderNodeMix")
        mixn.data_type = 'RGBA'
        mixn.inputs["Factor"].default_value = mix
        mixn.inputs["B"].default_value = (*fog, 1)
        nt.links.new(tex.outputs["Color"], hsv.inputs["Color"])
        nt.links.new(hsv.outputs["Color"], mixn.inputs["A"])
        nt.links.new(mixn.outputs["Result"], b.inputs["Base Color"])
        return m


def set_material(objs, old_prefix, new):
    for o in objs:
        for slot in getattr(o, "material_slots", []):
            if slot.material and slot.material.name.startswith(old_prefix):
                slot.material = new


def tile_chain(segment_mesh, path, closed, coll, link_scale, normal_fn, name="Chain", seg_len=3.0):
    """Lays real Dream_ChainSegment pieces (2 links per 3 studs, running along local -Y) end to end
    along a polyline. normal_fn(point, tangent) gives the direction the flat links face (away from
    the surface the chain lies on). The spacing is stretched a little so the links close exactly."""
    pts = [Vector(p) for p in path]
    segs = list(zip(pts, pts[1:] + ([pts[0]] if closed else [])))
    lengths = [(b - a).length for a, b in segs]
    total = sum(lengths)
    step = seg_len * link_scale
    n = max(1, round(total / step))
    k = total / (n * step)               # stretch (or squeeze) factor, close to 1
    objs = []
    for i in range(n):
        s = i * step * k
        acc = 0.0
        for (a, b), L in zip(segs, lengths):
            if s <= acc + L or (a, b) == segs[-1]:
                t = (b - a).normalized()
                p = a + t * (s - acc)
                break
            acc += L
        nrm = normal_fn(p, t)
        nrm = (nrm - t * nrm.dot(t)).normalized()
        ly = -t
        lz = nrm
        lx = ly.cross(lz)
        rot = Matrix((lx, ly, lz)).transposed()
        m = Matrix.Translation(p) @ rot.to_4x4() @ Matrix.Diagonal((link_scale, link_scale * k, link_scale, 1))
        o = bpy.data.objects.new(f"{name}_{i:03d}", segment_mesh)
        coll.objects.link(o)
        o.matrix_world = m
        objs.append(o)
    return objs


def convex_hull_2d(points):
    """Monotone chain convex hull, counter-clockwise."""
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def offset_polygon(poly, d):
    """Pushes a convex CCW polygon outward by d (miter joins, kept short)."""
    out = []
    n = len(poly)
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((e0.y, -e0.x)), Vector((e1.y, -e1.x))   # outward for CCW
        m = (n0 + n1)
        if m.length < 1e-6:
            m = n1
        m.normalize()
        cosh = max(m.dot(n1), 0.35)
        out.append(p1 + m * (d / cosh))
    return out


def simplify_polygon(poly, min_len):
    """Drops hull points closer than min_len to the previous kept one (a taut chain skips tiny bumps)."""
    out = [Vector(poly[0])]
    for p in poly[1:]:
        if (Vector(p) - out[-1]).length >= min_len:
            out.append(Vector(p))
    if len(out) > 3 and (out[0] - out[-1]).length < min_len:
        out.pop()
    return out

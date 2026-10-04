"""
kit.py - the shared building blocks for every model (see STYLE_GUIDE.md).

Write models in ROBLOX LOCAL COORDINATES, exactly like the game code does:
    x = right, y = up, z = back (the FRONT of a model is -Z), 1 unit = 1 stud,
    origin (0, 0, 0) = the object's frame (the spot the model drops into in the game).
The kit converts to Blender (x, -z, y) when the mesh is built, so in Blender the front faces +Y.

A Model collects pieces into up to three meshes (STYLE_GUIDE "one clean mesh per logical part"):
    <name>          the body: every face on the shared palette texture (SurfaceAppearance)
    <name>_Glow     glowing parts (Roblox Material = Neon, one color per glow mesh)
    <name>_Glass    see-through glass (Roblox Material = Glass, Transparency 0.3)

Every piece is a rounded primitive: bevel radius from the shared scale (S/M/L), smooth bevels with
flat faces kept flat ("hardened" normals), UVs on the center of one palette swatch.
"""

import json
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PALETTE = json.load(open(os.path.join(ROOT, "palette", "palette.json")))
COLORS = PALETTE["colors"]

# The ONE bevel radius scale (studs). Every edge in the world uses one of these.
BEVEL = {"XS": 0.06, "S": 0.12, "M": 0.25, "L": 0.5, "XL": 0.9}
SEGMENTS = {"XS": 1, "S": 2, "M": 2, "L": 2, "XL": 3}
MIN_THICK = 0.3  # nothing thinner than this (studs)

C = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))  # Roblox -> Blender
CT = C.transposed()


def rb(v):
    """Roblox local (x, y, z) -> Blender (x, -z, y)."""
    return Vector((v[0], -v[2], v[1]))


def rb_angles(rx=0.0, ry=0.0, rz=0.0):
    """Roblox CFrame.Angles(rx, ry, rz) (radians) as a Blender 3x3 rotation."""
    def mx(a):
        c, s = math.cos(a), math.sin(a)
        return Matrix(((1, 0, 0), (0, c, -s), (0, s, c)))

    def my(a):
        c, s = math.cos(a), math.sin(a)
        return Matrix(((c, 0, s), (0, 1, 0), (-s, 0, c)))

    def mz(a):
        c, s = math.cos(a), math.sin(a)
        return Matrix(((c, -s, 0), (s, c, 0), (0, 0, 1)))

    return C @ (mx(rx) @ my(ry) @ mz(rz)) @ CT


def deg(*angles):
    return [math.radians(a) for a in angles]


def round_segments(radius, wanted):
    """Round things get fewer sides when they are small (STYLE_GUIDE: resolution follows size)."""
    if radius < 0.25:
        cap = 6
    elif radius < 0.5:
        cap = 8
    elif radius < 0.8:
        cap = 10
    elif radius < 1.3:
        cap = 12
    elif radius < 2.5:
        cap = 16
    elif radius < 6:
        cap = 24
    else:
        cap = 999
    return max(6, min(wanted, cap))


class Model:
    def __init__(self, name):
        self.name = name
        self.groups = {}  # group -> dict(verts, faces, uvs, normals, mats)
        self.warnings = []
        self.R = Matrix.Identity(3)  # sub-assembly rotation (Roblox space)
        self.t = Vector((0, 0, 0))  # sub-assembly offset (Roblox space)

    # ------------------------------------------------------------------ helpers
    def _group(self, glow=None, glass=False):
        if glow:
            key = "Glow_" + glow
        elif glass:
            key = "Glass"
        else:
            key = "Body"
        if key not in self.groups:
            self.groups[key] = {"verts": [], "faces": [], "uvs": [], "normals": [], "flat": []}
        return self.groups[key]

    def _bevel(self, bm, size_min, bevel, edges=None, angle=math.radians(35)):
        if not bevel:
            return set()
        width = BEVEL[bevel] if isinstance(bevel, str) else float(bevel)
        segs = SEGMENTS[bevel] if isinstance(bevel, str) else (3 if width >= 0.4 else 2)
        width = min(width, size_min * 0.45)
        if width < 0.02:
            return set()
        if edges is None:
            bm.normal_update()
            edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > angle]
        if not edges:
            return set()
        res = bmesh.ops.bevel(bm, geom=edges + list({v for e in edges for v in e.verts}), offset=width,
                              offset_type="OFFSET", segments=segs, profile=0.5, affect="EDGES",
                              clamp_overlap=True)
        return set(res["faces"])

    def _add(self, bm, matrix, swatch, smooth_faces, glow=None, glass=False, all_smooth=False):
        """Transforms the piece (Blender-space 4x4 `matrix`), computes hardened normals and stores it.
        glow may carry a transparency: "RED@0.7" -> its own glow mesh "<name>_Glow_RED_T70"."""
        swatch = swatch.split("@")[0]
        if swatch not in COLORS:
            raise KeyError("not a palette color: %s" % swatch)
        g = self._group(glow, glass)
        bm.transform(matrix)
        bm.normal_update()
        smooth = set(smooth_faces)
        # normals of smooth faces around each vertex (angle-weighted)
        vnorm = {}
        for f in bm.faces:
            if all_smooth or f in smooth:
                for loop in f.loops:
                    w = loop.calc_angle()
                    vnorm.setdefault(loop.vert.index, Vector((0, 0, 0)))
                    vnorm[loop.vert.index] += f.normal * w
        base = len(g["verts"])
        bm.verts.index_update()
        for v in bm.verts:
            g["verts"].append(tuple(v.co))
        uv = tuple(COLORS[swatch]["uv"])
        for f in bm.faces:
            g["faces"].append(tuple(base + v.index for v in f.verts))
            is_smooth = all_smooth or f in smooth
            g["flat"].append(not is_smooth)
            for loop in f.loops:
                g["uvs"].append(uv)
                if is_smooth:
                    n = vnorm.get(loop.vert.index)
                    g["normals"].append(tuple(n.normalized()) if n is not None and n.length > 0 else tuple(f.normal))
                else:
                    g["normals"].append(tuple(f.normal))
        g.setdefault("glow", glow)
        bm.free()

    def _matrix(self, pos, rot):
        """pos: Roblox local position of the piece's center. rot: Blender-space 3x3 (or None).
        The current sub-assembly transform (self.R, self.t, Roblox space) is applied on top."""
        p = self.R @ Vector(pos) + self.t
        r = (C @ self.R @ CT) @ (rot if rot is not None else Matrix.Identity(3))
        m = r.to_4x4()
        m.translation = rb(p)
        return m

    # ------------------------------------------------------------------ primitives (Roblox local coords)
    def box(self, size, pos, swatch, bevel="M", rot=None, glow=None, glass=False, bottom=False, min_thick=True,
            round_bottom=None):
        """A rounded box. size = (x, y, z) studs. pos = center (or bottom center if bottom=True).
        Boxes standing on something (bottom=True) keep their 4 bottom edges sharp: nobody sees them."""
        sx, sy, sz = size
        if min_thick and min(sx, sy, sz) < MIN_THICK - 1e-6:
            self.warnings.append("thin box %s at %s" % (size, pos))
            sx, sy, sz = max(sx, MIN_THICK), max(sy, MIN_THICK), max(sz, MIN_THICK)
        if bottom:
            pos = (pos[0], pos[1] + sy / 2, pos[2])
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(sx, sz, sy), verts=bm.verts)  # Blender axes: x, y(depth), z(up)
        edges = list(bm.edges)
        if (round_bottom is None and bottom) or round_bottom is False:
            edges = [e for e in edges if not all(v.co.z < -sy / 2 + 1e-6 for v in e.verts)]
        smooth = self._bevel(bm, min(sx, sy, sz), bevel, edges=edges)
        self._add(bm, self._matrix(pos, rot), swatch, smooth, glow, glass)

    def cyl(self, radius, length, pos, swatch, axis="Y", bevel="M", rot=None, verts=20, glow=None, glass=False,
            radius_top=None, bottom=False):
        """A rounded cylinder (or cone/frustum with radius_top). axis = Roblox axis it points along."""
        if bottom and axis == "Y":
            pos = (pos[0], pos[1] + length / 2, pos[2])
        if radius * 2 < MIN_THICK - 1e-6:
            self.warnings.append("thin cylinder r=%.2f at %s" % (radius, pos))
            radius = MIN_THICK / 2
        if radius_top is not None and 0 < radius_top * 2 < MIN_THICK - 1e-6:
            radius_top = MIN_THICK / 2
        if length < MIN_THICK - 1e-6:
            self.warnings.append("thin cylinder length=%.2f at %s" % (length, pos))
            length = MIN_THICK
        verts = round_segments(max(radius, radius_top or 0), verts)
        if max(radius, radius_top or 0) < 0.26 and bevel in ("XS", "S"):
            bevel = None  # a rim this small is never seen
        bm = bmesh.new()
        rt = radius if radius_top is None else radius_top
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=radius, radius2=rt,
                              depth=length)
        # created along Blender Z; turn to the wanted Roblox axis
        turn = {"Y": Matrix.Identity(3), "X": Matrix.Rotation(math.radians(90), 3, "Y"),
                "Z": Matrix.Rotation(math.radians(90), 3, "X")}[axis]
        bm.transform(turn.to_4x4())
        bm.normal_update()
        sides = [f for f in bm.faces if len(f.verts) == 4]
        rims = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(40)]
        smooth = set(sides) | self._bevel(bm, min(radius, rt, length / 2) * 2 if rt > 0 else length, bevel, edges=rims)
        smooth = {f for f in bm.faces if f in smooth or len(f.verts) != verts}
        self._add(bm, self._matrix(pos, rot), swatch, smooth, glow, glass)

    def sphere(self, radius, pos, swatch, scale=(1, 1, 1), rot=None, segs=16, rings=10, glow=None, glass=False):
        if radius * 2 * min(scale) < MIN_THICK - 1e-6:
            self.warnings.append("thin sphere r=%.2f at %s" % (radius, pos))
        segs = round_segments(radius * max(scale), segs)
        rings = max(4, min(rings, segs // 2 + 1))
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
        bmesh.ops.scale(bm, vec=(scale[0], scale[2], scale[1]), verts=bm.verts)
        self._add(bm, self._matrix(pos, rot), swatch, [], glow, glass, all_smooth=True)

    def dome(self, radius, height, pos, swatch, segs=16, rings=6, rot=None, glow=None):
        """Top half of a sphere, squashed to `height`, standing on pos (bottom center)."""
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings * 2, radius=radius)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context="VERTS")
        bmesh.ops.scale(bm, vec=(1, 1, height / radius), verts=bm.verts)
        # close the bottom
        edges = [e for e in bm.edges if e.is_boundary]
        if edges:
            bmesh.ops.edgeloop_fill(bm, edges=edges)
        bm.normal_update()
        smooth = [f for f in bm.faces if len(f.verts) <= 4]
        self._add(bm, self._matrix(pos, rot), swatch, smooth, glow)

    def torus(self, major, minor, pos, swatch, axis="Z", rot=None, segs=20, ring_segs=8, glow=None, scale=None):
        if minor * 2 < MIN_THICK - 1e-6:
            self.warnings.append("thin torus r=%.2f at %s" % (minor, pos))
            minor = MIN_THICK / 2
        segs = round_segments(major, segs)
        ring_segs = round_segments(minor, ring_segs)
        bm = bmesh.new()
        verts = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            ring = []
            for j in range(ring_segs):
                b = 2 * math.pi * j / ring_segs
                r = major + minor * math.cos(b)
                ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), minor * math.sin(b))))
            verts.append(ring)
        for i in range(segs):
            for j in range(ring_segs):
                a, b = verts[i][j], verts[(i + 1) % segs][j]
                c, d = verts[(i + 1) % segs][(j + 1) % ring_segs], verts[i][(j + 1) % ring_segs]
                bm.faces.new((a, b, c, d))
        turn = {"Y": Matrix.Identity(3), "X": Matrix.Rotation(math.radians(90), 3, "Y"),
                "Z": Matrix.Rotation(math.radians(90), 3, "X")}[axis]
        bm.transform(turn.to_4x4())
        if scale is not None:  # Roblox axes (x, y, z) -> Blender (x, z, y)
            bmesh.ops.scale(bm, vec=(scale[0], scale[2], scale[1]), verts=bm.verts)
        self._add(bm, self._matrix(pos, rot), swatch, [], glow, all_smooth=True)

    def prism(self, points, depth, pos, swatch, plane="XY", bevel="S", rot=None, glow=None, glass=False):
        """An extruded 2D shape. plane "XY": points are (x, y) in the front plane, extruded along Z (depth).
        plane "XZ": points are (x, z) seen from above, extruded up (depth = height, pos = bottom center).
        plane "ZY": points are (z, y) seen from the side, extruded along X."""
        bm = bmesh.new()
        h = depth / 2
        if plane == "XY":
            back = [bm.verts.new(rb((x, y, h))) for x, y in points]
            front = [bm.verts.new(rb((x, y, -h))) for x, y in points]
        elif plane == "XZ":
            back = [bm.verts.new(rb((x, 0, z))) for x, z in points]
            front = [bm.verts.new(rb((x, depth, z))) for x, z in points]
        else:
            back = [bm.verts.new(rb((-h, y, z))) for z, y in points]
            front = [bm.verts.new(rb((h, y, z))) for z, y in points]
        bm.faces.new(back)
        bm.faces.new(list(reversed(front)))
        n = len(points)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((back[i], back[j], front[j], front[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        size_min = depth
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        size_min = min(size_min, max(xs) - min(xs), max(ys) - min(ys))
        smooth = self._bevel(bm, size_min, bevel)
        m = self._matrix(pos, rot)
        self._add(bm, m, swatch, smooth, glow, glass)

    def wedge(self, size, pos, swatch, bevel="S", rot=None, bottom=False):
        """Roblox WedgePart: flat bottom, tall face at the back (+Z), slope down to the front (-Z)."""
        sx, sy, sz = size
        if bottom:
            pos = (pos[0], pos[1] + sy / 2, pos[2])
        hy, hz = sy / 2, sz / 2
        self.prism([(-hz, -hy), (hz, -hy), (hz, hy)], sx, pos, swatch, plane="ZY", bevel=bevel, rot=rot)

    def custom(self, verts, faces, swatch, all_smooth=True, glow=None, glass=False, bevel=None):
        """A free-form closed mesh. verts in Roblox local coords, faces = tuples of vertex indices."""
        bm = bmesh.new()
        bv = [bm.verts.new(rb(v)) for v in verts]
        for f in faces:
            try:
                bm.faces.new([bv[i] for i in f])
            except ValueError:
                pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        smooth = self._bevel(bm, 0.6, bevel) if bevel else set()
        self._add(bm, self._matrix((0, 0, 0), None), swatch, smooth, glow, glass, all_smooth=all_smooth)

    def capsule(self, radius, length, pos, swatch, axis="Y", rot=None, segs=16, glow=None):
        """A rounded rod: cylinder with half-spheres on both ends (total length = length)."""
        if radius * 2 < MIN_THICK - 1e-6:
            self.warnings.append("thin capsule r=%.2f at %s" % (radius, pos))
            radius = MIN_THICK / 2
        body = max(length - 2 * radius, 0.01)
        segs = round_segments(radius, segs)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=max(4, min(8, segs // 2 + 1)), radius=radius)
        for v in bm.verts:
            v.co.z += body / 2 if v.co.z > 0 else -body / 2
        turn = {"Y": Matrix.Identity(3), "X": Matrix.Rotation(math.radians(90), 3, "Y"),
                "Z": Matrix.Rotation(math.radians(90), 3, "X")}[axis]
        bm.transform(turn.to_4x4())
        self._add(bm, self._matrix(pos, rot), swatch, [], glow, all_smooth=True)

    def stick(self, a, b, radius, swatch, radius_b=None, verts=12, bevel="XS"):
        """A (tapered) cylinder from point a to point b (Roblox coords)."""
        a, b = Vector(a), Vector(b)
        d = b - a
        rot = Vector((0, 0, 1)).rotation_difference(rb(d).normalized()).to_matrix()
        self.cyl(radius, d.length, (a + b) / 2, swatch, axis="Y", rot=rot, verts=verts, bevel=bevel,
                 radius_top=radius_b)

    def bar(self, a, b, thickness, swatch, round_bar=True, bevel="S"):
        """A stick from point a to point b (Roblox coords)."""
        a, b = Vector(a), Vector(b)
        d = b - a
        length = d.length
        mid = (a + b) / 2
        # rotation that turns Roblox +Y onto d (in Blender space)
        bd = rb(d).normalized()
        rot = Vector((0, 0, 1)).rotation_difference(bd).to_matrix()
        if round_bar:
            self.capsule(thickness / 2, length + thickness, mid, swatch, axis="Y", rot=rot, segs=10)
        else:
            self.box((thickness, length, thickness), mid, swatch, bevel=bevel, rot=rot)

    # ------------------------------------------------------------------ sub-assemblies
    def at(self, offset=(0, 0, 0), yaw=0.0, pitch=0.0):
        """with model.at((x, y, z), yaw): everything added inside is moved by `offset` and turned by `yaw`
        degrees around Y (Roblox), relative to the current sub-assembly. Kit parts use this."""
        model = self

        class _Ctx:
            def __enter__(self_):
                self_.old = (model.R.copy(), model.t.copy())
                a = math.radians(yaw)
                c, s_ = math.cos(a), math.sin(a)
                ry = Matrix(((c, 0, s_), (0, 1, 0), (-s_, 0, c)))
                b = math.radians(pitch)
                cb, sb = math.cos(b), math.sin(b)
                rx = Matrix(((1, 0, 0), (0, cb, -sb), (0, sb, cb)))  # Roblox CFrame.Angles(pitch, 0, 0)
                model.t = model.R @ Vector(offset) + model.t
                model.R = model.R @ ry @ rx
                return model

            def __exit__(self_, *exc):
                model.R, model.t = self_.old

        return _Ctx()

    # ------------------------------------------------------------------ build
    def triangles(self):
        return sum(sum(len(f) - 2 for f in g["faces"]) for g in self.groups.values())

    def build(self, collection, materials):
        """Makes the Blender objects (origin = the object's frame). Returns the list of objects."""
        objects = []
        for key in sorted(self.groups):
            g = self.groups[key]
            name = self.name if key == "Body" else "%s_%s" % (self.name, key.split("_")[0])
            if key.startswith("Glow_"):
                color, _, tr = key[5:].partition("@")
                name = "%s_Glow_%s" % (self.name, color) + ("_T%d" % round(float(tr) * 100) if tr else "")
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(g["verts"], [], g["faces"])
            uv = mesh.uv_layers.new(name="UVMap")
            flat_uvs = [c for t in g["uvs"] for c in t]
            uv.data.foreach_set("uv", flat_uvs)
            mesh.polygons.foreach_set("use_smooth", [not f for f in g["flat"]])
            mesh.validate(clean_customdata=False)
            mesh.normals_split_custom_set(g["normals"])
            transparency = 0.0
            if key.startswith("Glow_"):
                color, _, tr = key[5:].partition("@")
                transparency = float(tr) if tr else 0.0
                mesh.materials.append(materials.glow(color, alpha=1.0 - transparency))
            elif key == "Glass":
                mesh.materials.append(materials.glass())
            else:
                mesh.materials.append(materials.palette())
            obj = bpy.data.objects.new(name, mesh)
            collection.objects.link(obj)
            obj["wo_role"] = key.split("_")[0]
            if transparency >= 0.999:  # hidden until a game script shows it (e.g. the top-bidder highlight)
                obj.hide_render = True
            objects.append(obj)
        return objects


def _to_rb(v):
    """Blender vector -> Roblox (x, y, z)."""
    return (v[0], v[2], -v[1])


# ----------------------------------------------------------------------------
# Materials for Blender renders (the Roblox look is in STYLE_GUIDE.md)
# ----------------------------------------------------------------------------


def lin(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (ch(rgb[0]), ch(rgb[1]), ch(rgb[2]), 1.0)


class Materials:
    def __init__(self):
        self._palette = None
        self._glows = {}
        self._glass = None

    def palette(self):
        if self._palette is not None:
            return self._palette
        mat = bpy.data.materials.get("WO_Palette")
        if mat is None:
            mat = bpy.data.materials.new("WO_Palette")
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            bsdf = nodes.get("Principled BSDF")
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(os.path.join(ROOT, "palette", "palette_color.png"), check_existing=True)
            tex.interpolation = "Closest"
            rough = nodes.new("ShaderNodeTexImage")
            rough.image = bpy.data.images.load(os.path.join(ROOT, "palette", "palette_roughness.png"), check_existing=True)
            rough.image.colorspace_settings.name = "Non-Color"
            rough.interpolation = "Closest"
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
            bsdf.inputs["Specular IOR Level"].default_value = 0.5
        self._palette = mat
        return mat

    def glow(self, swatch, alpha=1.0):
        alpha = round(alpha, 2)
        if (swatch, alpha) in self._glows:
            return self._glows[(swatch, alpha)]
        name = "WO_Glow_" + swatch + ("" if alpha >= 0.999 else "_A%d" % round(alpha * 100))
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        # (re)applied every time, so blends saved with older settings follow the current ones
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        rgb = COLORS[swatch]["rgb"]
        bsdf.inputs["Base Color"].default_value = lin(rgb)
        bsdf.inputs["Emission Color"].default_value = lin(rgb)
        bsdf.inputs["Emission Strength"].default_value = 1.2  # bright, but the hue still shows
        bsdf.inputs["Alpha"].default_value = max(min(alpha, 1.0), 0.0)
        self._glows[(swatch, alpha)] = mat
        return mat

    def glass(self):
        if self._glass is not None:
            return self._glass
        mat = bpy.data.materials.get("WO_Glass")
        if mat is None:
            mat = bpy.data.materials.new("WO_Glass")
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Base Color"].default_value = lin(COLORS["WINDOW"]["rgb"])
            bsdf.inputs["Roughness"].default_value = 0.05
            bsdf.inputs["Alpha"].default_value = 0.55
        self._glass = mat
        return mat

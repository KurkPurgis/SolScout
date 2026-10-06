"""The player's real Roblox avatar (assets/thumbnail/thumbnail/avatar.obj, an R15 export from
Roblox Studio) imported, rigged with empties at its joints and posed.

Studio names the 15 body parts Rig1..Rig15 (plus Handle1 for the hair accessory), so the parts are
identified by where they are: torso parts in the middle, legs below the lower torso, arms out to the
sides, each chain ordered by height. The OBJ faces +Y in Blender (the feet point that way), so the
avatar's right is +X.

Joints are empties in a hierarchy (pelvis > waist > neck / shoulders > elbows > wrists, pelvis >
hips > knees > ankles); every mesh part is parented to its joint and the joints are rotated.
Joint centres are found from the meshes: each limb part's long axis (PCA) gives its two ends, a
joint sits between the touching ends of two parts.
"""
import math
import numpy as np
import bpy
from mathutils import Vector, Matrix, Quaternion

ORDER = ["UpperTorso", "LowerTorso", "Head", "Hair",
         "RightUpperArm", "RightLowerArm", "RightHand", "LeftUpperArm", "LeftLowerArm", "LeftHand",
         "RightUpperLeg", "RightLowerLeg", "RightFoot", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot"]


def _pts(o):
    return np.array([tuple(o.matrix_world @ v.co) for v in o.data.vertices])


def _axis_ends(P):
    """Centroid, unit long axis and the two ends of a part (PCA)."""
    c = P.mean(axis=0)
    w, V = np.linalg.eigh(np.cov((P - c).T))
    a = V[:, np.argmax(w)]
    t = (P - c) @ a
    return Vector(c), Vector(a), Vector(c + a * t.min()), Vector(c + a * t.max())


def import_avatar(path, coll):
    """Imports the OBJ into `coll`, returns {part name: object}, feet on z=0, centred on x/y."""
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path, use_split_groups=True, use_split_objects=True)
    objs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    for o in objs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    # textures: the body texture is fully opaque where it is used; drop the alpha links so
    # Cycles never treats skin as see-through (keep the hair's alpha)
    for o in objs:
        for m in o.data.materials:
            if m and m.node_tree and not o.name.startswith("Handle"):
                b = m.node_tree.nodes.get("Principled BSDF")
                for l in list(m.node_tree.links):
                    if l.to_node == b and l.to_socket.name == "Alpha":
                        m.node_tree.links.remove(l)
            if m and m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == 'TEX_IMAGE' and n.image:
                        n.interpolation = 'Linear'
    allp = np.vstack([_pts(o) for o in objs])
    off = Vector((-(allp[:, 0].min() + allp[:, 0].max()) / 2, -(allp[:, 1].min() + allp[:, 1].max()) / 2,
                  -allp[:, 2].min()))
    for o in objs:
        o.data.transform(Matrix.Translation(off) @ o.matrix_world)
        o.matrix_world = Matrix.Identity(4)

    info = {o: _pts(o).mean(axis=0) for o in objs}
    hair = [o for o in objs if o.name.startswith("Handle")]
    body = [o for o in objs if o not in hair]
    mid = [o for o in body if abs(info[o][0]) < 0.25]
    mid.sort(key=lambda o: info[o][2])
    lower_torso, upper_torso, head = mid[0], mid[1], mid[2]
    parts = {"LowerTorso": lower_torso, "UpperTorso": upper_torso, "Head": head}
    rest = [o for o in body if o not in mid]
    # legs sit under the hips, arms hang out at the sides (hands are lower than the hips)
    legs = [o for o in rest if abs(info[o][0]) < 0.75]
    arms = [o for o in rest if o not in legs]
    # front: the feet stick out forward of the shins
    feet_side = sorted(legs, key=lambda o: info[o][2])
    foot, shin = feet_side[0], [o for o in legs if abs(info[o][0] - info[feet_side[0]][0]) < 0.3]
    shin = sorted(shin, key=lambda o: info[o][2])[1]
    front = 1.0 if info[foot][1] > info[shin][1] else -1.0
    right_sign = front  # facing +Y -> right is +X
    for side, sgn in (("Right", right_sign), ("Left", -right_sign)):
        l = sorted([o for o in legs if info[o][0] * sgn > 0], key=lambda o: info[o][2])
        a = sorted([o for o in arms if info[o][0] * sgn > 0], key=lambda o: info[o][2])
        assert len(l) == 3 and len(a) == 3, "unexpected avatar layout"
        parts[side + "Foot"], parts[side + "LowerLeg"], parts[side + "UpperLeg"] = l
        parts[side + "Hand"], parts[side + "LowerArm"], parts[side + "UpperArm"] = a
    if hair:
        parts["Hair"] = hair[0]
        for h in hair[1:]:
            parts["Hair%d" % len(parts)] = h
    for k, o in parts.items():
        o.name = "Avatar_" + k
    return parts, front


class Rig:
    """Empties at the joints; pose by rotating them (degrees, in the avatar's own axes:
    X = his right, Y = his front, Z = up), or with two-bone IK for the arms."""

    def __init__(self, parts, coll):
        self.parts, self.coll = parts, coll
        P = {k: _pts(o) for k, o in parts.items()}
        self.ends = {k: _axis_ends(v) for k, v in P.items()}

        def bbox(k):
            q = P[k]
            return Vector(q.min(axis=0)), Vector(q.max(axis=0))

        def joint(a, b):
            """joint between parent part a and child part b. R15 parts overlap at the joints, so
            take the end of a nearest b's centre and the end of b nearest a's centre."""
            ca, cb = self.ends[a][0], self.ends[b][0]
            ea = min(self.ends[a][2:], key=lambda e: (e - cb).length)
            eb = min(self.ends[b][2:], key=lambda e: (e - ca).length)
            return (ea + eb) / 2

        def far_end(a, b):
            """the end of part a away from part b (shoulder/hip end)."""
            cb = self.ends[b][0]
            return max(self.ends[a][2:], key=lambda e: (e - cb).length)

        (lt0, lt1), (ut0, ut1), (hd0, hd1) = bbox("LowerTorso"), bbox("UpperTorso"), bbox("Head")
        J = {}
        J["Pelvis"] = Vector((0, (lt0.y + lt1.y) / 2, (lt0.z + lt1.z) / 2))
        J["Waist"] = Vector((0, (ut0.y + ut1.y) / 2, (lt1.z + ut0.z) / 2))
        J["Neck"] = Vector((0, (hd0.y + hd1.y) / 2, (ut1.z + hd0.z) / 2))
        for s in ("Right", "Left"):
            ua, la, hn = s + "UpperArm", s + "LowerArm", s + "Hand"
            ul, ll, ft = s + "UpperLeg", s + "LowerLeg", s + "Foot"
            top = far_end(ua, la)
            thick = float(np.ptp(P[ua][:, 0])) * 0.5
            J[s + "Shoulder"] = top + (self.ends[ua][0] - top).normalized() * thick * 0.55
            J[s + "Elbow"] = joint(ua, la)
            # wrist: the forearm's end at the hand, a little way up the forearm
            ce = self.ends[la][0]
            we = min(self.ends[la][2:], key=lambda e: (e - self.ends[hn][0]).length)
            J[s + "Wrist"] = we + (ce - we).normalized() * 0.12
            top = far_end(ul, ll)
            J[s + "Hip"] = top + (self.ends[ul][0] - top).normalized() * 0.3
            J[s + "Knee"] = joint(ul, ll)
            (f0, f1), (s0, s1) = bbox(ft), bbox(ll)
            J[s + "Ankle"] = Vector(((s0.x + s1.x) / 2, (s0.y + s1.y) / 2, f1.z - 0.3))
        self.rest = J
        tree = [("Pelvis", None), ("Waist", "Pelvis"), ("Neck", "Waist"),
                ("RightShoulder", "Waist"), ("RightElbow", "RightShoulder"), ("RightWrist", "RightElbow"),
                ("LeftShoulder", "Waist"), ("LeftElbow", "LeftShoulder"), ("LeftWrist", "LeftElbow"),
                ("RightHip", "Pelvis"), ("RightKnee", "RightHip"), ("RightAnkle", "RightKnee"),
                ("LeftHip", "Pelvis"), ("LeftKnee", "LeftHip"), ("LeftAnkle", "LeftKnee")]
        self.root = bpy.data.objects.new("Avatar", None)
        coll.objects.link(self.root)
        self.j = {}
        for name, par in tree:
            e = bpy.data.objects.new("J_" + name, None)
            coll.objects.link(e)
            e.empty_display_size = 0.2
            e.rotation_mode = 'QUATERNION'
            parent = self.j[par] if par else self.root
            e.parent = parent
            e.location = J[name] - (J[par] if par else Vector())
            self.j[name] = e
        owner = {"LowerTorso": "Pelvis", "UpperTorso": "Waist", "Head": "Neck",
                 "RightUpperArm": "RightShoulder", "RightLowerArm": "RightElbow", "RightHand": "RightWrist",
                 "LeftUpperArm": "LeftShoulder", "LeftLowerArm": "LeftElbow", "LeftHand": "LeftWrist",
                 "RightUpperLeg": "RightHip", "RightLowerLeg": "RightKnee", "RightFoot": "RightAnkle",
                 "LeftUpperLeg": "LeftHip", "LeftLowerLeg": "LeftKnee", "LeftFoot": "LeftAnkle"}
        bpy.context.view_layer.update()
        for k, o in parts.items():
            jn = owner.get(k, "Neck")      # hair (and any accessory) rides on the head
            e = self.j[jn]
            o.parent = e
            o.matrix_parent_inverse = e.matrix_world.inverted()

    # ------------------------------------------------------------------ placement and posing
    def place(self, loc, front_dir):
        """Stand him at loc (feet), his front pointing along front_dir (world, horizontal)."""
        f = Vector((front_dir[0], front_dir[1], 0)).normalized()
        yaw = math.atan2(-f.x, f.y)            # rest front is +Y
        self.root.matrix_world = Matrix.Translation(loc) @ Matrix.Rotation(yaw, 4, 'Z')
        bpy.context.view_layer.update()

    def rot(self, joint, x=0.0, y=0.0, z=0.0):
        """Local rotation of a joint (degrees about his X right, Y front, Z up; applied Z, Y, X)."""
        q = (Matrix.Rotation(math.radians(z), 3, 'Z') @ Matrix.Rotation(math.radians(y), 3, 'Y')
             @ Matrix.Rotation(math.radians(x), 3, 'X')).to_quaternion()
        self.j[joint].rotation_quaternion = q
        bpy.context.view_layer.update()

    def world(self, joint):
        return self.j[joint].matrix_world.translation.copy()

    def _aim(self, joint, child_joint, target_dir):
        """Rotate `joint` so the bone joint->child points along target_dir (world)."""
        e = self.j[joint]
        cur = (self.world(child_joint) - self.world(joint)).normalized()
        d = Vector(target_dir).normalized()
        delta = cur.rotation_difference(d)
        pw = e.parent.matrix_world.to_quaternion()
        ew = e.matrix_world.to_quaternion()
        new_w = delta @ ew
        e.rotation_quaternion = pw.inverted() @ new_w
        bpy.context.view_layer.update()

    def ik_arm(self, side, wrist_target, pole):
        """Two-bone IK: shoulder and elbow so the wrist reaches wrist_target; the elbow bends
        toward `pole` (a world direction)."""
        s, el, wr = side + "Shoulder", side + "Elbow", side + "Wrist"
        S = self.world(s)
        L1 = (self.rest[el] - self.rest[s]).length
        L2 = (self.rest[wr] - self.rest[el]).length
        T = Vector(wrist_target)
        D = T - S
        dist = min(max(D.length, abs(L1 - L2) + 1e-3), L1 + L2 - 1e-3)
        dn = D.normalized()
        a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
        h = math.sqrt(max(L1 * L1 - a * a, 0.0))
        p = Vector(pole) - dn * Vector(pole).dot(dn)
        p = p.normalized() if p.length > 1e-6 else Vector((0, 0, 1))
        E = S + dn * a + p * h
        self._aim(s, el, E - S)
        self._aim(el, wr, (S + dn * dist) - E)

    def aim_bone(self, joint, child_joint, target_dir):
        self._aim(joint, child_joint, target_dir)

    def aim_head(self, direction):
        """Turn the neck so his face (the head's +Y) points along `direction` (world)."""
        e = self.j["Neck"]
        cur = (e.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
        delta = cur.rotation_difference(Vector(direction).normalized())
        pw = e.parent.matrix_world.to_quaternion()
        e.rotation_quaternion = pw.inverted() @ (delta @ e.matrix_world.to_quaternion())
        bpy.context.view_layer.update()

    def centre(self, part):
        o = self.parts[part]
        pts = [o.matrix_world @ v.co for v in o.data.vertices]
        return sum(pts, Vector()) / len(pts)

    def aim_part(self, joint, part, target_point):
        """Rotate `joint` so the direction joint -> centre of `part` points at target_point."""
        e = self.j[joint]
        jw = self.world(joint)
        cur = (self.centre(part) - jw).normalized()
        d = (Vector(target_point) - jw).normalized()
        delta = cur.rotation_difference(d)
        pw = e.parent.matrix_world.to_quaternion()
        e.rotation_quaternion = pw.inverted() @ (delta @ e.matrix_world.to_quaternion())
        bpy.context.view_layer.update()

    def bounds(self):
        dg = bpy.context.evaluated_depsgraph_get()
        pts = []
        for o in self.parts.values():
            ev = o.evaluated_get(dg)
            pts += [ev.matrix_world @ v.co for v in ev.data.vertices]
        return pts

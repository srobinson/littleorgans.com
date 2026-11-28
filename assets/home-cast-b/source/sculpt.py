# Written by tm/frontend (gpt-6.2-sol).

"""Sculpt a role from crowns, frames, legs, arms and hands."""

from math import radians

import bpy
from mathutils import Vector

from parts import CROWNS, FRAMES


def material(label, tone, roughness=.45):
    mat = bpy.data.materials.new(label)
    mat.diffuse_color = (tone, tone, tone, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (tone, tone, tone, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Specular IOR Level"].default_value = .36
    return mat


class Shop:
    def __init__(self):
        self.ink = material("Dense charcoal", .026, .42)
        self.seam = material("Blackened steel", .045, .38)
        self.bright = material("Porcelain", .59, .48)
        self.pupil = material("Eye inset", .008, .63)
        self.floor = material("Limestone", .51, .81)
        self.wall = material("Plaster", .59, .82)
        self.dark = material("Boundary charcoal", .062, .70)
        self.recess = material("Plaster in the opening", .29, .85)
        self.grain(self.floor, 16, .018)
        self.grain(self.wall, 24, .012)

    @staticmethod
    def grain(material, scale, distance):
        nodes, links = material.node_tree.nodes, material.node_tree.links
        texture = nodes.new("ShaderNodeTexNoise")
        coords = nodes.new("ShaderNodeTexCoord")
        texture.inputs["Scale"].default_value = scale
        texture.inputs["Detail"].default_value = 2.2
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .16
        bump.inputs["Distance"].default_value = distance
        links.new(coords.outputs["Object"], texture.inputs["Vector"])
        links.new(texture.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], nodes.get("Principled BSDF").inputs["Normal"])

    def finish(self, obj, mat, bevel, soften=True):
        obj.data.materials.append(mat)
        if bevel:
            edge = obj.modifiers.new("Cut edges", "BEVEL")
            edge.width = bevel
            edge.segments = 3 if soften else 1
            edge.affect = "EDGES"
            edge.harden_normals = True
            normals = obj.modifiers.new("Face weighted normals", "WEIGHTED_NORMAL")
            normals.keep_sharp = True
        return obj

    def box(self, name, center, dimensions, bevel=.035, mat=None):
        x, y, z = (a / 2 for a in dimensions)
        obj = self.slab(name, ((-x, -z), (x, -z), (x, z), (-x, z)), y * 2,
                        bevel=bevel, mat=mat)
        obj.location = center
        return obj

    def slab(self, name, profile, depth, y=0, bevel=.05, mat=None):
        p = tuple(profile)
        n = len(p)
        if sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(p, p[1:] + p[:1])) < 0:
            p = p[::-1]
        verts = [(x, t, z) for t in (y - depth / 2, y + depth / 2) for x, z in p]
        faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
        faces += [(i, i+n, (i+1) % n + n, (i+1) % n) for i in range(n)]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        return self.finish(obj, mat or self.ink, bevel)

    def bar(self, name, a, b, width, breadth=None, taper=.84, mat=None):
        """An oriented rectangular bar with a smaller section at b."""
        a, b = Vector(a), Vector(b)
        width, breadth = width / 2, (breadth or width) / 2
        dx = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        distance = (b - a).length
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata([(u * width * r, v * breadth * r, z)
                          for r, z in ((1, 0), (taper, distance)) for u, v in dx],
                         [], [(3, 2, 1, 0), (4, 5, 6, 7),
                              (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = a
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = (b - a).to_track_quat("Z", "Y")
        return self.finish(obj, mat or self.ink, min(width*.38, .059))

    def folded_bar(self, name, centers, widths, breadth):
        """A continuous cut bar. The middle ring is a bend, never a visible joint."""
        points = list(map(Vector, centers))
        verts = []
        for i, (p, width) in enumerate(zip(points, widths)):
            a, b = points[max(i-1, 0)], points[min(i+1, len(points)-1)]
            axis = (b-a).normalized()
            front = (Vector((0, 1, 0)) - axis.y*axis).normalized()
            side = front.cross(axis).normalized()
            verts.extend(p + side*(u*width/2) + front*(v*breadth/2)
                         for u, v in ((-1,-1), (1,-1), (1,1), (-1,1)))
        last = len(verts) - 4
        faces = [(3, 2, 1, 0), tuple(range(last, last+4))]
        faces += [(i+j, i+(j+1)%4, i+(j+1)%4+4, i+j+4)
                  for i in range(0, last, 4) for j in range(4)]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        return self.finish(obj, self.ink, min(.047, min(widths)*.24))


class Figure:
    def __init__(self, shop, role):
        self.shop = shop
        self.role = role
        self.frame = FRAMES[role.frame]

    def head(self, kind, eye):
        s, f, c = self.shop, self.frame, CROWNS[kind]
        w, h = c.width/2, c.height
        profiles = {
            "cut": ((-1, .05), (-1, 1), (1, 1), (1, .28), (.67, .28), (.37, 0)),
            "steps": ((-.74, .01), (-.49, .38), (-1, .42), (-.70, .57), (-1, .64),
                      (-.60, .76), (-.77, 1), (.47, 1), (.97, .63), (1, .25), (.60, 0)),
            "shelf": ((-1, .20), (-1, .82), (-.74, 1), (.82, 1), (1, .75),
                      (1, .08), (.55, 0), (-.95, 0)),
            "lintel": ((-1, .18), (-1, .78), (-.76, 1), (.85, 1), (1, .69),
                       (1, .24), (.70, 0), (-.70, 0)),
            "wedge": ((-1, .05), (-.82, .72), (.53, 1), (1, .68), (.96, .21), (.44, 0)),
            "recess": ((-1, .19), (-1, .91), (.71, 1), (1, .70), (1, .27), (.57, .01), (-.66, 0)),
        }
        shift = f.lean + (.26 if kind == "swept" else .11 if kind == "square" else 0)
        s.bar("Neck bar", (f.lean*.72, .03, f.chest-.09),
              (shift-.09, .02, f.neck + .13), max(f.limb*1.14, .20), max(f.limb*1.42, .30))
        s.slab("Head tile", [(shift+u*w, f.neck+v*h) for u, v in profiles[c.form]],
               c.depth, bevel=.045 if c.form == "steps" else .060)
        if kind == "shelf":
            s.box("Shelf jaw", (shift-.02, -.036, f.neck+.026), (c.width*.84, c.depth*1.05, .13), .032)
        # A small inlay below the brow, never a full width visor.
        side = -.30 if kind == "shelf" else .35 if c.form in {"steps", "cut", "recess"} else 0
        x, y, z = shift + side*w, -c.depth/2-.005, f.neck+h*.59
        ow = min(c.width*.30, .235)
        ey = .032 if kind != "square" else .047
        drop = .032 if eye == "sly" else 0
        s.slab("Eye inlay", ((x-ow/2, z+ey*.38), (x+ow/2, z+ey*.38-drop),
                           (x+ow*.41, z-ey*.60-drop), (x-ow*.42, z-ey*.60)),
               .014, y=y, bevel=.004, mat=s.bright)
        if eye == "focused":
            s.box("Eye focus", (x+ow*.21, y-.012, z), (.040, .013, ey*.74), .005, s.pupil)

    def torso(self, body_class):
        f, s = FRAMES[body_class], self.shop
        z, top, a, b, l, h = f.hips, f.chest, f.shoulder/2, f.hem/2, f.lean, f.hip_shift
        p = [(h-b-f.sweep, z), (l-a, top-.24), (l-a*.66, top), (l+a*.66, top),
             (l+a, top-.16), (h+b, z+.04)]
        if f.profile == "flared":
            p = [(h-b-f.sweep, z-.17), (h-b*.54, z+.65), (l-a, top-.12),
                 (l-a*.48, top), (l+a*.64, top), (l+a, top-.24),
                 (h+b*.73, z+.06), (h-b*.54, z+.06)]
        elif f.profile == "crossbar":
            p = [(h-b, z), (l-a*.43, top-.42), (l-a, top-.43), (l-a, top-.09),
                 (l-a*.88, top), (l+a*.88, top), (l+a, top-.09), (l+a, top-.43),
                 (l+a*.43, top-.42), (h+b, z)]
        elif f.profile == "bearing":
            p = [(h-b, z), (h-a*.86, z+.36), (l-a, top-.31), (l-a*.87, top),
                 (l+a*.87, top), (l+a, top-.29), (h+a*.89, z+.41), (h+b, z)]
        elif f.profile == "stacked":
            p = [(h-b, z+.18), (h-b, z+.46), (l-a, top-.15), (l-a*.72, top),
                 (l+a*.72, top), (l+a, top-.15), (h+b, z+.46), (h+b, z+.18),
                 (h+b*.72, z), (h-b*.75, z)]
        elif f.profile == "stepped":
            p = [(h-b, z), (h-b, z+.57), (l-a*.84, top-.47), (l-a, top-.13),
                 (l-a*.69, top), (l+a, top), (l+a, top-.33), (l+a*.64, top-.35),
                 (h+b, z+.18)]
        s.slab(f"{body_class.title()} frame", p, f.depth,
               bevel=.108 if f.profile in {"flared", "bearing", "stacked"} else .078)
        if f.profile == "flared":
            s.bar("Long pressed coat seam", (h+b*.29, -f.depth*.508, z+.16),
                  (l+a*.34, -f.depth*.508, top-.16), .036, .015, mat=s.seam)
        if f.profile == "stacked":
            s.box("Horizontal jacket layer", (h, -f.depth*.50, z+.32), (b*1.67, .06, .12), .028, s.seam)

    def legs(self, stance):
        s, f = self.shop, self.frame
        h = f.hip_shift
        if stance == "stride":
            steps = [(-.31, .27, -1.03, .18, 0), (.32, -.18, .98, -.31, 13)]
        elif stance == "brace":
            steps = [(-.48, .34, -1.04, .45, 0), (.50, -.35, 1.05, -.48, 0)]
        elif stance == "approach":
            steps = [(-.23, .21, -.59, .29, 0), (.25, -.23, .57, -.28, 0)]
        else:
            spread = {"sill": .31, "span": .64, "folio": .55, "bow": .37}.get(self.role.frame, .36)
            steps = [(-.23, .19, -spread, .20, 0), (.26, -.20, spread, -.21, 0)]
        foot_width = .52 if stance == "brace" else .40 if stance == "stride" else .38
        for hip, y, foot, fy, tilt in steps:
            ankle = (h+foot, fy, .15 if not tilt else .20)
            knee = (h+(hip+foot)/2+(.04 if stance == "stride" else 0),
                    (y+fy)/2+(-.18 if stance == "brace" else -.05), f.hips*.50)
            s.folded_bar("Long leg bar", ((h+hip, y, f.hips+.13), knee, ankle),
                         (f.limb*1.21, f.limb, f.limb*.89), f.limb*1.14)
            shoe = s.slab("Planted foot" if not tilt else "Leading foot",
                          ((-.135, 0), (foot_width-.13, 0), (foot_width-.13, .07),
                           (.06, .155), (-.113, .186)), f.limb*1.50, bevel=.027)
            shoe.location = (ankle[0]-.02, ankle[1], 0 if not tilt else .063)
            shoe.rotation_euler[1] = radians(-tilt)

    def hand(self, kind, center):
        s = self.shop
        x, y, z = center
        if kind == "clasp":
            s.box("Closed near hand", (x-.07, y-.09, z), (.28, .20, .20), .055, s.seam)
            s.box("Closed far hand", (x+.07, y+.04, z+.035), (.24, .24, .18), .049)
            for i in range(2):
                s.box("Finger seam", (x-.16+i*.07, y-.194, z+.022), (.021, .012, .086), .006)
        elif kind == "palm":
            s.box("Level palm", (x, y, z-.075), (.51, .32, .15), .032)
            s.box("Thumb heel", (x-.13, y+.14, z-.070), (.19, .11, .13), .025)
        elif kind == "bear":
            s.box("Load bearing palm", (x, y, z-.105), (.47, .38, .21), .046)
        elif kind == "stop":
            s.box("Flat stop", (x, y, z+.085), (.15, .37, .41), .046)
        else:
            s.box("Closed hand", center, (.24, .23, .22), .047)

    def arm(self, gesture):
        s, f = self.shop, self.frame
        z, l, reach = f.chest-.19, f.lean, f.shoulder/2
        collar = max(f.depth*.37, .18)
        low = z-.72
        lead, off, kind = (), (), "closed"
        if gesture == "clasp":
            # Both wrists turn behind the coat. The actual near knuckles break the back edge.
            lead = ((l-.12, -collar, z), (-.80, -.23, 2.81), (-.74, -.30, 2.35))
            off = ((l+.11, collar, z), (-.44, .42, 2.78), (-.60, -.04, 2.37))
            kind = "clasp"
        elif gesture == "serve":
            lead = ((.43, -.21, z), (.58, -.23, 2.025), (1.42, -.08, 2.065))
            off = ((-.12, .20, z+.02), (-.66, .23, 2.23), (-.47, .14, 2.00))
            kind = "palm"
        elif gesture == "receive":
            lead = ((-.70, -.51, z), (-.58, -.69, 1.78), (-1.44, -.49, 2.035))
            off = ((-.74, .46, z), (-.98, .44, 1.82), (-1.35, -.12, 2.045))
            kind = "bear"
        elif gesture == "stop":
            lead = ((l+reach*.69, -.23, z), (l+.83, -.23, z), (l+1.28, -.23, z))
            off = ((l-reach*.72, collar, z), (l-.47, collar, low), (l-.40, collar, low-.41))
            kind = "stop"
        elif gesture == "compare":
            lead = ((-.47, -.35, z), (-.79, -.64, low+.05), (-.60, -.89, z-.18))
            off = ((.47, -.32, z), (.79, -.61, low+.08), (.66, -.85, z-.12))
        elif gesture == "inspect":
            lead = ((l+reach*.60, -.28, z), (l+.57, -.41, low+.28), (l+.84, -.41, low+.47))
            off = ((l-reach*.71, collar, z), (l-.33, collar, low+.10), (l-.44, collar, low-.24))
        elif gesture == "fold":
            lead = ((l+reach*.79, -.12, z), (l+reach*.64, -.24, low), (l-.33, -.52, low+.18))
            off = ((l-reach*.79, -.08, z), (l-reach*.66, -.26, low+.04), (l+.32, -.67, low+.37))
        else:  # align: both hands do the same job on the bench
            lead = ((l-reach*.82, -.14, z), (l-.90, -.58, low+.03), (l-.65, -.97, low-.05))
            off = ((l+reach*.82, -.13, z), (l+.91, -.58, low+.03), (l+.65, -.97, low-.05))
        for chain in (off, lead):
            s.folded_bar("Folded arm bar", chain, (f.limb*1.13, f.limb*.92, f.limb*.75), f.limb*1.08)
        if gesture == "clasp":
            self.hand(kind, (-.68, -.21, 2.36))
        elif gesture == "receive":
            for x, y, _ in (lead[-1], off[-1]):
                self.hand(kind, (x, y, 2.15))
        elif gesture == "serve":
            self.hand(kind, (1.42, -.08, 2.15))
            self.hand("closed", off[-1])
        else:
            self.hand(kind, lead[-1])
            self.hand("closed", off[-1])
        if gesture == "compare":
            for x, y, z, angle in ((-.58, -.94, 2.18, -12), (.65, -.89, 2.29, 12)):
                plate = s.box("Reference plate", (x, y, z), (.48, .15, .54), .026, s.bright)
                plate.rotation_euler[1] = radians(angle)

    def build(self, placement=(0, 0, 0), scale=1, angle=0):
        before = set(bpy.context.collection.objects)
        self.legs(self.role.stance)
        self.torso(self.role.frame)
        self.arm(self.role.gesture)
        self.head(self.role.crown, self.role.eye)
        pieces = [obj for obj in bpy.context.collection.objects if obj not in before]
        group = bpy.data.objects.new(self.role.name, None)
        bpy.context.collection.objects.link(group)
        for obj in pieces:
            obj.parent = group
        group.location = placement
        group.scale = (scale,) * 3
        group.rotation_euler[2] = radians(angle)
        return group

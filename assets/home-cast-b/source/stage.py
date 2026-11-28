# Written by tm/frontend (gpt-6.2-sol).
"""Stage the Lilo block cast as two framings of one ensemble."""

import argparse
from dataclasses import replace
from math import atan2, degrees, hypot, radians
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy
from mathutils import Vector

from cast import CAST
from parts import FRAMES
from sculpt import Figure, Shop, material


ROLES = {role.name: role for role in CAST}
# (floor x, depth y, scale, yaw). The forward direction of each rig is -Y.
SHOTS = {
    "wide": (
        (.17, -15.3, .73), (.0, 1, 2.55), 38, (2400, 960),
        {
            "Span": (-6.35, 2.5, .97, 73),
            "Kern": (-3.45, -.40, 1.03, 31),
            "Heft": (-.10, -.85, 1.05, 49),
            "Sill": (2.94, 4.5, 1.12, 170),
            "Ply": (5.64, .98, 1.11, -59),
        },
    ),
    "tall": (
        (.05, -11.7, .61), (0, 1.5, 2.29), 41, (840, 810),
        {
            "Span": (-5.22, 2.88, .89, 88),
            "Kern": (-2.09, -.74, .97, 40),
            "Sill": (-.06, 3.42, 1.12, 179),
            "Heft": (2.05, -.08, .90, 57),
            "Ply": (5.26, 4.44, 1.06, -65),
        },
    ),
}


def point(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, position, target, energy, width, height=None, spread=180):
    bpy.ops.object.light_add(type="AREA", location=position)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.energy = energy
    lamp.data.size = width
    lamp.data.spread = radians(spread)
    if height:
        lamp.data.shape = "RECTANGLE"
        lamp.data.size_y = height
    point(lamp, target)


def room(shop, portal):
    s = shop
    cement = material("Threshold stone", .63, .86)
    floor = s.box("Continuous floor", (0, 3, -.31), (100, 80, .62), 0, cement)
    floor.is_shadow_catcher = True
    x, y = portal
    width, height, depth, pier = 2.54, 5.75, 1.06, .43
    for side in (-1, 1):
        s.box("Threshold return", (x + side*(width+pier)/2, y, height/2),
              (pier, depth, height), .025, cement)
    s.box("Threshold lintel", (x, y, height+.23), (width+2*pier, depth, .46), .025, cement)


def place(shop, positions):
    finishes = {"Span": .032, "Kern": .018, "Heft": .026, "Ply": .036, "Sill": .031}
    rigs = {}
    shop.bright = material("Porcelain inlay", .51, .60)
    shop.seam = material("Structural seam", .064, .60)
    shop.grain(shop.seam, 31, .009)
    poses = {"Span": {"gesture": "fold"}, "Kern": {"gesture": "swing"},
             "Sill": {"stance": "depart", "gesture": "depart"}}
    for name, (x, y, scale, yaw) in positions.items():
        shop.ink = material(f"{name} finish", finishes[name], .61)
        shader = shop.ink.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Metallic"].default_value = .19
        shop.grain(shop.ink, 44, .006)
        role = replace(ROLES[name], **poses.get(name, {}))
        rigs[name] = Figure(shop, role).build((x, y, 0), scale, yaw)

    shop.ink = material("Billet graphite", .14, .58)
    billet = shop.box("Billet in Heft's hands", (-1.39, -.315, 2.295),
                      (.57, .92, .29), .018, shop.ink)
    billet.parent = rigs["Heft"]
    handle = shop.box("Ply's standing tile", (1.42, -.10, 2.50), (.37, .22, .70),
                      .019, shop.seam)
    handle.parent = rigs["Ply"]
    handle.rotation_euler[1] = -.14
    bpy.context.view_layer.update()
    return rigs


def render(key, destination, quick):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 22 if quick else 112
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 7
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 8
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -.24
    scene.world = bpy.data.worlds.new("Fill")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = .095

    position, target, lens, resolution, figures = SHOTS[key]
    shop = Shop()
    sx, sy, _, _ = figures["Sill"]
    portal = (sx+.10, sy+2.0)
    room(shop, portal)
    rigs = place(shop, figures)
    x, y = portal
    area("Hard doorway key", (x, y+.37, 5.20), (.1, -.9, 1.95), 3280, .65, 1.58)
    area("Low side bounce", (-7.9, -4.1, 4.0), (-1.1, 1.7, 2.05), 530, 4.5, spread=105)
    area("Stone return", (x+4.3, y+.55, 7.2), (x, y, 4.0), 1630, 3.7, spread=70)
    bpy.ops.object.camera_add(location=position)
    cam = bpy.context.object
    cam.data.lens = lens
    cam.data.sensor_fit = "HORIZONTAL"
    point(cam, target)
    scene.camera = cam

    hip_min = min(FRAMES[ROLES[name].frame].hips * rig.scale.x for name, rig in rigs.items())
    tilt = Vector(target) - cam.location
    print(f"{key} camera: z={position[2]:.2f}, lowest hip={hip_min:.2f}, "
          f"upward tilt={degrees(atan2(tilt.z, hypot(tilt.x, tilt.y))):.1f}°", flush=True)
    # Measure from each cast member's shoulders, in their own frame.
    for name, rig in rigs.items():
        view = rig.matrix_world.inverted() @ cam.location - Vector((0, 0, 2.55))
        print(f"{key} {name}: yaw={degrees(atan2(view.x, -view.y)):+.1f} "
              f"pitch={degrees(atan2(view.z, hypot(view.x, view.y))):+.1f} "
              f"distance={view.length * rig.scale.x:.1f}", flush=True)

    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 40 if quick else 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(destination / f"{key}.png")
    bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--shot", choices=SHOTS)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    args.destination.mkdir(parents=True, exist_ok=True)
    for key in (args.shot,) if args.shot else SHOTS:
        render(key, args.destination, args.quick)


if __name__ == "__main__":
    main()

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
from sculpt import Figure, Shop, material


ROLES = {role.name: role for role in CAST}
# (floor x, depth y, scale, yaw). The forward direction of each rig is -Y.
SHOTS = {
    "wide": (
        (1.15, -19.6, 2.32), (0, 1, 2.50), 48, (2560, 1024),
        {
            "Span": (-5.90, 4.0, .97, 145),
            "Kern": (-2.95, -.65, .98, 34),
            "Heft": (.05, .28, 1.03, 53),
            "Ply": (3.1, 1.7, 1.13, -51),
            "Sill": (6.44, 5.3, .88, -151),
        },
    ),
    "tall": (
        (.5, -12.3, 2.9), (-.03, 1.2, 2.65), 55, (840, 900),
        {
            "Span": (-4.52, 5.0, .89, 158),
            "Kern": (-1.49, -.72, 1, 37),
            "Heft": (.93, -.63, .89, 51),
            "Ply": (3.34, 4.15, 1.07, -63),
            "Sill": (.44, 6.15, 1.27, -143),
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


def room(shop):
    s = shop
    cement = material("Honed concrete", .34, .78)
    s.grain(cement, 8, .024)
    s.box("Continuous floor", (0, 3, -.31), (100, 80, .62), 0, cement)
    s.box("Raised gallery floor", (0, 13.75, -.055), (39, 21, 1.21), .025, cement)
    s.box("Far wall left", (-12.8, 8.1, 8), (25.0, 1.8, 16), .043, cement)
    s.box("Far wall right", (18.65, 8.1, 8), (27.0, 1.8, 16), .043, cement)
    s.box("Threshold lintel", (2.4, 8.1, 11.4), (5.55, 1.8, 9.2), .043, cement)
    s.box("Return inside the opening", (5.1, 11.65, 4.5), (1.3, 8.4, 9), .04, cement)
    s.box("Far gallery", (0, 17.5, 8), (45, 1, 16), .035, cement)
    s.box("Left return", (-8.5, 4.9, 8), (1.25, 7, 16), .04, cement)


def place(shop, positions):
    finishes = {"Span": .051, "Kern": .013, "Heft": .027, "Ply": .038, "Sill": .023}
    rigs = {}
    shop.bright = material("Porcelain inlay", .29, .52)
    for name, (x, y, scale, yaw) in positions.items():
        shop.ink = material(f"{name} finish", finishes[name], .49)
        shader = shop.ink.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Metallic"].default_value = .16
        shop.grain(shop.ink, 29, .011)
        role = ROLES[name]
        if name == "Span":
            role = replace(role, gesture="fold")
        if name == "Sill":
            role = replace(role, stance="approach")
        rigs[name] = Figure(shop, role).build((x, y, .55 if y >= 3.25 else 0), scale, yaw)

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
    scene.cycles.samples = 12 if quick else 56
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 7
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 8
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = .12
    scene.world = bpy.data.worlds.new("Fill")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = .13

    position, target, lens, resolution, figures = SHOTS[key]
    shop = Shop()
    room(shop)
    rigs = place(shop, figures)
    area("High raking key", (-5.2, -.9, 8.4), (-.3, 1.9, 1.6), 2320, 3.1, 2.5, spread=94)
    area("Portal bounce", (2.2, 10.70, 5.5), (.6, .4, 1.7), 2520, 3, 4.7)
    area("Broad fill", (7.1, -6.8, 6.3), (0, 2, 1.9), 520, 6.5, spread=102)
    area("Far gallery light", (1.4, 13.1, 5.4), (3.05, 17, 3.49), 3180, 3.7)
    bpy.ops.object.camera_add(location=position)
    cam = bpy.context.object
    cam.data.lens = lens
    cam.data.sensor_fit = "HORIZONTAL"
    point(cam, target)
    scene.camera = cam

    # Measure from each cast member's shoulders, in their own frame.
    for name, rig in rigs.items():
        view = rig.matrix_world.inverted() @ cam.location - Vector((0, 0, 2.55))
        print(f"{key} {name}: yaw={degrees(atan2(view.x, -view.y)):+.1f} "
              f"pitch={degrees(atan2(view.z, hypot(view.x, view.y))):+.1f} "
              f"distance={view.length * rig.scale.x:.1f}", flush=True)

    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 40 if quick else 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
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

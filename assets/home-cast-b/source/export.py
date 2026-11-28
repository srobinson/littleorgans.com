# Written by tm/frontend (gpt-6.2-sol).
"""Export the grayscale render as Lilo ink coverage over the site's CSS paper."""

import argparse
from pathlib import Path

from PIL import Image, ImageChops


INK = (0x16, 0x14, 0x0F)
PLATES = (("wide", "wide", None), ("wide", "wide-1440", (1440, 576)), ("tall", "tall", None))
# The shadow catcher dissolves into paper outside the ensemble's footprint.
FLOOR = {"wide": (.81, .94, 1), "tall": (.64, .725, .93)}


def ramp(value):
    t = min(1, max(0, value))
    return t*t*(3-2*t)


def ground_matte(size, side_start, foot_line, shadow_end):
    w, h = size
    def edge(span):
        return Image.frombytes("L", (w, 1), bytes(
            round(255*ramp(min(x, w-1-x)/(span*w))) for x in range(w)
        )).resize(size)

    side = Image.frombytes("L", (1, h), bytes(
        round(255*ramp((y/(h-1)-side_start)/.055)) for y in range(h)
    )).resize(size)
    foreground = Image.frombytes("L", (1, h), bytes(
        round(255*ramp(y/(.025*h))*ramp((shadow_end-y/(h-1))/(shadow_end-foot_line)))
        for y in range(h)
    )).resize(size)
    margin = Image.composite(edge(.045), edge(.02), side)
    return ImageChops.multiply(margin, foreground)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("renders", type=Path)
    parser.add_argument("assets", type=Path)
    args = parser.parse_args()
    for source, name, size in PLATES:
        with Image.open(args.renders / f"{source}.png") as rendered:
            light = rendered.convert("L")
            coverage = light.point(lambda value: round(255 * (1 - min(1, max(0, (value - 10) / 237)))))
            ink_coverage = ImageChops.multiply(coverage, rendered.getchannel("A"))
            if size:
                ink_coverage = ink_coverage.resize(size, Image.Resampling.LANCZOS)
            ink_coverage = ImageChops.multiply(ink_coverage, ground_matte(ink_coverage.size, *FLOOR[source]))
            plate = Image.new("RGBA", ink_coverage.size, INK)
            plate.putalpha(ink_coverage)
            plate.save(args.assets / f"{name}.webp", lossless=True, method=6, exact=True)


if __name__ == "__main__":
    main()

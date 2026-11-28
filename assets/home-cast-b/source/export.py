# Written by tm/frontend (gpt-6.2-sol).
"""Export the grayscale render as Lilo ink coverage over the site's CSS paper."""

import argparse
from pathlib import Path

from PIL import Image


INK = (0x16, 0x14, 0x0F)
PLATES = (("wide", "wide", None), ("wide", "wide-1440", (1440, 576)), ("tall", "tall", None))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("renders", type=Path)
    parser.add_argument("assets", type=Path)
    args = parser.parse_args()
    for source, name, size in PLATES:
        with Image.open(args.renders / f"{source}.png") as rendered:
            light = rendered.convert("L")
            if size:
                light = light.resize(size, Image.Resampling.LANCZOS)
            ink_coverage = light.point(lambda value: round(255 * (1 - min(1, max(0, (value - 10) / 237)))))
            plate = Image.new("RGBA", light.size, INK)
            plate.putalpha(ink_coverage)
            plate.save(args.assets / f"{name}.webp", lossless=True, method=6, exact=True)


if __name__ == "__main__":
    main()

# Written by tm/frontend (gpt-6.2-sol).

"""Cast part library. Dimensions are reusable across the sculpture and rest icon."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Frame:
    hips: float
    chest: float
    neck: float
    shoulder: float
    hem: float
    depth: float
    hip_shift: float = 0
    lean: float = 0
    sweep: float = 0
    limb: float = .22
    profile: str = "upright"


FRAMES = {
    "coat": Frame(1.73, 3.59, 4.36, .68, 1.27, .68, -.08, .22, .38, .21, "flared"),
    "bow": Frame(1.51, 2.83, 3.12, .84, .62, .54, -.31, .27, 0, .22, "pitched"),
    "seat": Frame(1.04, 2.58, 2.76, 2.03, 1.38, 1.26, .06, -.08, 0, .37, "bearing"),
    "span": Frame(1.59, 3.08, 3.25, 2.72, .81, .68, 0, 0, 0, .26, "crossbar"),
    "sill": Frame(1.66, 3.41, 3.65, .77, .64, .69, 0, 0, 0, .21, "upright"),
    "folio": Frame(1.17, 2.54, 2.74, 1.22, 1.50, .93, 0, 0, 0, .25, "stacked"),
    "notch": Frame(1.24, 2.70, 2.87, .99, .86, .75, -.18, .29, 0, .24, "stepped"),
}


@dataclass(frozen=True)
class Crown:
    width: float
    height: float
    depth: float
    form: str


CROWNS = {
    "square": Crown(.73, .49, .61, "cut"),
    "swept": Crown(.89, .53, .52, "steps"),
    "shelf": Crown(.83, .52, .90, "shelf"),
    "lintel": Crown(1.01, .48, .56, "lintel"),
    "pier": Crown(.52, .65, .57, "cut"),
    "wedge": Crown(.73, .50, .58, "wedge"),
    "recess": Crown(.64, .56, .67, "recess"),
}


@dataclass(frozen=True)
class Badge:
    """Black masses plus intentional cuts on the 16px master."""

    masses: tuple
    cuts: tuple = ()
    windows: tuple = ()


# Upper body at rest; two reads in each: the crown and the way the body breaks.
# The 1px joints are cast joints, not partial logo paths.
BADGES = {
    "coat": Badge(((7, 2, 12, 5), (8, 5, 11, 8), (6, 8, 12, 12), (4, 12, 12, 14)),
                  windows=((9, 3, 11, 4),)),
    "bow": Badge(((4, 3, 10, 6), (3, 4, 6, 7), (5, 6, 9, 13), (8, 10, 13, 13)),
                 ((9, 8, 13, 10),), ((6, 4, 9, 5),)),
    "seat": Badge(((5, 3, 11, 6), (2, 6, 14, 12), (3, 12, 13, 13)),
                  cuts=((6, 10, 10, 13),)),
    "span": Badge(((6, 3, 10, 6), (2, 6, 14, 9), (3, 9, 6, 11),
                   (10, 9, 13, 11), (6, 9, 10, 13))),
    "sill": Badge(((4, 2, 8, 6), (4, 6, 9, 14), (9, 6, 12, 9))),
    "folio": Badge(((6, 3, 10, 6), (6, 6, 10, 13), (2, 6, 5, 10), (11, 7, 14, 11),
                    (5, 12, 11, 13))),
    "notch": Badge(((6, 2, 11, 6), (4, 5, 12, 8), (4, 8, 8, 12), (4, 12, 11, 14)),
                   ((9, 6, 12, 7),)),
}


def badge(frame, badge=None):
    return badge if badge is not None else BADGES[frame]

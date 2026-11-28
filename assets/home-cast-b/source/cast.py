# Written by tm/frontend (gpt-6.2-sol).

from dataclasses import dataclass

from parts import Badge


@dataclass(frozen=True)
class Cast:
    key: str
    role: str
    name: str
    frame: str
    crown: str
    stance: str
    gesture: str
    eye: str = "level"
    badge: Badge | None = None


CAST = (
    Cast("lead", "Lead", "Span", "span", "lintel", "planted", "align"),
    Cast("product-owner", "Product owner", "Sill", "sill", "pier", "planted", "stop"),
    Cast("builder", "Builder", "Heft", "seat", "shelf", "brace", "receive"),
    Cast("reviewer", "Reviewer", "Kern", "coat", "square", "stride", "clasp", "focused"),
    Cast("researcher", "Researcher", "Folio", "folio", "wedge", "planted", "compare"),
    Cast("discovery", "Discovery", "Notch", "notch", "recess", "approach", "inspect"),
    Cast("archivist", "Archivist", "Ply", "bow", "swept", "planted", "serve", "sly"),
)

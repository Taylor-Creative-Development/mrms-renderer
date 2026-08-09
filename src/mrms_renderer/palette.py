"""Centralized reflectivity (dBZ) color palette.

This module is the single source of truth for how raw reflectivity values
become RGBA pixels. The current palette is preserved verbatim from the
prototype in ``prototype/WeatherRadarResearch/benchmark_radar.py``; it must
not be changed silently. Any future palette or opacity change must be made
here, reflected in ``tests/test_palette.py``, and documented in README.md.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PaletteEntry:
    """A reflectivity band and its RGBA color."""

    threshold: float
    r: int
    g: int
    b: int
    a: int


# Reflectivity bands, ascending by threshold. Pixels below the lowest
# threshold are fully transparent.
DEFAULT_PALETTE = (
    PaletteEntry(5.0, 80, 180, 255, 150),
    PaletteEntry(10.0, 0, 220, 120, 180),
    PaletteEntry(20.0, 0, 170, 0, 200),
    PaletteEntry(30.0, 255, 200, 0, 220),
    PaletteEntry(40.0, 255, 80, 0, 230),
    PaletteEntry(50.0, 255, 0, 0, 240),
)

TRANSPARENT = (0, 0, 0, 0)


def color_values(dbz: np.ndarray, palette: tuple[PaletteEntry, ...] = DEFAULT_PALETTE) -> np.ndarray:
    """Convert a 1-D array of dBZ values into an Nx4 uint8 RGBA array.

    Vectorized; mirrors the benchmark implementation. Each palette band is
    applied in ascending threshold order so later bands overwrite earlier
    ones, preserving the prototype's threshold table.
    """
    rgba = np.zeros((dbz.size, 4), dtype=np.uint8)
    for entry in palette:
        rgba[dbz >= entry.threshold] = (entry.r, entry.g, entry.b, entry.a)
    return rgba
"""Render decoded radar grids into transparent RGBA PNG frames.

The vectorized approach from the prototype is preserved: a flat RGBA array
is built in one pass with NumPy, reshaped to the grid, and encoded via
Pillow. Transparency comes from the palette (values below the lowest
threshold are fully transparent).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from mrms_renderer.decode import DecodedGrid
from mrms_renderer.palette import color_values


class RenderError(RuntimeError):
    """Raised when a radar frame cannot be rendered."""


def render_rgba(grid: DecodedGrid) -> np.ndarray:
    """Build an ``(nj, ni, 4)`` uint8 RGBA image from a decoded grid."""
    rgba = color_values(grid.values)
    return rgba.reshape((grid.nj, grid.ni, 4))


def save_png(grid: DecodedGrid, path: Path) -> Path:
    """Render a grid and save a transparent PNG frame."""
    try:
        image = Image.fromarray(render_rgba(grid), mode="RGBA")
        image.save(path, format="PNG")
    except (ValueError, OSError) as exc:
        raise RenderError(f"Failed to render {path}: {exc}") from exc
    return path
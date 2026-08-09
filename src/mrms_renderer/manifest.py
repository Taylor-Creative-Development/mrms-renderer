"""Frame manifest generation.

The manifest is a machine-readable JSON document with one entry per rendered
frame, ordered oldest-first (ascending in time). The viewer consumes this
manifest to animate the sequence in chronological order.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from mrms_renderer.decode import DecodedGrid


class ManifestError(RuntimeError):
    """Raised when a manifest cannot be written."""


@dataclass(frozen=True)
class FrameEntry:
    filename: str
    file: str
    valid_time: str
    ni: int
    nj: int
    bounds: dict[str, float]


def build_entry(decoded: DecodedGrid, png_rel_path: Path) -> FrameEntry:
    """Build a manifest entry for one decoded, rendered frame."""
    return FrameEntry(
        filename=png_rel_path.name,
        file=str(png_rel_path),
        valid_time=decoded.valid_time.strftime("%Y-%m-%dT%H:%M:%S"),
        ni=decoded.ni,
        nj=decoded.nj,
        bounds=decoded.bounds,
    )


def write_manifest(entries: list[FrameEntry], path: Path) -> Path:
    """Write the manifest as oldest-first chronological JSON."""
    entries_sorted = sorted(entries, key=lambda entry: entry.valid_time)
    payload = {"frames": [asdict(entry) for entry in entries_sorted]}
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        raise ManifestError(f"Failed to write manifest {path}: {exc}") from exc
    return path
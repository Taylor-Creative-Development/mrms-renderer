"""Tests for manifest generation and ordering."""

import json
from datetime import datetime
from pathlib import Path

from mrms_renderer.decode import DecodedGrid
from mrms_renderer.manifest import FrameEntry, build_entry, write_manifest


def make_entry(valid: str, png: str) -> FrameEntry:
    grid = DecodedGrid(
        ni=4,
        nj=3,
        values=[],
        valid_time=datetime.fromisoformat(valid),
        bounds={"south": 20.0, "north": 50.0, "west": -130.0, "east": -60.0},
    )
    return build_entry(grid, Path(png))


def json_load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_written_chronological(tmp_path):
    entries = [
        make_entry("2026-08-08T02:00:40", "frames/frame_20260808-020040.png"),
        make_entry("2026-08-08T02:02:40", "frames/frame_20260808-020240.png"),
        make_entry("2026-08-08T02:05:00", "frames/frame_20260808-020500.png"),
    ]
    path = tmp_path / "frames.json"
    write_manifest(entries, path)

    data = json_load(path)
    times = [frame["valid_time"] for frame in data["frames"]]
    assert times == sorted(times)
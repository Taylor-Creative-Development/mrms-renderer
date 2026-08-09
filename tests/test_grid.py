"""Tests for ecCodes-based decoding, bounds computation, and grid handling."""

from datetime import UTC, datetime

import numpy as np
import pytest

from mrms_renderer.decode import DecodedGrid, _as_degrees, _bounds


def test_as_degrees_passthrough():
    assert _as_degrees(40.50) == pytest.approx(40.50)
    assert _as_degrees(-60.5) == pytest.approx(-60.5)


def test_as_degrees_converts_microdegrees():
    assert _as_degrees(20006102) == pytest.approx(20.006102)
    assert _as_degrees(-129988000) == pytest.approx(-129.988)


def test_bounds_from_corners_degrees():
    assert _bounds(20.0, 50.0, -130.0, -60.0) == {
        "south": 20.0,
        "north": 50.0,
        "west": -130.0,
        "east": -60.0,
    }


def test_bounds_handle_microdegree_grid():
    bounds = _bounds(20006102, 50006102, -130047000, -57988000)
    assert bounds["south"] == pytest.approx(20.006102)
    assert bounds["north"] == pytest.approx(50.006102)
    assert bounds["east"] == pytest.approx(-57.988)


def test_bounds_normalize_360_to_180_longitudes():
    # MRMS CONUS stores longitudes in 0..360 as microdegree integers.
    bounds = _bounds(20.005, 54.995, 230005000, 299995000)
    assert bounds["west"] == pytest.approx(-129.995)
    assert bounds["east"] == pytest.approx(-60.005)


class _FakeId:
    """A stand-in for an ecCodes handle."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_valid_time_reads_with_hourless_time(monkeypatch):
    from mrms_renderer import decode

    gid = _FakeId(dataDate=20260808, hour=0, minute=0, second=0)
    monkeypatch.setattr(decode, "codes_get", lambda handle, key: getattr(handle, key))
    assert decode._valid_time(gid) == datetime(2026, 8, 8, 0, 0, 0, tzinfo=UTC)


def test_valid_time_reads_normal_time(monkeypatch):
    from mrms_renderer import decode

    gid = _FakeId(dataDate=20260808, hour=4, minute=26, second=41)
    monkeypatch.setattr(decode, "codes_get", lambda handle, key: getattr(handle, key))
    assert decode._valid_time(gid) == datetime(2026, 8, 8, 4, 26, 41, tzinfo=UTC)


def test_decoded_grid_round_trip():
    grid = DecodedGrid(
        ni=4,
        nj=3,
        values=np.arange(12, dtype=np.float64),
        valid_time=datetime(2026, 8, 8, 4, 26, 41, tzinfo=UTC),
        bounds={"south": 20.0, "north": 50.0, "west": -130.0, "east": -60.0},
    )
    assert grid.values.shape == (12,)


def test_render_rgba_shape_and_transparency():
    from mrms_renderer.render import render_rgba

    grid = DecodedGrid(
        ni=4,
        nj=3,
        values=np.array([0.0, 4.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 0.0, 60.0, 6.0, 15.0]),
        valid_time=datetime(2026, 8, 8, 4, 26, 41, tzinfo=UTC),
        bounds={"south": 20.0, "north": 50.0, "west": -130.0, "east": -60.0},
    )
    image = render_rgba(grid)
    assert image.shape == (3, 4, 4)
    assert image.dtype == np.uint8
    # Below the lowest threshold stays transparent.
    assert (image[0, 0] == (0, 0, 0, 0)).all()
    assert (image[0, 1] == (0, 0, 0, 0)).all()
    # 5 dBZ boundary should be the light blue band.
    assert (image[0, 2] == (80, 180, 255, 150)).all()
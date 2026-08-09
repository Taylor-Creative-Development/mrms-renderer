"""Tests for MRMS frame discovery."""

from datetime import UTC, datetime

import pytest

from mrms_renderer.discovery import parse_listing

# A typical Apache auto-index listing from mrms.ncep.noaa.gov.
LISTING = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html><head><title>Index of /2D/ReflectivityAtLowestAltitude</title></head><body>
<h1>Index of /2D/ReflectivityAtLowestAltitude</h1>
  <table>
   <tr><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size</a></th></tr>
   <tr><th colspan="3"><hr></th></tr>
<tr><td><a href="/2D/">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td></tr>
<tr><td><a href="MRMS_ReflectivityAtLowestAltitude.latest.grib2.gz">MRMS_ReflectivityAtLowestAltitude.latest.grib2.gz</a></td><td align="right">09-Aug-2026 02:28  </td><td align="right">552K</td></tr>
<tr><td><a href="MRMS_ReflectivityAtLowestAltitude_00.50_20260809-022641.grib2.gz">MRMS_ReflectivityAtLowestAltitude_00.50_20260809-022641.grib2.gz</a></td><td align="right">minus text</td><td align="right">551K</td></tr>
<tr><td><a href="MRMS_ReflectivityAtLowestAltitude_00.50_20260809-022441.grib2.gz">MRMS_ReflectivityAtLowestAltitude_00.50_20260809-022441.grib2.gz</a></td><td align="right">08-Aug-2026 02:46  </td><td align="right">552K</td></tr>
<tr><td><a href="MRMS_ReflectivityAtLowestAltitude_00.50_20260808-020040.grib2.gz">MRMS_ReflectivityAtLowestAltitude_00.50_20260808-020040.grib2.gz</a></td><td align="right">08-Aug-2026 02:02  </td><td align="right">567K</td></tr>
<tr><td><a href="MRMS_ReflectivityAtLowestAltitude_00.50_20260808-020040.grib2.gz?x=1">MRMS_ReflectivityAtLowestAltitude_00.50_20260808-020044.grib2.gz</a></td><td align="right">08-Aug-2026 02:02  </td><td align="right">567K</td></tr>
</table></body></html>
"""


def test_parse_lists_timestamped_frames_only():
    frames = parse_listing(LISTING)
    names = [frame.filename for frame in frames]
    assert "MRMS_ReflectivityAtLowestAltitude.latest.grib2.gz" not in names
    assert "Parent Directory" not in names
    assert all(name.endswith(".grib2.gz") for name in names)


def test_parse_rejects_non_timestamped_entries():
    text = '<a href="MRMS_ReflectivityAtLowestAltitude.latest.grib2.gz">x</a>'
    assert parse_listing(text) == []


def test_frames_are_oldest_first():
    frames = parse_listing(LISTING)
    assert frames == sorted(frames, key=lambda f: f.valid_time)


def test_frame_timestamp_is_parsed():
    frame = parse_listing(LISTING)[0]
    assert frame.valid_time == datetime(2026, 8, 8, 2, 0, 40, tzinfo=UTC)


def test_newest_frame_last():
    frames = parse_listing(LISTING)
    assert frames[-1].filename == "MRMS_ReflectivityAtLowestAltitude_00.50_20260809-022641.grib2.gz"


def test_discover_returns_newest_first_up_to_limit(monkeypatch):
    from mrms_renderer import discovery

    monkeypatch.setattr(discovery, "fetch_listing_text", lambda url: LISTING)
    result = discovery.discover(limit=2)
    assert [frame.filename for frame in result] == [
        "MRMS_ReflectivityAtLowestAltitude_00.50_20260809-022641.grib2.gz",
        "MRMS_ReflectivityAtLowestAltitude_00.50_20260809-022441.grib2.gz",
    ]


def test_discover_raises_on_empty_listing(monkeypatch):
    from mrms_renderer import discovery

    monkeypatch.setattr(discovery, "fetch_listing_text", lambda url: "<html></html>")
    with pytest.raises(discovery.DiscoveryError):
        discovery.discover(limit=30)
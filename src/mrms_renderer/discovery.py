"""Discovery of recent NOAA MRMS ReflectivityAtLowestAltitude frames.

The NCEP MRMS server exposes an Apache auto-index directory listing at
``https://mrms.ncep.noaa.gov/2D/ReflectivityAtLowestAltitude/``. Each
timestamped product is named::

    MRMS_ReflectivityAtLowestAltitude_00.50_YYYYMMDD-HHMMSS.grib2.gz

A special ``.latest.grib2.gz`` file is also present and is excluded because
it carries no timestamp.

Discovery returns the most recent ``limit`` frames ordered newest-first.
"""

from __future__ import annotations

import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime

PRODUCT = "ReflectivityAtLowestAltitude"
LISTING_URL = f"https://mrms.ncep.noaa.gov/2D/{PRODUCT}/"

# MRMS_ReflectivityAtLowestAltitude_00.50_20260808-020040.grib2.gz
_FILENAME_RE = re.compile(
    rf"^MRMS_{PRODUCT}_(\d{{2}}\.\d{{2}})_(\d{{8}})-(\d{{6}})\.grib2\.gz$"
)


class DiscoveryError(RuntimeError):
    """Raised when the NOAA MRMS listing cannot be discovered."""


@dataclass(frozen=True)
class Frame:
    """A single discoverable MRMS frame."""

    filename: str
    url: str
    valid_time: datetime


def parse_listing(text: str) -> list[Frame]:
    """Extract timestamped frames from the raw listing HTML.

    Only filenames matching the timestamped ``.grib2.gz`` pattern are
    retained; ``MRMS_...latest.grib2.gz`` and any non-product entries are
    ignored. Returns frames sorted oldest-first.
    """
    frames: list[Frame] = []
    for href in re.findall(r'href="([^"]+)"', text):
        name = href.rsplit("/", 1)[-1]
        match = _FILENAME_RE.match(name)
        if not match:
            continue
        date_part = match.group(2)
        time_part = match.group(3)
        valid_time = datetime(
            int(date_part[0:4]),
            int(date_part[4:6]),
            int(date_part[6:8]),
            int(time_part[0:2]),
            int(time_part[2:4]),
            int(time_part[4:6]),
            tzinfo=UTC,
        )
        frames.append(Frame(filename=name, url=f"{LISTING_URL}{name}", valid_time=valid_time))
    return sorted(frames, key=lambda frame: frame.valid_time)


def fetch_listing_text(url: str = LISTING_URL) -> str:
    """Download the raw directory listing from NOAA/NCEP."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "mrms-renderer/0.1 (open source radar visualizer)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise DiscoveryError(f"Failed to fetch MRMS listing from {url}: {exc}") from exc


def discover(url: str = LISTING_URL, limit: int = 30) -> list[Frame]:
    """Return up to ``limit`` most recent frames, newest-first.

    The NOAA listing is chronological ascending; this returns the tail of
    that ordering, reversed, so the newest frame is first.
    """
    frames = parse_listing(fetch_listing_text(url))
    if not frames:
        raise DiscoveryError(f"No timestamped {PRODUCT} frames found at {url}")
    return list(reversed(frames[-limit:]))

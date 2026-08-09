"""ecCodes-based decoding of MRMS GRIB2 radar grids.

Each decoded frame carries the grid dimensions, the flat data values, the
valid time (UTC), and the geographic bounds derived from the GRIB master
grid metadata (no hardcoded CONUS box is assumed).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from eccodes import codes_get, codes_get_values, codes_grib_new_from_file, codes_release


class DecodeError(RuntimeError):
    """Raised when a GRIB2 file cannot be decoded."""


def _as_degrees(value: float) -> float:
    """Convert an ecCodes angle to degrees regardless of source unit."""
    if value > 180 or value < -180:
        return value / 1e6
    return float(value)


def _normalized_longitude(value: float) -> float:
    """Map a longitude to the standard -180..180 range."""
    degrees = _as_degrees(value)
    return degrees - 360.0 if degrees > 180.0 else degrees


def _bounds(
    lat_first: float,
    lat_last: float,
    lon_first: float,
    lon_last: float,
) -> dict[str, float]:
    """Compute a southwest/northeast box from the grid corner metadata."""
    latitude = [_as_degrees(lat_first), _as_degrees(lat_last)]
    longitude = [_normalized_longitude(lon_first), _normalized_longitude(lon_last)]
    # A regular MRMS lat/lon grid spans the box of its corner points.
    return {
        "south": min(latitude),
        "north": max(latitude),
        "west": min(longitude),
        "east": max(longitude),
    }


def _valid_time(gid) -> datetime:
    day = int(codes_get(gid, "dataDate"))
    hour = int(codes_get(gid, "hour"))
    minute = int(codes_get(gid, "minute"))
    second = int(codes_get(gid, "second"))
    year = day // 10000
    month = (day // 100) % 100
    day_of_month = day % 100
    return datetime(year, month, day_of_month, hour, minute, second, tzinfo=UTC)


@dataclass(frozen=True)
class DecodedGrid:
    ni: int
    nj: int
    values: np.ndarray
    valid_time: datetime
    bounds: dict[str, float]


def read_grid(path: Path) -> DecodedGrid:
    """Load one GRIB2 file and return its decoded grid."""
    try:
        with path.open("rb") as source:
            gid = codes_grib_new_from_file(source)
            if gid is None:
                raise DecodeError(f"No GRIB message found in {path}")
            try:
                ni = int(codes_get(gid, "Ni"))
                nj = int(codes_get(gid, "Nj"))
                values = np.array(codes_get_values(gid), dtype=np.float64)
                valid_time = _valid_time(gid)
                bounds = _bounds(
                    codes_get(gid, "latitudeOfFirstGridPoint"),
                    codes_get(gid, "latitudeOfLastGridPoint"),
                    codes_get(gid, "longitudeOfFirstGridPoint"),
                    codes_get(gid, "longitudeOfLastGridPoint"),
                )
            finally:
                codes_release(gid)
    except OSError as exc:
        raise DecodeError(f"Failed to read {path}: {exc}") from exc

    if values.size != ni * nj:
        raise DecodeError(
            f"Grid size mismatch in {path.name}: {ni}x{nj} expects {ni * nj} values, got {values.size}"
        )
    return DecodedGrid(ni=ni, nj=nj, values=values, valid_time=valid_time, bounds=bounds)
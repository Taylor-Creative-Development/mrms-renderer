"""Download and decompress MRMS GRIB2 files from NOAA/NCEP.

These helpers work with ``.grib2.gz`` sources and produce decompressed
``.grib2`` files locally inside the (git-ignored) output directory.
"""

from __future__ import annotations

import gzip
import shutil
import urllib.error
import urllib.request
from pathlib import Path


class DownloadError(RuntimeError):
    """Raised when a GRIB2 download or decompression fails."""


def download_gzip(url: str, dest_dir: Path) -> Path:
    """Download a GRIB2 file from a gzipped URL.

    Returns the path to the downloaded ``.grib2.gz`` file.
    """
    filename = url.rsplit("/", 1)[-1]
    dest_path = dest_dir / filename
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "mrms-renderer/0.1 (open source radar visualizer)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response, dest_path.open(
            "wb"
        ) as target:
            shutil.copyfileobj(response, target)
    except urllib.error.URLError as exc:
        raise DownloadError(f"Failed to download {url}: {exc}") from exc
    return dest_path


def decompress_gzip(gzip_path: Path, dest_dir: Path) -> Path:
    """Decompress a ``.grib2.gz`` file into a ``.grib2`` file.

    Returns the path to the decompressed file.
    """
    if not gzip_path.name.endswith(".grib2.gz"):
        raise DownloadError(f"Expected a .grib2.gz file, got {gzip_path.name}")
    dest_path = dest_dir / gzip_path.name[: -len(".gz")]
    with gzip.open(gzip_path, "rb") as source, dest_path.open("wb") as target:
        shutil.copyfileobj(source, target)
    return dest_path
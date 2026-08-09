# MRMS Renderer

**MRMS Renderer** is an open-source tool for retrieving, rendering, and
visualizing NOAA Multi-Radar/Multi-Sensor (MRMS) radar data locally.

It turns recent NOAA `ReflectivityAtLowestAltitude` GRIB2 files into
transparent PNG frames, writes a chronological frame manifest, and animates
the sequence over an OpenStreetMap-based interactive map in the browser.

## Requirements

- Python 3.11+
- [ecCodes](https://confluence.ecmwf.int/display/UDOC/ecCodes+Home)
  (with Python bindings installed via `pip install eccodes` or your package
  manager)
- NumPy and Pillow (installed automatically)

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Usage

The CLI runs the full local workflow and never touches a hosted radar
service — every byte is fetched from NOAA/NCEP.

| Command | What it does |
| --- | --- |
| `mrms-renderer discover` | Lists up to 30 recent MRMS frames from the NOAA/NCEP index, newest first. |
| `mrms-renderer frames` | Full pipeline: download → decompress → decode (ecCodes) → render (NumPy/Pillow) → `output/frames.json`. |
| `mrms-renderer view` | Serves `output/` and opens the browser viewer. |
| `mrms-renderer demo` | Runs `frames` then `view`: complete 30-frame pipeline + animated map. |

Common options are `--count N` (default 30) and `--output/-o PATH`
(default `./output`).

### The happy path

```sh
mrms-renderer demo
```

This downloads up to 30 recent reflectivity frames, decompresses and decodes
them with ecCodes, renders transparent RGBA PNGs with NumPy and Pillow, writes
the chronological manifest, and opens a local interactive map. Press
play/pause, scrub the timeline, and change playback speed.

Output is written to the git-ignored `output/` directory:

```
output/
  download/         *.grib2.gz
  decompressed/     *.grib2
  frames/           frame_YYYYMMDD-HHMMSS.png
  frames.json       chronological manifest
  index.html        local viewer (installed automatically)
```

## Products

The v0.1 release is scoped to NOAA's `ReflectivityAtLowestAltitude` product.
Frames are discovered from
`https://mrms.ncep.noaa.gov/2D/ReflectivityAtLowestAltitude/`, which lists
`MRMS_ReflectivityAtLowestAltitude_00.50_YYYYMMDD-HHMMSS.grib2.gz` files.

## Reflectivity palette

The palette is centralized in `src/mrms_renderer/palette.py` and preserved
unchanged from the prototype pipeline. dBZ values below `5.0` are fully
transparent.

| dBZ | RGBA |
| --- | --- |
| ≥ 5.0 | `(80, 180, 255, 150)` |
| ≥ 10.0 | `(0, 220, 120, 180)` |
| ≥ 20.0 | `(0, 170, 0, 200)` |
| ≥ 30.0 | `(255, 200, 0, 220)` |
| ≥ 40.0 | `(255, 80, 0, 230)` |
| ≥ 50.0 | `(255, 0, 0, 240)` |

Any future palette or opacity change must be made in `palette.py`, covered by
`tests/test_color.py`, and documented here.

## Testing and linting

```sh
pytest
ruff check src tests
```

Tests cover the palette bands, frame discovery/parsing, grid decoding
(including bounds derivation from GRIB metadata), rendering output, and
manifest ordering.

## Architecture

```text
NOAA MRMS index
    ↓
discover  (mrms_renderer/discovery.py)
    ↓
download + decompress  (mrms_renderer/download.py)
    ↓
ecCodes decode  (mrms_renderer/decode.py)
    ↓
NumPy → RGBA → Pillow PNG  (mrms_renderer/render.py)
    ↓
frames.json manifest  (mrms_renderer/manifest.py)
    ↓
JavaScript viewer animation  (web/)
```

## What this project is not

MRMS Renderer is not a hosted radar service, processed radar feed,
commercial API, weather forecast service, or production framework. It
includes none of Taylor Creative Development's private production
infrastructure: no scheduling, cloud deployment, WeatherKit integration,
CDN, databases, or authentication. Users retrieve and process NOAA data
themselves.

## Data attribution

Radar data is provided by NOAA through the Multi-Radar/Multi-Sensor (MRMS)
system. Map tiles are &copy; OpenStreetMap contributors (ODbL).

## License

Apache License 2.0. See `LICENSE`.

MRMS Renderer is developed by **Taylor Creative Development**.
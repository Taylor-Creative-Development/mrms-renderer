# MRMS Renderer

**MRMS Renderer** is an open-source project for retrieving, rendering, and visualizing NOAA Multi-Radar/Multi-Sensor (MRMS) radar data.

The project is focused on turning current 2D MRMS radar products into application-friendly visual output, including animated radar layers for web mapping interfaces.

## Project goals

MRMS Renderer aims to make it straightforward for developers to:

- retrieve recent NOAA MRMS radar files directly from NOAA/NCEP sources;
- decode MRMS GRIB2 data locally;
- transform radar reflectivity values into transparent rendered imagery;
- generate a time-ordered sequence of radar frames;
- visualize and animate those frames over an interactive map.

The initial public release will focus on NOAA's `ReflectivityAtLowestAltitude` product and a local browser-based demonstration.

## What this project is not

MRMS Renderer is not a hosted radar service, processed radar feed, commercial API, weather forecast service, or production deployment framework.

It intentionally does **not** include Taylor Creative Development's private production infrastructure, scheduling systems, cloud deployment architecture, WeatherKit integration, CDN strategy, or Weather Experience application code.

Users retrieve and process NOAA data themselves.

## Planned v0.1 scope

- Retrieve up to 30 recent MRMS `ReflectivityAtLowestAltitude` frames
- Decode GRIB2 using ecCodes
- Process radar data with NumPy
- Render transparent PNG frames
- Generate a frame manifest
- Display radar over an OpenStreetMap-based map
- Animate the radar sequence with basic playback controls
- Provide a clean local setup and command-line workflow

## Architecture

```text
NOAA MRMS
    ↓
GRIB2 download
    ↓
ecCodes
    ↓
NumPy radar grid
    ↓
RGBA rendering
    ↓
PNG frames + manifest
    ↓
JavaScript map viewer
    ↓
Animated radar overlay
```

## Status

MRMS Renderer is currently being prepared for its first public release.

## Related work

NASA's [MMM-Py](https://github.com/nasa/MMM-Py) is a scientific toolkit for ingesting, analyzing, and visualizing MRMS radar mosaics, particularly 3D radar-volume workflows. MRMS Renderer is independently implemented and focuses on lightweight rendering of current 2D MRMS products for animated application and web-map visualization.

## Data attribution

Radar data is provided by the National Oceanic and Atmospheric Administration (NOAA) through the Multi-Radar/Multi-Sensor (MRMS) system.

Map data and tiles used by the demonstration viewer will follow the applicable OpenStreetMap attribution requirements.

## License

A project license will be selected before the first public release.

---

MRMS Renderer is developed by **Taylor Creative Development**.

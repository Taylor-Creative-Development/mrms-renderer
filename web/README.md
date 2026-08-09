# MRMS Renderer Web Viewer

Local, browser-based visualization of MRMS radar frames for MRMS Renderer v0.1.

The viewer:

- reads the locally generated `frames.json` manifest (chronological order);
- displays radar imagery over an OpenStreetMap-based interactive map;
- animates the frame sequence with play/pause, a timeline scrubber, and
  playback-speed controls;
- derives the geographic bounds for the overlay from the GRIB2 grid metadata
  recorded in the manifest (no hardcoded box).

It never connects to a Taylor Creative Development hosted feed or production
API — all data is fetched by the local `mrms-renderer` pipeline.

## Running

The viewer is served automatically by the CLI. See the top-level `README.md`:

```sh
mrms-renderer demo
```

When `frames` or `demo` run, a copy of `index.html`, `viewer.js`, and
`viewer.css` is installed into the (git-ignored) output directory so the
local static file server has everything it needs.

## Attribution

- Map tiles: &copy; OpenStreetMap contributors (ODbL).
- Radar data: NOAA Multi-Radar/Multi-Sensor (MRMS) system.
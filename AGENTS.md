# MRMS Renderer Agent Instructions

## Product definition

MRMS Renderer is a finished open-source developer tool for retrieving current
NOAA MRMS radar data, processing it locally, rendering it into
application-friendly imagery, and viewing an animated sequence over an
interactive map.

## v0.1 target

The first public release must support this end-to-end local workflow:

1. Discover up to 30 recent NOAA MRMS `ReflectivityAtLowestAltitude` frames.
2. Download the source GRIB2 files directly from NOAA/NCEP.
3. Decompress and decode them using ecCodes.
4. Convert the radar grid to an RGBA image using NumPy.
5. Encode transparent PNG frames using Pillow.
6. Generate a machine-readable frame manifest in chronological order.
7. Serve or open a local JavaScript viewer.
8. Display the radar imagery over an OpenStreetMap-based interactive map.
9. Animate the frame sequence with basic play/pause, timeline, and playback-speed controls.

## Preserve the working technical direction

The proven processing stack is:

- Python
- ecCodes
- NumPy
- Pillow

Do not replace these merely for stylistic reasons. Refactor only when it improves reliability, packaging, testability, portability, or clarity.

## Public scope boundaries

Keep changes focused on functionality documented in this repository. Do not
introduce unrelated product, service, or infrastructure concerns without an
explicit project decision.

Proprietary Taylor Creative Development products, services, infrastructure,
and implementation details are outside the scope of this repository and must
not be described or inferred in public project documentation.

## Data behavior

Generated GRIB2, NetCDF, PNG, and other radar output files must not be committed to Git. They should be generated locally into an ignored output directory.

## Development approach

- Prefer small, understandable modules over a large monolithic script.
- Keep data acquisition, decoding, rendering, manifest generation, and browser visualization separate.
- Preserve geographic correctness.
- Do not silently change the radar palette or reflectivity thresholds without documenting the change.
- Add tests for parsing, frame discovery, grid handling, rendering output, and manifest generation.
- Avoid speculative abstractions for unsupported future radar products.
- Keep setup straightforward for a developer cloning the repository for the first time.

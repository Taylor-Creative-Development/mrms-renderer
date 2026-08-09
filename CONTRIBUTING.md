# Contributing to MRMS Renderer

Thanks for your interest in MRMS Renderer.

MRMS Renderer is focused on retrieving, rendering, and visualizing NOAA MRMS radar data locally. Contributions that improve correctness, performance, portability, documentation, testing, visualization quality, or developer experience are welcome.

## Before contributing

Please keep the project's scope boundaries in mind. MRMS Renderer is not intended to provide hosted radar imagery, a production radar API, cloud deployment infrastructure, or Weather Experience application code.

## Development setup

The intended development workflow is:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

The public CLI and browser demo are under active development for the first release.

## Pull requests

Please keep pull requests focused and explain:

- what problem the change solves;
- how the change was tested;
- whether radar output, geographic behavior, dependencies, or public interfaces change.

For rendering changes, include before/after examples when practical.

## Generated data

Do not commit downloaded MRMS GRIB2 files, generated radar frames, or other large runtime artifacts. The repository's `.gitignore` excludes these outputs.

## NOAA and third-party data

Contributions must respect NOAA data attribution and the attribution/license requirements of any map or third-party resources used by the demo.

## Prior art and copied code

MRMS Renderer is independently implemented. Do not copy code from projects with incompatible or additional licensing obligations into this repository without explicit discussion and approval.

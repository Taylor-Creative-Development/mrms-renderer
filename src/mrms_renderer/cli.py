"""Command-line interface for MRMS Renderer.

Subcommands:
    discover   List recent NOAA MRMS frames (newest first).
    frames     Run the full local pipeline: discover, download, decompress,
               decode, render, manifest.
    view       Serve an existing output directory and open the viewer.
    demo       Run ``frames`` then open the viewer (the happy path).
"""

from __future__ import annotations

import argparse
import functools
import http.server
import shutil
import sys
import webbrowser
from pathlib import Path

from mrms_renderer.decode import DecodeError, read_grid
from mrms_renderer.discovery import DiscoveryError, discover
from mrms_renderer.download import DownloadError, decompress_gzip, download_gzip
from mrms_renderer.manifest import FrameEntry, ManifestError, build_entry, write_manifest
from mrms_renderer.render import RenderError, save_png

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


class WorkflowError(RuntimeError):
    """Raised when the local pipeline cannot complete."""


def _install_web_assets(output_dir: Path) -> None:
    """Copy the browser viewer into the (git-ignored) output directory."""
    web_dir = PROJECT_ROOT / "web"
    for name in ("index.html", "viewer.js", "viewer.css"):
        source = web_dir / name
        if source.exists():
            shutil.copyfile(source, output_dir / name)


def run_frames(output_dir: Path, count: int) -> tuple[list[str], Path]:
    """Discover, download, decompress, decode, render, and manifest frames."""
    if count <= 0:
        raise WorkflowError("--count must be a positive integer")
    downloads_dir = output_dir / "download"
    decompressed_dir = output_dir / "decompressed"
    frames_dir = output_dir / "frames"
    for directory in (downloads_dir, decompressed_dir, frames_dir):
        directory.mkdir(parents=True, exist_ok=True)

    discovered = discover(limit=count)
    entries: list[FrameEntry] = []
    produced: list[str] = []
    total = len(discovered)
    for index, frame in enumerate(discovered, start=1):
        try:
            gzip_path = download_gzip(frame.url, downloads_dir)
            grib2_path = decompress_gzip(gzip_path, decompressed_dir)
            decoded = read_grid(grib2_path)
            png_name = f"frame_{frame.valid_time:%Y%m%d-%H%M%S}.png"
            png_path = save_png(decoded, frames_dir / png_name)
            entries.append(build_entry(decoded, Path("frames") / png_name))
            produced.append(str(png_path))
            print(f"  [{index}/{total}] {frame.filename} -> {png_path.name}")
        except (DownloadError, DecodeError, RenderError) as exc:
            print(f"  [{index}/{total}] FAILED {frame.filename}: {exc}", file=sys.stderr)

    if not produced:
        raise WorkflowError("No frames could be produced; wrote nothing.")
    manifest_path = write_manifest(entries, output_dir / "frames.json")
    _install_web_assets(output_dir)
    return produced, manifest_path


def run_view(output_dir: Path, port: int, open_browser: bool) -> int:
    """Serve the output directory over local HTTP and open the viewer."""
    _install_web_assets(output_dir)
    manifest_path = output_dir / "frames.json"
    if not manifest_path.exists():
        print(
            f"The manifest {manifest_path} was not found; run `mrms-renderer frames` first.",
            file=sys.stderr,
        )
        return 1

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(output_dir)
    )
    url = f"http://localhost:{port}/"
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Serving {output_dir} at {url}")
        print("Press Ctrl+C to stop.")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mrms-renderer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("discover", help="List recent upstream MRMS frames.")
    p.add_argument("--count", type=int, default=30, help="How many frames to list.")
    p.set_defaults(func=cmd_discover)

    p = subparsers.add_parser("frames", help="Run the full local pipeline.")
    p.add_argument("--count", type=int, default=30)
    p.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.set_defaults(func=cmd_frames)

    p = subparsers.add_parser("view", help="Serve the rendered output and open the viewer.")
    p.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(func=cmd_view)

    p = subparsers.add_parser(
        "demo", help="Run the full 30-frame pipeline and open the animated viewer."
    )
    p.add_argument("--count", type=int, default=30)
    p.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--port", type=int, default=8000)
    p.set_defaults(func=cmd_demo)

    return parser


def cmd_discover(args) -> int:
    try:
        frames = discover(limit=args.count)
    except DiscoveryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for frame in frames:  # newest-first
        print(f"{frame.valid_time:%Y-%m-%dT%H:%M:%S}  {frame.filename}  {frame.url}")
    return 0


def cmd_frames(args) -> int:
    try:
        produced, manifest_path = run_frames(args.output, args.count)
    except (DiscoveryError, WorkflowError, ManifestError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"\nWrote {len(produced)} frames and a manifest at {manifest_path}")
    return 0


def cmd_view(args) -> int:
    return run_view(args.output, args.port, open_browser=not args.no_browser)


def cmd_demo(args) -> int:
    if cmd_frames(args) != 0:
        return 1
    return run_view(args.output, args.port, open_browser=True)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
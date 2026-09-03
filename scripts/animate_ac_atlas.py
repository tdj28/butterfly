#!/usr/bin/env python3
"""Render verified GPU atlas frames as a GIF and contact sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
from PIL import Image

from butterfly.plotting import SPECIAL_CODES, parameter_plane, pixel_edges
from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def colors(max_period: int) -> tuple[ListedColormap, BoundaryNorm]:
    special = ["#7f0000", "#ffffff", "#d9d9d9", "#35b779"]
    periods = plt.colormaps["turbo"](np.linspace(0.05, 0.95, max_period))
    palette = special + [tuple(map(float, color)) for color in periods] + ["#081d58", "#54278f"]
    lower = SPECIAL_CODES["numerical_failure"]
    upper = SPECIAL_CODES["multistable"]
    cmap = ListedColormap(palette)
    return cmap, BoundaryNorm(np.arange(lower - 0.5, upper + 1.5), cmap.N)


def load_frames(frame_dir: Path) -> tuple[list[dict], dict[str, str]]:
    results = []
    hashes = {}
    for result_path in sorted(frame_dir.glob("frame-[0-9][0-9][0-9].json")):
        receipt_path = result_path.with_suffix(".receipt.json")
        raw = result_path.read_bytes()
        receipt = json.loads(receipt_path.read_bytes())
        if receipt.get("complete") is not True or receipt.get("result_sha256") != sha256_bytes(raw):
            raise RuntimeError(f"frame provenance failed: {result_path}")
        result = json.loads(raw)
        results.append(result)
        hashes[str(result["frame_index"])] = sha256_bytes(raw)
    if not results or [row["frame_index"] for row in results] != list(range(len(results))):
        raise RuntimeError("frames must form a contiguous zero-based sequence")
    return results, hashes


def render_frame(result: dict, output: Path, *, dpi: int, max_period: int) -> None:
    plane = parameter_plane(result, max_period=max_period)
    cmap, norm = colors(max_period)
    a_left, a_right = pixel_edges(plane.a_values)
    c_bottom, c_top = pixel_edges(plane.c_values)
    fig, axis = plt.subplots(figsize=(7.4, 5.6), constrained_layout=True)
    image = axis.imshow(
        plane.values,
        origin="lower",
        interpolation="nearest",
        aspect="auto",
        extent=(a_left, a_right, c_bottom, c_top),
        cmap=cmap,
        norm=norm,
        rasterized=True,
    )
    axis.set_xlabel(r"$a$")
    axis.set_ylabel(r"$c$")
    axis.set_title(rf"Rössler $(a,c)$ period atlas, $b={result['b']:.3f}$")
    axis.set_xlim(float(plane.a_values[0]), float(plane.a_values[-1]))
    axis.set_ylim(float(plane.c_values[0]), float(plane.c_values[-1]))
    colorbar = fig.colorbar(
        image,
        ax=axis,
        boundaries=np.arange(0.5, max_period + 1.5),
        ticks=[1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32],
        fraction=0.045,
        pad=0.03,
    )
    colorbar.set_label("Detected fundamental period")
    fig.savefig(output, dpi=dpi)
    plt.close(fig)


def render_contact_sheet(
    results: list[dict], output: Path, *, dpi: int, max_period: int
) -> None:
    columns = 4
    rows = int(np.ceil(len(results) / columns))
    cmap, norm = colors(max_period)
    fig, axes = plt.subplots(
        rows,
        columns,
        figsize=(3.3 * columns, 2.75 * rows),
        constrained_layout=True,
        squeeze=False,
    )
    for axis, result in zip(axes.ravel(), results, strict=False):
        plane = parameter_plane(result, max_period=max_period)
        a_left, a_right = pixel_edges(plane.a_values)
        c_bottom, c_top = pixel_edges(plane.c_values)
        axis.imshow(
            plane.values,
            origin="lower",
            interpolation="nearest",
            aspect="auto",
            extent=(a_left, a_right, c_bottom, c_top),
            cmap=cmap,
            norm=norm,
            rasterized=True,
        )
        axis.set_title(rf"$b={result['b']:.2f}$", fontsize=10)
        axis.set_xlabel(r"$a$", fontsize=8)
        axis.set_ylabel(r"$c$", fontsize=8)
        axis.tick_params(labelsize=7)
    for axis in axes.ravel()[len(results) :]:
        axis.set_visible(False)
    fig.suptitle("Evolution of the Rössler period atlas across b", fontsize=14)
    fig.savefig(output, dpi=dpi)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contact-sheet", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=140)
    parser.add_argument("--duration-ms", type=int, default=650)
    parser.add_argument("--max-period", type=int, default=32)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".gif":
        raise SystemExit("--output must end in .gif")
    if args.contact_sheet.suffix.lower() != ".png":
        raise SystemExit("--contact-sheet must end in .png")
    results, frame_hashes = load_frames(args.frame_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.contact_sheet.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="butterfly-atlas-") as directory:
        paths = []
        for result in results:
            path = Path(directory) / f"frame-{result['frame_index']:03d}.png"
            render_frame(result, path, dpi=args.dpi, max_period=args.max_period)
            paths.append(path)
        images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in paths]
        images[0].save(
            args.output,
            save_all=True,
            append_images=images[1:],
            duration=args.duration_ms,
            loop=0,
            optimize=False,
        )
    render_contact_sheet(
        results, args.contact_sheet, dpi=args.dpi, max_period=args.max_period
    )
    receipt = {
        "schema": "butterfly.ac-atlas-animation-receipt.v1",
        "experiment_id": results[0]["experiment_id"],
        "frame_result_sha256": frame_hashes,
        "frame_count": len(results),
        "b_values": [result["b"] for result in results],
        "gif": {
            "file": args.output.name,
            "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
            "bytes": args.output.stat().st_size,
            "duration_ms": args.duration_ms,
        },
        "contact_sheet": {
            "file": args.contact_sheet.name,
            "sha256": hashlib.sha256(args.contact_sheet.read_bytes()).hexdigest(),
            "bytes": args.contact_sheet.stat().st_size,
        },
        "dpi": args.dpi,
        "max_period": args.max_period,
    }
    receipt_path = args.output.with_suffix(".gif.receipt.json")
    atomic_write(receipt_path, canonical_json(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

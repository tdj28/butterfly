#!/usr/bin/env python3
"""Plot EXP-203 orbit qualification, components, and stability margin."""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def _components(indices: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
    unseen = set(indices)
    output = []
    while unseen:
        start = unseen.pop()
        component = {start}
        queue = deque((start,))
        while queue:
            i, j = queue.popleft()
            for di, dj in (
                (1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1),
            ):
                neighbor = (i + di, j + dj)
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        output.append(component)
    return sorted(output, key=len, reverse=True)


def _edges(values: np.ndarray) -> np.ndarray:
    edges = np.empty(values.size + 1, dtype=float)
    edges[1:-1] = 0.5 * (values[:-1] + values[1:])
    edges[0] = values[0] - 0.5 * (values[1] - values[0])
    edges[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return edges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    if sha256_bytes(receipt_bytes) != args.expected_receipt_sha256:
        raise SystemExit("receipt hash mismatch")
    manifest = json.loads(manifest_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt.get("manifest_sha256") != sha256_bytes(manifest_bytes):
        raise SystemExit("manifest hash mismatch")

    a_values = np.asarray(receipt["grid"]["a_values"], dtype=float)
    c_values = np.asarray(receipt["grid"]["c_values"], dtype=float)
    shape = (c_values.size, a_values.size)
    status = np.full(shape, np.nan)
    dominant = np.full(shape, np.nan)
    passing_indices = set()
    for row in receipt["candidates"]:
        i, j = map(int, row["grid_index"])
        if row["passed"]:
            status[j, i] = 3.0
            dominant[j, i] = float(row["dominant_nontrivial_multiplier"]["modulus"])
            passing_indices.add((i, j))
        elif not row.get("checks", {}).get("correction", True):
            status[j, i] = 0.0
        elif not row.get("checks", {}).get("stable", True):
            status[j, i] = 1.0
        else:
            status[j, i] = 2.0
    components = _components(passing_indices)
    component_field = np.full(shape, np.nan)
    for component_index, component in enumerate(components):
        for i, j in component:
            component_field[j, i] = float(component_index)

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.1), constrained_layout=True)
    a_edges, c_edges = _edges(a_values), _edges(c_values)
    status_cmap = ListedColormap(("#d9d9d9", "#ef8a62", "#fddbc7", "#2166ac"))
    status_norm = BoundaryNorm((-0.5, 0.5, 1.5, 2.5, 3.5), status_cmap.N)
    axes[0].pcolormesh(
        a_edges, c_edges, status, cmap=status_cmap, norm=status_norm,
        shading="flat", rasterized=True,
    )
    axes[0].set_title("orbit qualification\n551/6,283 pass")
    axes[0].legend(
        handles=[
            Line2D((0,), (0,), marker="s", linestyle="none", color="#2166ac", label="qualified"),
            Line2D((0,), (0,), marker="s", linestyle="none", color="#ef8a62", label="unstable first"),
            Line2D((0,), (0,), marker="s", linestyle="none", color="#d9d9d9", label="correction first"),
        ],
        fontsize=7,
        loc="lower left",
        frameon=True,
    )

    component_colors = ListedColormap(("#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e"))
    component_norm = BoundaryNorm(np.arange(-0.5, len(components) + 0.5), component_colors.N)
    axes[1].pcolormesh(
        a_edges, c_edges, component_field, cmap=component_colors,
        norm=component_norm, shading="flat", rasterized=True,
    )
    axes[1].set_title("eight-connected qualified components\n331, 156, 62, 1, 1")

    stability = axes[2].pcolormesh(
        a_edges, c_edges, np.ma.masked_invalid(dominant), cmap="magma",
        vmin=0.0, vmax=1.0, shading="flat", rasterized=True,
    )
    fig.colorbar(stability, ax=axes[2], shrink=0.84, pad=0.02, label=r"$|\lambda_{\mathrm{dom}}|$")
    axes[2].set_title("qualified stability margin\nmax 0.99945")

    seed = manifest["seed"]["parameters"]
    for axis in axes:
        axis.scatter(
            [seed["a"]], [seed["c"]], marker="*", s=85,
            facecolor="#fff176", edgecolor="#111111", linewidth=0.7,
        )
        axis.set_xlabel(r"$a$")
        axis.ticklabel_format(axis="x", style="plain", useOffset=False)
    axes[0].set_ylabel(r"$c$")
    for axis in axes[1:]:
        axis.tick_params(labelleft=False)
    fig.suptitle(
        r"EXP-203: lower-$c$ extension reaches a bounded stable period-6 strip",
        fontsize=12,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)

    output_bytes = args.output.read_bytes()
    output_receipt = {
        "schema": "butterfly.exp203-stable-period6-extension-figure.v1",
        "experiment_id": "EXP-203",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "input_receipt_sha256": sha256_bytes(receipt_bytes),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "qualified_candidate_count": len(passing_indices),
        "component_sizes": [len(component) for component in components],
        "maximum_qualified_dominant_modulus": float(np.nanmax(dominant)),
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(output_receipt),
    )
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

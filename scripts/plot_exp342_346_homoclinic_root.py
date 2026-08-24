#!/usr/bin/env python3
"""Plot the qualified homoclinic orbit and its three-radius persistence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from scipy.integrate import solve_ivp

from butterfly import RosslerParameters, rossler_rhs
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes

try:
    from scripts.scan_jones_homoclinic_manifold_match import align_local_geometry
    from scripts.scan_jones_homoclinic_unstable_angles import eigenspaces
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from scan_jones_homoclinic_manifold_match import align_local_geometry
    from scan_jones_homoclinic_unstable_angles import eigenspaces


SCHEMA = "butterfly.exp342-346-homoclinic-root-figure.v1"
RECEIPT_SCHEMA = "butterfly.jones-homoclinic-multiple-shooting-summary.v1"


def read_bound(path: Path, expected_hash: str) -> tuple[bytes, dict]:
    data = path.read_bytes()
    if sha256_bytes(data) != expected_hash:
        raise SystemExit(f"receipt hash mismatch: {path}")
    receipt = json.loads(data)
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("passed") is not True:
        raise SystemExit(f"unexpected receipt status: {path}")
    if receipt.get("root_nominated") is not True:
        raise SystemExit(f"root nomination missing: {path}")
    return data, receipt


def colored_path(axis, horizontal, vertical, time_values, *, cmap="viridis"):
    points = np.column_stack((horizontal, vertical))
    segments = np.stack((points[:-1], points[1:]), axis=1)
    collection = LineCollection(segments, cmap=cmap, linewidth=1.1)
    collection.set_array(0.5 * (time_values[:-1] + time_values[1:]))
    axis.add_collection(collection)
    axis.autoscale()
    return collection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for experiment in ("342", "344", "346"):
        parser.add_argument(f"--exp{experiment}", type=Path, required=True)
        parser.add_argument(f"--exp{experiment}-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None or source["dirty"]:
        raise SystemExit("clean source required")
    bound = []
    for experiment in ("342", "344", "346"):
        bound.append(
            read_bound(
                getattr(args, f"exp{experiment}"),
                getattr(args, f"exp{experiment}_sha256"),
            )
        )
    receipts = [row[1] for row in bound]
    if [row["matching_radius"] for row in receipts] != [0.03, 0.025, 0.02]:
        raise SystemExit("unexpected radius sequence")

    root = receipts[-1]
    variables = root["final_variables"]
    parameters = RosslerParameters(a=variables["a"], b=0.2, c=10.3084)
    reference = RosslerParameters(a=0.1798, b=0.2, c=10.3084)
    _reference_equilibrium, _reference_values, reference_stable, reference_plane = (
        eigenspaces(reference)
    )
    equilibrium, _values, _stable, plane = align_local_geometry(
        parameters, reference_stable, reference_plane
    )
    angle = float(variables["angle"])
    direction = np.cos(angle) * plane[:, 0] + np.sin(angle) * plane[:, 1]
    initial = equilibrium + 1e-7 * direction
    nodes = np.asarray(root["final_nodes"], dtype=np.float64)
    starts = np.vstack((initial, nodes))
    segment_count = int(root["segment_count"])
    total_time = float(variables["total_flight_time"])
    segment_time = total_time / segment_count
    path_rows = []
    time_rows = []
    points_per_segment = 90
    local_times = np.linspace(0.0, segment_time, points_per_segment)
    for index, start in enumerate(starts):
        integrated = solve_ivp(
            lambda time_value, state: rossler_rhs(time_value, state, parameters),
            (0.0, segment_time),
            start,
            method="Radau",
            rtol=1e-10,
            atol=1e-12,
            max_step=0.05,
            t_eval=local_times,
        )
        if not integrated.success:
            raise RuntimeError("orbit segment rendering failed")
        first = 0 if index == 0 else 1
        path_rows.append(integrated.y[:, first:].T)
        time_rows.append(index * segment_time + local_times[first:])
    path = np.vstack(path_rows)
    orbit_time = np.concatenate(time_rows)

    figure = plt.figure(figsize=(14.2, 5.4), constrained_layout=True)
    grid = figure.add_gridspec(1, 3, width_ratios=(1.0, 1.0, 0.92))
    axis_xy = figure.add_subplot(grid[0, 0])
    axis_xz = figure.add_subplot(grid[0, 1])
    right = grid[0, 2].subgridspec(2, 1, hspace=0.08)
    axis_parameter = figure.add_subplot(right[0, 0])
    axis_residual = figure.add_subplot(right[1, 0], sharex=axis_parameter)

    xy_collection = colored_path(axis_xy, path[:, 0], path[:, 1], orbit_time)
    colored_path(axis_xz, path[:, 0], path[:, 2], orbit_time)
    for axis, horizontal, vertical in (
        (axis_xy, 0, 1),
        (axis_xz, 0, 2),
    ):
        axis.plot(
            equilibrium[horizontal],
            equilibrium[vertical],
            marker="*",
            color="#d73027",
            markersize=10,
            label="saddle focus",
            zorder=4,
        )
        axis.plot(
            path[-1, horizontal],
            path[-1, vertical],
            marker="o",
            markerfacecolor="none",
            markeredgecolor="#111111",
            markersize=6,
            label="stable target",
            zorder=4,
        )
        axis.grid(alpha=0.18)
        axis.set_xlabel("x")
    axis_xy.set_ylabel("y")
    axis_xz.set_ylabel("z")
    axis_xy.set_title("A  Matched homoclinic orbit: x-y")
    axis_xz.set_title("B  Matched homoclinic orbit: x-z")
    axis_xy.legend(fontsize=8, loc="best")
    colorbar = figure.colorbar(xy_collection, ax=[axis_xy, axis_xz], shrink=0.82)
    colorbar.set_label("flight time")

    radii = np.asarray([row["matching_radius"] for row in receipts])
    a_values = np.asarray([row["final_variables"]["a"] for row in receipts])
    residuals = np.asarray([row["final_maximum_block_residual"] for row in receipts])
    axis_parameter.plot(radii, a_values, "o-", color="#2166ac", linewidth=1.5)
    axis_parameter.axhline(0.1798, color="#b2182b", linestyle="--", label="Jones printed a")
    axis_parameter.set_ylabel("fitted a")
    axis_parameter.set_title("C  Shrinking-sphere persistence")
    axis_parameter.grid(alpha=0.2)
    axis_parameter.legend(fontsize=8, loc="best")
    axis_parameter.tick_params(labelbottom=False)
    axis_parameter.set_ylim(0.17955, 0.1829)
    axis_parameter.text(
        0.02,
        0.97,
        f"spread in fitted a: {np.ptp(a_values):.2e}",
        transform=axis_parameter.transAxes,
        va="top",
        fontsize=8.5,
    )

    axis_residual.semilogy(radii, residuals, "s-", color="#1b7837", linewidth=1.5)
    axis_residual.axhline(1e-8, color="#222222", linestyle=":", label="root gate")
    axis_residual.set_xlabel("matching-sphere radius")
    axis_residual.set_ylabel("max arc defect")
    axis_residual.grid(alpha=0.2)
    axis_residual.legend(fontsize=8, loc="best")
    axis_residual.invert_xaxis()

    figure.suptitle(
        "Revised-coordinate homoclinic root: independent solver and radius persistence",
        fontsize=13,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    figure.savefig(temporary, dpi=args.dpi)
    plt.close(figure)
    temporary.replace(args.output)

    output_bytes = args.output.read_bytes()
    receipt = {
        "schema": SCHEMA,
        "source": source,
        "exp342_receipt_sha256": sha256_bytes(bound[0][0]),
        "exp344_receipt_sha256": sha256_bytes(bound[1][0]),
        "exp346_receipt_sha256": sha256_bytes(bound[2][0]),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "path_point_count": len(path),
        "matching_radii": radii.tolist(),
        "fitted_a_values": a_values.tolist(),
        "maximum_arc_defects": residuals.tolist(),
        "fitted_a_spread": float(np.ptp(a_values)),
        "printed_a": 0.1798,
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

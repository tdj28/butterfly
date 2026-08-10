#!/usr/bin/env python3
"""Render the qualified published unimodal and bimodal return-map controls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline

from butterfly import RosslerParameters, SolverConfig, barrio_rossler_section, collect_crossings
from butterfly.return_map import _binned_relation
from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    manifest = json.loads(manifest_bytes)
    receipt = json.loads(receipt_bytes)
    if receipt["manifest_sha256"] != sha256_bytes(manifest_bytes):
        raise SystemExit("EXP-108 manifest/receipt mismatch")
    solver = SolverConfig(**manifest["solver"])
    baseline = manifest["oracle_baseline"]
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.0), constrained_layout=True)
    summaries = []
    for axis, case in zip(axes, manifest["parameter_cases"], strict=True):
        parameters = RosslerParameters(**case["parameters"])
        crossings = collect_crossings(
            parameters,
            manifest["initial_state"],
            barrio_rossler_section(parameters),
            transient=float(manifest["crossings"]["transient"]),
            observation_horizon=float(manifest["crossings"]["observation_horizon"]),
            max_crossings=int(manifest["crossings"]["max_crossings"]),
            config=solver,
        )
        values = crossings.states[:, 1]
        source = values[:-1]
        target = values[1:]
        source_min = float(np.min(source))
        source_range = float(np.ptp(source))
        target_min = float(np.min(target))
        target_range = float(np.ptp(target))
        normalized_source = (source - source_min) / source_range
        normalized_target = (target - target_min) / target_range
        x_values, y_values, _ = _binned_relation(
            normalized_source,
            normalized_target,
            bin_count=int(baseline["bin_count"]),
            minimum_bin_points=int(baseline["minimum_bin_points"]),
        )
        order = np.argsort(x_values)
        spline = UnivariateSpline(
            x_values[order],
            y_values[order],
            k=3,
            s=float(baseline["smoothing"]) * len(x_values),
            ext=3,
        )
        grid = np.linspace(float(np.min(x_values)), float(np.max(x_values)), 1200)
        axis.scatter(source, target, s=8, alpha=0.23, color="#3182bd", edgecolors="none")
        axis.plot(
            source_min + grid * source_range,
            target_min + spline(grid) * target_range,
            color="#e31a1c",
            linewidth=2.0,
            label="binned spline",
        )
        rows = [
            row
            for row in receipt["rows"]
            if row["parameter_case"] == case["name"]
            and row["coordinate"] == "y"
            and row["oracle_variant"] == "baseline"
            and abs(float(row["section_offset_delta"])) < 1e-15
        ]
        if len(rows) != 1:
            raise SystemExit("missing unique baseline EXP-108 receipt row")
        oracle = rows[0]["oracle"]
        for critical in oracle["critical_points"]:
            axis.axvline(float(critical), color="#6a3d9a", linestyle="--", linewidth=1.4)
        axis.set_title(
            rf"$a={parameters.a:.2f}$: {oracle['branch_count']} branches",
            fontsize=12,
        )
        axis.set_xlabel(r"$y_n$")
        axis.set_ylabel(r"$y_{n+1}$")
        axis.grid(alpha=0.18)
        summaries.append(
            {
                "case": case["name"],
                "crossing_count": len(crossings.times),
                "integration_success": crossings.integration_success,
                "branch_count": oracle["branch_count"],
                "critical_points": oracle["critical_points"],
            }
        )
    axes[0].legend(loc="lower left", frameon=True)
    fig.suptitle(
        r"Published Barrio-section controls at $(b,c)=(0.2,20)$",
        fontsize=15,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi, bbox_inches="tight")
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    output_receipt = {
        "schema": "butterfly.paper-return-map-controls.v1",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "qualification_receipt_sha256": sha256_bytes(receipt_bytes),
        "summaries": summaries,
        "output": str(args.output),
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
    }
    atomic_write(args.output.with_suffix(".receipt.json"), canonical_json(output_receipt))
    print(json.dumps(output_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Plot a full unit-event pseudo-arclength trace and its residuals."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from butterfly.scan import atomic_write, canonical_json, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--source-curve", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    source_raw = args.source_curve.read_bytes()
    receipt = json.loads(raw)
    source = json.loads(source_raw)
    if receipt.get("schema") != "butterfly.unit-event-pseudo-arclength-receipt.v1":
        raise SystemExit("unsupported event pseudo-arclength receipt")
    if source.get("schema") != "butterfly.unit-event-curve-receipt.v1":
        raise SystemExit("unsupported source curve receipt")

    seed_a = [variables[4] for variables in receipt["seed_variables"]]
    seed_b = [variables[5] for variables in receipt["seed_variables"]]
    rows = receipt["rows"]
    a_values = np.asarray(seed_a + [row["a"] for row in rows], dtype=float)
    b_values = np.asarray(seed_b + [row["b"] for row in rows], dtype=float)
    arc_index = np.arange(len(a_values))
    accepted = [row for row in source["rows"] if row["solver_success"]]

    fig, (curve_axis, residual_axis) = plt.subplots(
        1, 2, figsize=(11.0, 4.7), constrained_layout=True
    )
    curve_axis.plot(
        [row["a"] for row in accepted],
        [row["b"] for row in accepted],
        color="0.72",
        marker="o",
        markersize=3,
        linewidth=1.2,
        label="EXP-034 natural continuation",
    )
    curve_axis.plot(a_values, b_values, color="tab:blue", linewidth=1.5, alpha=0.75)
    points = curve_axis.scatter(
        a_values,
        b_values,
        c=arc_index,
        cmap="plasma",
        s=28,
        zorder=3,
        label="EXP-035 pseudo-arclength",
    )
    a_minimum = int(np.argmin(a_values))
    b_minimum = int(np.argmin(b_values))
    curve_axis.scatter(
        [a_values[a_minimum]], [b_values[a_minimum]], marker="D", s=55, color="black"
    )
    curve_axis.scatter(
        [a_values[b_minimum]], [b_values[b_minimum]], marker="s", s=55, color="black"
    )
    curve_axis.annotate(
        "a reversal",
        (a_values[a_minimum], b_values[a_minimum]),
        xytext=(8, -18),
        textcoords="offset points",
        fontsize=8,
    )
    curve_axis.annotate(
        "b reversal",
        (a_values[b_minimum], b_values[b_minimum]),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
    )
    curve_axis.set_xlabel("Rössler parameter a")
    curve_axis.set_ylabel(r"Event parameter $b_*$")
    curve_axis.set_title(f"Fold-safe period-5 +1 event trace at c={receipt['fixed_c']}")
    curve_axis.grid(True, alpha=0.24, linewidth=0.6)
    curve_axis.legend(fontsize=8)
    colorbar = fig.colorbar(points, ax=curve_axis, pad=0.02)
    colorbar.set_label("Continuation point index")

    step = np.arange(len(rows))
    for label, key, marker in (
        ("Closure", "closure_error", "o"),
        ("Unit eigenvector", "eigen_residual", "s"),
        ("Flow orthogonality", "flow_orthogonality_residual", "^"),
        ("Arclength", "arclength_residual", "x"),
    ):
        residual_axis.semilogy(
            step,
            [max(float(row[key]), np.finfo(float).tiny) for row in rows],
            marker=marker,
            markersize=3.5,
            linewidth=1.1,
            label=label,
        )
    residual_axis.axhline(1e-8, color="black", linestyle="--", linewidth=1.0)
    residual_axis.set_xlabel("Corrected pseudo-arclength step")
    residual_axis.set_ylabel("Residual")
    residual_axis.set_title("Coupled event-corrector residuals")
    residual_axis.grid(True, which="both", alpha=0.24, linewidth=0.6)
    residual_axis.legend(fontsize=8)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.event-pseudo-arclength-figure-receipt.v1",
        "experiment_id": receipt["experiment_id"],
        "source_receipt_sha256": sha256_bytes(raw),
        "source_curve_receipt_sha256": sha256_bytes(source_raw),
        "output_file": args.output.name,
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "output_bytes": len(output_bytes),
        "dpi": args.dpi,
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(figure_receipt),
    )
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Plot valid and rejected points from a coupled unit-event curve receipt."""

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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    receipt = json.loads(raw)
    if receipt.get("schema") != "butterfly.unit-event-curve-receipt.v1":
        raise SystemExit("unsupported unit-event curve receipt")
    valid = [row for row in receipt["rows"] if row["solver_success"]]
    rejected = [row for row in receipt["rows"] if not row["solver_success"]]

    fig, (curve_axis, residual_axis) = plt.subplots(
        1, 2, figsize=(10.5, 4.5), constrained_layout=True
    )
    curve_axis.plot(
        [row["a"] for row in valid],
        [row["b"] for row in valid],
        "o-",
        linewidth=1.7,
        label="Accepted coupled events",
    )
    if rejected:
        curve_axis.scatter(
            [row["a"] for row in rejected],
            [row["b"] for row in rejected],
            marker="x",
            s=70,
            linewidth=2,
            color="crimson",
            label="Rejected corrector output",
        )
    curve_axis.set_xlabel("Rössler parameter a")
    curve_axis.set_ylabel(r"Corrected event parameter $b_*(a)$")
    curve_axis.set_title(f"Period-5 +1 event curve at c={receipt['fixed_c']}")
    curve_axis.grid(True, alpha=0.24, linewidth=0.6)
    curve_axis.legend(fontsize=8)

    for label, key, marker in (
        ("Closure", "closure_error", "o"),
        ("Unit eigenvector", "eigen_residual", "s"),
        ("Flow orthogonality", "flow_orthogonality_residual", "^"),
    ):
        residual_axis.semilogy(
            [row["a"] for row in receipt["rows"]],
            [max(float(row[key]), np.finfo(float).tiny) for row in receipt["rows"]],
            marker=marker,
            linewidth=1.25,
            label=label,
        )
    residual_axis.axhline(1e-8, color="black", linestyle="--", linewidth=1.0)
    residual_axis.set_xlabel("Rössler parameter a")
    residual_axis.set_ylabel("Coupled-solve residual")
    residual_axis.set_title("Acceptance residuals (gate at $10^{-8}$)")
    residual_axis.grid(True, which="both", alpha=0.24, linewidth=0.6)
    residual_axis.legend(fontsize=8)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.unit-event-curve-figure-receipt.v1",
        "experiment_id": receipt["experiment_id"],
        "source_receipt_sha256": sha256_bytes(raw),
        "valid_point_count": len(valid),
        "rejected_point_count": len(rejected),
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

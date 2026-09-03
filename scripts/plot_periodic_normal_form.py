#!/usr/bin/env python3
"""Plot phase-quotient branch and multiplier scaling near a +1 event."""

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
    if receipt.get("schema") != "butterfly.periodic-normal-form-scaling-receipt.v1":
        raise SystemExit("unsupported normal-form receipt")

    rows = receipt["rows"]
    mu = np.asarray([row["mu"] for row in rows], dtype=float)
    separation = np.asarray([row["separation_rms"] for row in rows], dtype=float)
    primary_excess = np.asarray(
        [row["primary_multiplier_modulus"] - 1.0 for row in rows], dtype=float
    )
    secondary_deficit = np.asarray(
        [1.0 - row["secondary_multiplier_modulus"] for row in rows], dtype=float
    )
    fit = receipt["separation_power_law"]
    predicted = np.exp(float(fit["intercept"])) * mu ** float(fit["exponent"])

    fig, (branch_axis, multiplier_axis) = plt.subplots(
        1, 2, figsize=(10.5, 4.6), constrained_layout=True
    )
    branch_axis.loglog(mu, separation, "o-", linewidth=1.6, label="Corrected cycles")
    branch_axis.loglog(
        mu,
        predicted,
        "--",
        linewidth=1.4,
        label=rf"fit: $\beta={fit['exponent']:.6f}$, $R^2={fit['r_squared']:.7f}$",
    )
    branch_axis.set_xlabel(r"Distance above event $\mu=b-b_*$")
    branch_axis.set_ylabel("Phase-aligned orbit separation (RMS)")
    branch_axis.set_title("Square-root branch opening")
    branch_axis.grid(True, which="both", alpha=0.24, linewidth=0.6)
    branch_axis.legend(fontsize=8)

    multiplier_axis.loglog(
        mu, primary_excess, "o-", linewidth=1.6, label=r"Primary: $\lambda_p-1$"
    )
    multiplier_axis.loglog(
        mu,
        secondary_deficit,
        "s-",
        linewidth=1.6,
        label=r"Secondary: $1-\lambda_s$",
    )
    multiplier_axis.loglog(
        mu,
        2.0 * primary_excess,
        ":",
        color="black",
        linewidth=1.2,
        label=r"Pitchfork reference $2(\lambda_p-1)$",
    )
    multiplier_axis.set_xlabel(r"Distance above event $\mu=b-b_*$")
    multiplier_axis.set_ylabel("Floquet-multiplier deviation")
    multiplier_axis.set_title(
        f"Stability exchange (median ratio {receipt['multiplier_ratio_median']:.4f})"
    )
    multiplier_axis.grid(True, which="both", alpha=0.24, linewidth=0.6)
    multiplier_axis.legend(fontsize=8)

    fig.suptitle(
        rf"Period-5 local normal form at $b_*={receipt['b_star']:.12f}$",
        fontsize=13,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.periodic-normal-form-figure-receipt.v1",
        "experiment_id": receipt["experiment_id"],
        "source_receipt_sha256": sha256_bytes(raw),
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

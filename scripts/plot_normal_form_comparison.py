#!/usr/bin/env python3
"""Compare pitchfork-like scaling at two separated surface events."""

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


def scaling_rows(receipt: dict) -> list[dict]:
    if receipt["schema"] == "butterfly.periodic-normal-form-scaling-receipt.v1":
        return receipt["rows"]
    if receipt["schema"] == "butterfly.separated-normal-form-receipt.v1":
        return receipt["scaling_rows"]
    raise ValueError("unsupported normal-form receipt")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    receipts = []
    hashes = {}
    for path in args.receipts:
        raw = path.read_bytes()
        receipt = json.loads(raw)
        scaling_rows(receipt)
        receipts.append(receipt)
        hashes[receipt["experiment_id"]] = sha256_bytes(raw)

    fig, (separation_axis, ratio_axis) = plt.subplots(
        1, 2, figsize=(10.5, 4.5), constrained_layout=True
    )
    colors = plt.colormaps["tab10"](np.linspace(0.0, 0.8, len(receipts)))
    for color, receipt in zip(colors, receipts, strict=True):
        rows = scaling_rows(receipt)
        mu = np.asarray([row["mu"] for row in rows], dtype=float)
        separation = np.asarray([row["separation_rms"] for row in rows], dtype=float)
        ratios = np.asarray([row["multiplier_deviation_ratio"] for row in rows], dtype=float)
        fit = receipt["separation_power_law"]
        predicted = np.exp(float(fit["intercept"])) * mu ** float(fit["exponent"])
        if "event" in receipt:
            label = (
                f"{receipt['experiment_id']}: "
                f"a={receipt['event']['a']:.4f}, c={receipt['event']['c']:.1f}"
            )
        else:
            label = f"{receipt['experiment_id']}: a=0.2450, c=5.1"
        separation_axis.loglog(mu, separation, "o", color=color, label=label)
        separation_axis.loglog(
            mu,
            predicted,
            "--",
            color=color,
            linewidth=1.4,
            label=rf"$\beta={fit['exponent']:.6f}$, $R^2={fit['r_squared']:.7f}$",
        )
        ratio_axis.semilogx(mu, ratios, "o-", color=color, linewidth=1.5, label=label)

    separation_axis.set_xlabel(r"Distance above event $\mu=b-b_*$")
    separation_axis.set_ylabel("Phase-aligned primary/secondary RMS")
    separation_axis.set_title("Square-root opening at separated surface points")
    separation_axis.grid(True, which="both", alpha=0.24, linewidth=0.6)
    separation_axis.legend(fontsize=8)

    ratio_axis.axhline(2.0, color="black", linestyle="--", linewidth=1.0)
    ratio_axis.set_xlabel(r"Distance above event $\mu=b-b_*$")
    ratio_axis.set_ylabel(r"$(1-\lambda_s)/(\lambda_p-1)$")
    ratio_axis.set_title("Cubic normal-form multiplier ratio")
    ratio_axis.grid(True, which="both", alpha=0.24, linewidth=0.6)
    ratio_axis.legend(fontsize=8)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.normal-form-comparison-figure-receipt.v1",
        "experiment_ids": [receipt["experiment_id"] for receipt in receipts],
        "source_receipt_sha256": hashes,
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

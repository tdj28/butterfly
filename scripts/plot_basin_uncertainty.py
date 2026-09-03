#!/usr/bin/env python3
"""Plot provenance-bound basin uncertain fractions and declared power-law fits."""

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
    parser.add_argument("--receipts", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    if args.output.suffix.lower() not in (".png", ".pdf", ".svg"):
        raise SystemExit("--output must end in .png, .pdf, or .svg")

    receipts = []
    input_hashes = {}
    for path in args.receipts:
        raw = path.read_bytes()
        receipt = json.loads(raw)
        if receipt.get("schema") != "butterfly.basin-uncertainty-receipt.v1":
            raise SystemExit(f"unsupported receipt schema: {path}")
        receipts.append(receipt)
        input_hashes[receipt["experiment_id"]] = sha256_bytes(raw)

    fig, axis = plt.subplots(figsize=(7.4, 5.6), constrained_layout=True)
    colors = plt.colormaps["viridis"](np.linspace(0.2, 0.8, len(receipts)))
    for color, receipt in zip(colors, receipts, strict=True):
        analysis = receipt["analysis"]
        epsilon = np.asarray(analysis["epsilons"], dtype=float)
        fraction = np.asarray(analysis["uncertain_fractions_jeffreys"], dtype=float)
        order = np.argsort(epsilon)
        axis.loglog(
            epsilon[order],
            fraction[order],
            marker="o",
            linewidth=1.8,
            color=color,
            label=f"{receipt['experiment_id']} observations",
        )
        predicted = np.exp(float(analysis["intercept"])) * epsilon ** float(
            analysis["alpha"]
        )
        axis.loglog(
            epsilon[order],
            predicted[order],
            linestyle="--",
            linewidth=1.4,
            color=color,
            label=(
                f"{receipt['experiment_id']} all-scale fit: "
                rf"$\alpha={analysis['alpha']:.3f}$, $R^2={analysis['r_squared']:.3f}$"
            ),
        )

    axis.set_xlabel(r"Initial-condition separation $\varepsilon$")
    axis.set_ylabel(r"Uncertain-pair fraction $f(\varepsilon)$")
    axis.set_title("Period-3 / period-12 basin uncertainty scaling")
    axis.grid(True, which="both", alpha=0.24, linewidth=0.6)
    axis.legend(fontsize=8, frameon=True)
    axis.invert_xaxis()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.stem}.tmp{args.output.suffix}")
    fig.savefig(temporary, dpi=args.dpi)
    plt.close(fig)
    temporary.replace(args.output)
    output_bytes = args.output.read_bytes()
    figure_receipt = {
        "schema": "butterfly.basin-uncertainty-figure-receipt.v1",
        "experiment_ids": [receipt["experiment_id"] for receipt in receipts],
        "source_receipt_sha256": input_hashes,
        "output_file": args.output.name,
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "output_bytes": len(output_bytes),
        "dpi": args.dpi,
        "note": "Dashed lines are each experiment's all-declared-scale fit; EXP-019 visibly includes coarse-scale saturation.",
    }
    receipt_path = args.output.with_suffix(args.output.suffix + ".receipt.json")
    atomic_write(receipt_path, canonical_json(figure_receipt))
    print(json.dumps(figure_receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

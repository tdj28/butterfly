#!/usr/bin/env python3
"""Plot the printed-hub coarse and refined unstable-angle return scans."""

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


SCHEMA = "butterfly.exp329-331-homoclinic-angle-scan-figure.v1"


def read_bound(path: Path, expected_hash: str, schema: str) -> tuple[bytes, dict]:
    data = path.read_bytes()
    if sha256_bytes(data) != expected_hash:
        raise SystemExit(f"receipt hash mismatch: {path}")
    receipt = json.loads(data)
    if receipt.get("schema") != schema or receipt.get("passed") is not True:
        raise SystemExit(f"unexpected receipt status: {path}")
    return data, receipt


def plot_rows(axes, rows: list[dict], title_prefix: str) -> None:
    angles = np.asarray([row["angle"] for row in rows], dtype=np.float64)
    distances = np.asarray([row["minimum_return_distance"] for row in rows], dtype=np.float64)
    stable_cosines = np.asarray([row["stable_direction_cosine"] for row in rows], dtype=np.float64)
    closest = int(np.argmin(distances))

    axes[0].plot(angles, distances, "o-", markersize=3.2, linewidth=1.0, color="#2166ac")
    axes[0].plot(angles[closest], distances[closest], "*", markersize=11, color="#b2182b")
    axes[0].axhline(0.01, color="#222222", linestyle=":", label="distance gate")
    axes[0].set_ylabel("closest return distance")
    axes[0].set_title(f"{title_prefix}: proximity")
    axes[0].grid(alpha=0.2)
    axes[0].legend(fontsize=8)

    cosine_gate = np.sqrt(1.0 - 0.1**2)
    axes[1].plot(angles, stable_cosines, "o-", markersize=3.2, linewidth=1.0, color="#1b7837")
    axes[1].plot(angles[closest], stable_cosines[closest], "*", markersize=11, color="#b2182b")
    axes[1].axhline(cosine_gate, color="#222222", linestyle=":", label="stable-alignment gate")
    axes[1].set_ylim(-0.02, 1.04)
    axes[1].set_xlabel("unstable-eigenspace departure angle (radians)")
    axes[1].set_ylabel(r"$|\langle \widehat{x-x_*},e_s\rangle|$")
    axes[1].set_title(f"{title_prefix}: stable-direction alignment")
    axes[1].grid(alpha=0.2)
    axes[1].legend(fontsize=8)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp329", type=Path, required=True)
    parser.add_argument("--exp329-sha256", required=True)
    parser.add_argument("--exp331", type=Path, required=True)
    parser.add_argument("--exp331-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    bytes329, exp329 = read_bound(
        args.exp329,
        args.exp329_sha256,
        "butterfly.jones-homoclinic-unstable-angle-scan-receipt.v1",
    )
    bytes331, exp331 = read_bound(
        args.exp331,
        args.exp331_sha256,
        "butterfly.jones-homoclinic-unstable-angle-refinement-receipt.v1",
    )
    if exp329["candidate_count"] != 0 or exp331["candidate_count"] != 0:
        raise SystemExit("candidate classification changed")

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), constrained_layout=True)
    plot_rows(axes[:, 0], exp329["angles"], "96-angle full circle")
    plot_rows(axes[:, 1], exp331["angles"], "257-angle local refinement")
    figure.suptitle(
        "EXP-329/331: close returns at the printed hub are strongly transverse",
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
        "exp329_receipt_sha256": sha256_bytes(bytes329),
        "exp331_receipt_sha256": sha256_bytes(bytes331),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "coarse_candidate_count": exp329["candidate_count"],
        "refined_candidate_count": exp331["candidate_count"],
        "refined_closest_distance": exp331["closest_return"]["minimum_return_distance"],
        "refined_closest_stable_transverse_ratio": exp331["closest_return"][
            "stable_transverse_ratio"
        ],
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

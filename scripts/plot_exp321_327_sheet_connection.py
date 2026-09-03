#!/usr/bin/env python3
"""Plot the exact connection from the seventh daughter to event eight."""

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


SCHEMA = "butterfly.exp321-327-sheet-connection-figure.v1"


def read_bound(path: Path, expected_hash: str, schema: str, passed: bool):
    data = path.read_bytes()
    if sha256_bytes(data) != expected_hash:
        raise SystemExit(f"receipt hash mismatch: {path}")
    receipt = json.loads(data)
    if receipt.get("schema") != schema or receipt.get("passed") is not passed:
        raise SystemExit(f"unexpected receipt status: {path}")
    return data, receipt


def signed_multiplier(row: dict) -> float:
    return float(row["spectrum"]["products"][0]["dominant_transverse_decimal"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp321", type=Path, required=True)
    parser.add_argument("--exp321-sha256", required=True)
    parser.add_argument("--exp326", type=Path, required=True)
    parser.add_argument("--exp326-sha256", required=True)
    parser.add_argument("--exp327", type=Path, required=True)
    parser.add_argument("--exp327-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=260)
    args = parser.parse_args()

    bytes321, exp321 = read_bound(
        args.exp321,
        args.exp321_sha256,
        "butterfly.jones-period1536-decimal-continuation-receipt.v1",
        True,
    )
    bytes326, exp326 = read_bound(
        args.exp326,
        args.exp326_sha256,
        "butterfly.jones-period1536-decimal-event-connection-receipt.v1",
        False,
    )
    bytes327, exp327 = read_bound(
        args.exp327,
        args.exp327_sha256,
        "butterfly.jones-period1536-decimal-phase-registration-receipt.v1",
        True,
    )
    failed326 = sorted(name for name, passed in exp326["checks"].items() if not passed)
    if failed326 != ["node_identity"]:
        raise SystemExit("EXP-326 failure pattern changed")

    target_a = float(exp326["target_a_decimal"])
    rows321 = exp321["rows"]
    rows326 = exp326["continuation_rows"]
    all_rows = [*rows321, *rows326]
    event_offsets = np.array([1e12 * (row["a"] - target_a) for row in all_rows])
    amplitudes = np.array([row["half_node_rms"] for row in all_rows])

    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.8), constrained_layout=True)
    axes[0, 0].plot(
        event_offsets[: len(rows321)], amplitudes[: len(rows321)],
        "o-", color="#2166ac", label="EXP-321 stable continuation",
    )
    axes[0, 0].plot(
        event_offsets[len(rows321) - 1 :], amplitudes[len(rows321) - 1 :],
        "o-", color="#b2182b", label="EXP-326 connection rows",
    )
    axes[0, 0].axvline(0.0, color="#222222", linestyle=":", label="event coordinate")
    axes[0, 0].set_xlabel(r"event-relative $10^{12}(a-a_8)$")
    axes[0, 0].set_ylabel("primitive half-node RMS amplitude")
    axes[0, 0].set_title("the immediate daughter reaches event eight")
    axes[0, 0].ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    axes[0, 0].grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)

    connection_offsets = [1e12 * (row["a"] - target_a) for row in rows326]
    connection_multipliers = [signed_multiplier(row) for row in rows326]
    axes[0, 1].plot(
        connection_offsets,
        connection_multipliers,
        "o-",
        color="#b2182b",
        label="continued parent sheet",
    )
    axes[0, 1].plot(
        [0.0],
        [float(exp327["spectrum"]["products"][0]["dominant_transverse_decimal"])],
        marker="*",
        markersize=13,
        color="#1b7837",
        label="shared-phase event root",
    )
    axes[0, 1].axhline(-1.0, color="#222222", linestyle=":", label="flip condition")
    axes[0, 1].axvline(0.0, color="#777777", linestyle=":")
    axes[0, 1].set_xlabel(r"event-relative $10^{12}(a-a_8)$")
    axes[0, 1].set_ylabel("signed dominant transverse multiplier")
    axes[0, 1].set_title("the same sheet crosses the real -1 event")
    axes[0, 1].grid(alpha=0.2)
    axes[0, 1].legend(fontsize=8)

    iterations = [row["iteration"] for row in exp327["history"]]
    for key, label, color in (
        ("direct_node_rms", "direct node RMS", "#2166ac"),
        ("matching_residual", "matching residual", "#b2182b"),
        ("phase_residual", "phase residual", "#1b7837"),
    ):
        axes[1, 0].semilogy(
            iterations,
            [max(row[key], 1e-55) for row in exp327["history"]],
            "o-",
            color=color,
            label=label,
        )
    axes[1, 0].axhline(1e-8, color="#777777", linestyle=":", label="node gate")
    axes[1, 0].axhline(1e-20, color="#222222", linestyle=":", label="closure gate")
    axes[1, 0].set_xlabel("shared-phase Newton update")
    axes[1, 0].set_ylabel("residual or discrepancy")
    axes[1, 0].set_title("exact rephasing removes the apparent mismatch")
    axes[1, 0].grid(alpha=0.2, which="both")
    axes[1, 0].legend(fontsize=7.6)

    normalized = {
        "matching": exp327["history"][-1]["matching_residual"] / 1e-20,
        "node identity": exp327["shared_phase_node_rms"] / 1e-8,
        "period identity": exp327["connected_period_difference"] / 1e-8,
        "neutral mode": exp327["spectrum"]["maximum_neutral_residual"] / 1e-10,
    }
    bars = axes[1, 1].bar(
        np.arange(len(normalized)),
        list(normalized.values()),
        color=["#b2182b", "#2166ac", "#4393c3", "#1b7837"],
    )
    axes[1, 1].axhline(1.0, color="#222222", linestyle=":", label="frozen gate")
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xticks(np.arange(len(normalized)), list(normalized), rotation=15, ha="right")
    axes[1, 1].set_ylabel("observed value / allowed value")
    axes[1, 1].set_title("all connection gates pass with large margins")
    axes[1, 1].grid(alpha=0.2, axis="y", which="both")
    axes[1, 1].legend(fontsize=8)
    for bar, value in zip(bars, normalized.values()):
        axes[1, 1].annotate(
            f"{value:.1e}",
            (bar.get_x() + bar.get_width() / 2, value),
            ha="center",
            va="bottom",
            xytext=(0, 3),
            textcoords="offset points",
            fontsize=8,
        )

    figure.suptitle(
        "EXP-321/326/327: exact sheet connection from birth seven to event eight",
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
        "exp321_receipt_sha256": sha256_bytes(bytes321),
        "exp326_receipt_sha256": sha256_bytes(bytes326),
        "exp327_receipt_sha256": sha256_bytes(bytes327),
        "output": args.output.name,
        "output_bytes": len(output_bytes),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "dpi": args.dpi,
        "target_a": target_a,
        "connection_event_multiplier": float(
            exp327["spectrum"]["products"][0]["dominant_transverse_decimal"]
        ),
        "shared_phase_node_rms": exp327["shared_phase_node_rms"],
        "normalized_gate_usage": normalized,
    }
    atomic_write(
        args.output.with_suffix(args.output.suffix + ".receipt.json"),
        canonical_json(receipt),
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Reconstruct Jones (2012) Figure 6 from the frozen source transcription.

This graph reports original symbolic claims, not modern orbit qualification.
It reads only checked-in source-transcription/audit JSON, not numerical orbit
artifacts or unresolved parameter-box associations.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from butterfly.scan import atomic_write, canonical_json, git_value


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTION_SHA256 = "6a5aba797473d40db9197d7a2ebe51195193f888613800584f406742376581da"
ASSET_AUDIT_SHA256 = "95ff6db8e96307773da1e89729597f2bf46a14abeca6fef7925edf8a74b60e32"
PAPER_SHA256 = "54b2a35bcfe50c5c2dc2f8ac1f3d3f98acbb2991dab7bc6e66cf61dc4b5ffb6f"
WORDS = (
    "C1", "C2", "C21", "CD0", "CD00", "CD01", "CD000", "CD001", "CD011",
    "CD0000", "CD0001", "CD0010", "CD0011", "CD0111", "CD00000", "CD00001",
    "CD00010", "CD00011", "CD00101", "CD00110", "CD00111", "CD01101", "CD01111",
)
MATCHED_EDGES = (
    ("CD0", "CD00"), ("CD01", "CD001"), ("CD00", "CD000"),
    ("CD011", "CD0011"), ("CD001", "CD0001"), ("CD000", "CD0000"),
    ("CD0010", "CD00010"), ("CD0011", "CD00011"),
    ("CD0001", "CD00001"), ("CD0000", "CD00000"),
)
ISOLATED_ORIGINS = {"CD011", "CD0010", "CD0111", "CD00101", "CD01101", "CD01111"}
ORPHAN_WORDS = {"CD00101", "CD00110", "CD01101", "CD01111"}
TEXT_EDGES = (
    ("C2", "CD0", "branch3-to-TTL-connection"),
    ("C21", "CD01", "branch3-to-TTL-connection"),
    ("C1", "CD01", "period-double"),
)
CLAIM_BOUNDARY = "Jones 2012 source reconstruction; not new orbit validation. Source-matched denotes the original report's geometry-and-symbol evidence category, not modern numerical qualification."


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def graph_from_transcription(transcription, audit):
    """Validate exact source semantics and return explicitly typed graph data."""
    if not isinstance(transcription, Mapping) or transcription.get("schema") != "butterfly.jones2012-source-transcription.v1":
        raise ValueError("the frozen Jones source transcription is required")
    if not isinstance(audit, Mapping) or audit.get("schema") != "butterfly.jones2012-figure6-asset-audit.v1":
        raise ValueError("the frozen Figure 6 asset audit is required")
    for document in (transcription, audit):
        if document["source"].get("arxiv_id") != "1201.4343v1" or document["source"].get("paper_sha256") != PAPER_SHA256:
            raise ValueError("source paper identity differs from the frozen Jones paper")
    if audit["frozen_transcription"].get("sha256") != TRANSCRIPTION_SHA256:
        raise ValueError("asset audit does not bind the frozen transcription")
    if audit["attachment_assessment"].get("status") != "not fully resolved":
        raise ValueError("parameter-to-word associations must remain unresolved")
    if transcription.get("claim_boundary") != "This is a source transcription and validation target. It is not new numerical evidence that the paths, partition, or transitions are dynamically correct.":
        raise ValueError("source reconstruction must not be reclassified as modern numerical validation")
    figure = transcription["figure6"]
    nodes = figure["nodes"]
    words = [row["word"] for row in nodes]
    if len(words) != 23 or len(set(words)) != 23 or set(words) != set(WORDS):
        raise ValueError("all 23 distinct transcribed words are required")
    for row in nodes:
        word = row["word"]
        if set(row) - {"word", "period", "isolated_branch3_origin", "branch3_connection", "period_double_marker"}:
            raise ValueError("source nodes must not acquire untranscribed metadata or validation flags")
        if isinstance(row["period"], bool) or row["period"] != len(word):
            raise ValueError("node period must equal its transcribed symbolic word length")
        for flag, expected in (
            ("isolated_branch3_origin", word in ISOLATED_ORIGINS),
            ("branch3_connection", word in {"C2", "C21"}),
            ("period_double_marker", word == "CD0010"),
        ):
            if row.get(flag, False) is not expected:
                raise ValueError(f"node {word} changes the original {flag} flag")
    matched = [(row["source"], row["target"]) for row in figure["matched_p_to_p_plus_1_transitions"]]
    if len(matched) != 10 or set(matched) != set(MATCHED_EDGES):
        raise ValueError("exactly the ten source-matched p-to-p+1 arrows are required")
    visual = figure["visual_only_transition"]
    if visual != {"source": "CD0111", "target": "CD00111"}:
        raise ValueError("the visual-only arrow must retain its separate status")
    text = [(row["source"], row["target"], row["kind"]) for row in figure["explicit_text_relationships"]]
    if len(text) != 3 or set(text) != set(TEXT_EDGES):
        raise ValueError("the two text connections and one text period doubling must remain distinct")
    edges = [{"source": source, "target": target, "category": "source_matched_p_to_p_plus_1", "modern_orbit_validated": False} for source, target in matched]
    edges.append({**visual, "category": "visual_only", "modern_orbit_validated": False})
    edges.extend({"source": source, "target": target, "category": "text_branch3_connection" if kind == "branch3-to-TTL-connection" else "text_period_double", "modern_orbit_validated": False} for source, target, kind in text)
    connected = {word for edge in edges for word in (edge["source"], edge["target"])}
    orphans = [word for word in words if word not in connected]
    if set(orphans) != ORPHAN_WORDS:
        raise ValueError("unconnected source words must not gain invented links")
    return {
        "nodes": [dict(row) for row in nodes], "edges": edges,
        "orphan_words": orphans, "edge_counts": dict(Counter(row["category"] for row in edges)),
        "modern_orbit_validated": False, "parameter_coordinates_assigned": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def load_graph(transcription_path, audit_path):
    """Bind source bytes before interpreting any graph or association claims."""
    raw, audit_raw = Path(transcription_path).read_bytes(), Path(audit_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != TRANSCRIPTION_SHA256:
        raise ValueError("source transcription SHA-256 mismatch")
    if hashlib.sha256(audit_raw).hexdigest() != ASSET_AUDIT_SHA256:
        raise ValueError("source asset audit SHA-256 mismatch")
    return graph_from_transcription(json.loads(raw), json.loads(audit_raw))


def graph_positions():
    """Period columns and compact chain rows, with no dynamical coordinates."""
    rows = {
        "C2": 0, "CD0": 0, "CD00": 0, "CD000": 0, "CD0000": 0, "CD00000": 0,
        "C1": 2.0, "C21": 1, "CD01": 1, "CD001": 1, "CD0001": 1, "CD00001": 1,
        "CD0010": 2, "CD00010": 2,
        "CD011": 3, "CD0011": 3, "CD00011": 3,
        "CD00101": 4, "CD00110": 5,
        "CD0111": 6, "CD00111": 6,
        "CD01101": 7, "CD01111": 8,
    }
    return {word: (1.8 * (len(word) - 2), row) for word, row in rows.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcription", type=Path, default=ROOT / "experiments/source-transcriptions/jones2012-figures-2-and-6.json")
    parser.add_argument("--asset-audit", type=Path, default=ROOT / "experiments/source-transcriptions/jones2012-figure6-asset-audit.json")
    parser.add_argument("--output", type=Path, default=ROOT / "paper/figures/fig33-jones-symbolic-chain.png")
    parser.add_argument("--receipt", type=Path, default=ROOT / "paper/figures/fig33-jones-symbolic-chain.png.receipt.json")
    parser.add_argument("--dpi", type=int, default=240)
    args = parser.parse_args(argv)
    try:
        graph = load_graph(args.transcription, args.asset_audit)
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"invalid source graph: {error}") from error
    positions = graph_positions()
    styles = {
        "source_matched_p_to_p_plus_1": ("#276573", "-", 2.0),
        "visual_only": ("#667085", (0, (4, 3)), 1.8),
        "text_branch3_connection": ("#3468AD", "-", 2.3),
        "text_period_double": ("#8B4B9B", "-.", 2.0),
    }
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 14, "savefig.facecolor": "white"}):
        fig, ax = plt.subplots(figsize=(13, 9))
        fig.subplots_adjust(left=0.05, right=0.975, bottom=0.09, top=0.86)
        ax.set_xlim(-0.85, 9.8)
        ax.set_ylim(8.55, -1.0)
        ax.axis("off")
        for period in range(2, 8):
            x = 1.8 * (period - 2)
            ax.text(x, -0.73, f"Period {period}", ha="center", va="center", fontsize=16, weight="bold", color="#344054")
            ax.plot([x, x], [-0.38, 8.35], color="#EEF0F3", lw=1.0, zorder=0)
        patches = {}
        for node in graph["nodes"]:
            word = node["word"]
            x, y = positions[word]
            isolated = node.get("isolated_branch3_origin", False)
            patch = FancyBboxPatch((x - 0.68, y - 0.30), 1.36, 0.60, boxstyle="round,pad=0.015,rounding_size=0.08", facecolor="#FCEBD6" if isolated else "#F8FAFC", edgecolor="#A86A2D" if isolated else "#8A9AAF", linewidth=1.4, zorder=3)
            ax.add_patch(patch)
            patches[word] = patch
            ax.text(x, y, word, ha="center", va="center", fontfamily="DejaVu Sans Mono", fontsize=18, weight="bold" if isolated else "normal", color="#794916" if isolated else "#25374C", zorder=4)
            if node.get("period_double_marker", False):
                ax.text(x + 0.59, y - 0.33, "†", ha="left", va="center", color="#8B4B9B", fontsize=15, weight="bold", zorder=5)
        for edge in graph["edges"]:
            color, linestyle, width = styles[edge["category"]]
            connection = "arc3,rad=0.17" if edge["category"] == "text_period_double" else "arc3,rad=0"
            ax.add_patch(FancyArrowPatch(positions[edge["source"]], positions[edge["target"]], patchA=patches[edge["source"]], patchB=patches[edge["target"]], shrinkA=4, shrinkB=4, arrowstyle="-|>", mutation_scale=16, connectionstyle=connection, color=color, linestyle=linestyle, linewidth=width, zorder=2))
        # Legend occupies empty lower-left graph space, never a source node.
        ax.add_patch(FancyBboxPatch((-0.67, 4.08), 6.76, 4.16, boxstyle="round,pad=0.12,rounding_size=0.1", facecolor="white", edgecolor="#E4E7EC", linewidth=1.0, zorder=1))
        ax.text(-0.40, 4.43, "What the source reports", fontsize=16, weight="bold", color="#344054", va="center")
        entries = [
            ("source_matched_p_to_p_plus_1", "10 reported geometry + symbol matches"),
            ("visual_only", "1 reported visual-attractor match only"),
            ("text_branch3_connection", "2 branch-3 connections stated in text"),
            ("text_period_double", "1 period doubling stated in text"),
        ]
        for index, (category, label) in enumerate(entries):
            y = 4.98 + index * 0.46
            color, linestyle, width = styles[category]
            ax.add_patch(FancyArrowPatch((-0.4, y), (0.42, y), arrowstyle="-|>", mutation_scale=16, linewidth=width, linestyle=linestyle, color=color, zorder=3))
            ax.text(0.62, y, label, fontsize=14, va="center", color="#344054")
        ax.add_patch(FancyBboxPatch((-0.4, 6.90), 0.80, 0.32, boxstyle="round,pad=0.02", facecolor="#FCEBD6", edgecolor="#A86A2D", zorder=3))
        ax.text(0.62, 7.06, "Original isolated-shrimp origin (bold)", fontsize=14, va="center", weight="bold", color="#794916")
        ax.text(-0.40, 7.54, "† CD0010 has an original doubling marker; no extra link.", fontsize=12.5, color="#667085", va="center")
        ax.text(-0.40, 7.96, "Four unconnected words are shown without invented arrows.", fontsize=12.5, color="#667085", va="center")
        fig.suptitle("Jones (2012)  |  The reported symbolic chains", x=0.05, y=0.975, ha="left", fontsize=21, weight="bold")
        fig.text(0.05, 0.92, "23 source words · Periods 2–7 · Source reconstruction, not new orbit validation", fontsize=15, color="#475467")
        fig.text(0.05, 0.035, "All arrow evidence is from Jones (2012), not a new numerical result. Layout is schematic; no parameter coordinates are assigned.", fontsize=12.5, color="#667085")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.output, dpi=args.dpi)
        plt.close(fig)
    receipt = {
        "schema": "butterfly.jones2012-symbolic-chain-figure.v1",
        "source_commit": git_value("rev-parse", "HEAD"),
        "source_dirty": bool(git_value("status", "--porcelain")),
        "script_sha256": file_hash(__file__), "transcription_sha256": file_hash(args.transcription),
        "asset_audit_sha256": file_hash(args.asset_audit), "paper_sha256": PAPER_SHA256,
        "figure_sha256": file_hash(args.output), "dpi": args.dpi,
        "matplotlib_version": matplotlib.__version__,
        "inputs": [str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path) for path in (args.transcription, args.asset_audit)],
        "raw_artifact_required_to_regenerate_figure": False,
        "node_words": [row["word"] for row in graph["nodes"]],
        "nodes": graph["nodes"], "edges": graph["edges"], "edge_counts": graph["edge_counts"],
        "orphan_words": graph["orphan_words"],
        "modern_orbit_validated": False, "parameter_coordinates_assigned": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    atomic_write(args.receipt, canonical_json(receipt))
    print(json.dumps({"figure": str(args.output), "sha256": receipt["figure_sha256"], "nodes": len(graph["nodes"]), "arrows": len(graph["edges"]), "modern_orbit_validated": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

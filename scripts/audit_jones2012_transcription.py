#!/usr/bin/env python3
"""Audit the machine-readable Jones Figures 2 and 6 source transcription."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from scipy.optimize import brentq


SCHEMA = "butterfly.jones2012-source-transcription.v1"
ALLOWED_SYMBOLS = frozenset("CD012")


def small_equilibrium_hopf_a_at_c(c: float, b: float) -> float:
    """Invert the regular small-equilibrium Hopf locus at fixed ``(b, c)``."""

    def large_r(a: float) -> float:
        return 0.5 * (c + math.sqrt(c * c - 4.0 * a * b))

    def residual(a: float) -> float:
        r = large_r(a)
        return a * (1.0 + r * r - a * r) - b

    return float(brentq(residual, 1e-12, min(b, c * c / (4.0 * b)) * (1.0 - 1e-12)))


def audit_transcription(document: dict) -> dict:
    if document.get("schema") != SCHEMA:
        raise ValueError("unsupported Jones source-transcription schema")
    source_hash = document["source"]["paper_sha256"]
    if len(source_hash) != 64 or any(char not in "0123456789abcdef" for char in source_hash):
        raise ValueError("paper_sha256 must be a lowercase SHA-256 digest")

    figure2 = document["figure2"]
    path_ids = {path["id"] for path in figure2["paths"]}
    if path_ids != {"L1", "L2"}:
        raise ValueError("Figure 2 must transcribe exactly L1 and L2")
    if figure2["printed_path_equations"] or figure2["printed_path_endpoint_coordinates"]:
        raise ValueError("the source does not print exact L1/L2 parameterizations")
    diagnostic = figure2["l1_hopf_consistency_diagnostic"]
    computed_hopf_a = small_equilibrium_hopf_a_at_c(
        float(diagnostic["reported_hub_height_c"]),
        float(document["reported_parameters"]["b"]),
    )
    if abs(computed_hopf_a - float(diagnostic["small_equilibrium_hopf_a"])) > 2e-15:
        raise ValueError("stored L1 Hopf-consistency diagnostic is stale")
    if not computed_hopf_a < float(diagnostic["figure_left_a_limit"]):
        raise ValueError("L1 Hopf point should lie outside the plotted a-range")

    figure6 = document["figure6"]
    nodes = figure6["nodes"]
    words = [node["word"] for node in nodes]
    if len(words) != len(set(words)):
        raise ValueError("Figure 6 node words must be unique")
    node_by_word = {node["word"]: node for node in nodes}
    for node in nodes:
        word = node["word"]
        if not word.startswith("C") or not set(word) <= ALLOWED_SYMBOLS:
            raise ValueError(f"invalid Figure 6 word: {word}")
        if len(word) != int(node["period"]):
            raise ValueError(f"word length and period disagree for {word}")

    verified = figure6["matched_p_to_p_plus_1_transitions"]
    visual = [figure6["visual_only_transition"]]
    for evidence, transitions in (("matched", verified), ("visual-only", visual)):
        for transition in transitions:
            source = transition["source"]
            target = transition["target"]
            if source not in node_by_word or target not in node_by_word:
                raise ValueError(f"{evidence} transition references an unknown word")
            if node_by_word[target]["period"] != node_by_word[source]["period"] + 1:
                raise ValueError(f"{evidence} transition is not p-to-p+1: {source}->{target}")
            expected = source[:2] + "0" + source[2:]
            if target != expected:
                raise ValueError(f"{evidence} transition violates the printed zero-insertion rule")

    for relationship in figure6["explicit_text_relationships"]:
        if relationship["source"] not in node_by_word or relationship["target"] not in node_by_word:
            raise ValueError("text relationship references an unknown word")
    landmarks = figure6["parameter_landmarks"]
    if len(landmarks) != 10 or any(float(row["b"]) != 0.2 for row in landmarks):
        raise ValueError("expected the ten fixed-b Figure 6 parameter landmarks")

    return {
        "passed": True,
        "path_count": len(path_ids),
        "node_count": len(nodes),
        "matched_transition_count": len(verified),
        "visual_only_transition_count": len(visual),
        "parameter_landmark_count": len(landmarks),
        "computed_l1_height_hopf_a": computed_hopf_a,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    result = audit_transcription(json.loads(args.source.read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

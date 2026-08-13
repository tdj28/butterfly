#!/usr/bin/env python3
"""Audit Jones/Barrio critical membership across a frozen smoothing ensemble."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.jones-scale-ensemble-residual-manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def point_assignment(orbit_values, critical_points, domain) -> dict:
    """Assign ordered critical points to distinct phases by normalized distance."""

    orbit = np.asarray(orbit_values, dtype=float)
    criticals = np.asarray(critical_points, dtype=float)
    lower, upper = map(float, domain)
    width = upper - lower
    if orbit.ndim != 1 or criticals.shape != (2,) or width <= 0.0:
        return {"resolved": False, "reason": "invalid orbit, criticals, or domain"}
    rows = []
    for first in range(len(orbit)):
        for second in range(len(orbit)):
            if first == second:
                continue
            indices = (first, second)
            residuals = tuple(
                (float(orbit[orbit_index]) - float(criticals[critical_index])) / width
                for critical_index, orbit_index in enumerate(indices)
            )
            rows.append((max(map(abs, residuals)), sum(map(abs, residuals)), indices, residuals))
    best = min(rows, key=lambda row: (row[0], row[1], row[2]))
    return {
        "resolved": True,
        "orbit_indices": list(best[2]),
        "orbit_values": [float(orbit[index]) for index in best[2]],
        "normalized_signed_residuals": [float(value) for value in best[3]],
        "maximum_absolute_residual": float(best[0]),
        "sum_absolute_residual": float(best[1]),
    }


def signed_residual_bracket_cells(rows: list[dict]) -> list[dict]:
    """Find cells bracketing both residuals in every scale/support/step view."""

    lookup = {
        tuple(row["grid_index"]): row
        for row in rows
        if row.get("eligible") and row.get("grid_index") is not None
    }
    cells = []
    for i, j in sorted(lookup):
        indices = ((i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1))
        if any(index not in lookup for index in indices):
            continue
        corners = [lookup[index] for index in indices]
        assignments = {tuple(row["common_assignment_indices"]) for row in corners}
        reconstruction_keys = [set(row["reconstructions"]) for row in corners]
        if len(assignments) != 1 or len({frozenset(keys) for keys in reconstruction_keys}) != 1:
            continue
        reconstructions = []
        passed = True
        for key in sorted(reconstruction_keys[0]):
            residual_ranges = []
            for residual_index in range(2):
                values = [
                    float(row["reconstructions"][key]["normalized_signed_residuals"][residual_index])
                    for row in corners
                ]
                bounds = [min(values), max(values)]
                residual_ranges.append(bounds)
                if bounds[0] > 0.0 or bounds[1] < 0.0:
                    passed = False
            reconstructions.append({"key": key, "signed_residual_ranges": residual_ranges})
        if passed:
            a_values = [float(row["parameters"]["a"]) for row in corners]
            c_values = [float(row["parameters"]["c"]) for row in corners]
            cells.append(
                {
                    "lower_grid_index": [i, j],
                    "corner_ids": [row["id"] for row in corners],
                    "a_bounds": [min(a_values), max(a_values)],
                    "c_bounds": [min(c_values), max(c_values)],
                    "assignment_indices": list(next(iter(assignments))),
                    "reconstructions": reconstructions,
                }
            )
    return cells


def _candidate_row(candidate: dict, receipt_rows: list[tuple[str, dict]], manifest: dict) -> dict:
    axis = int(manifest["return_coordinate"]["axis"])
    orbit_values = np.asarray(candidate["section_states"], dtype=float)[:, axis]
    smoothing_indices = [int(index) for index in manifest["smoothing_indices"]]
    reconstructions = {}
    normalized_criticals = [[], []]
    reasons = []
    for profile_name, row in receipt_rows:
        for support in row["supports"]:
            domain = support["source_domain"]
            lower, upper = map(float, domain)
            width = upper - lower
            for smoothing_index in smoothing_indices:
                result = support["results"][smoothing_index]
                key = f"{profile_name}/{support['name']}/s{smoothing_index}"
                if not result.get("resolved") or result.get("branch_count") != 3:
                    reasons.append(f"{key}: requires resolved three-branch result")
                    continue
                criticals = [float(value) for value in result["critical_points"]]
                assignment = point_assignment(orbit_values, criticals, domain)
                if not assignment["resolved"]:
                    reasons.append(f"{key}: {assignment['reason']}")
                    continue
                normalized = [(value - lower) / width for value in criticals]
                for index, value in enumerate(normalized):
                    normalized_criticals[index].append(float(value))
                reconstructions[key] = {
                    "profile": profile_name,
                    "support": support["name"],
                    "smoothing_index": smoothing_index,
                    "smoothing": float(support["smoothing_values"][smoothing_index]),
                    "source_domain": [lower, upper],
                    "critical_points": criticals,
                    "normalized_critical_points": normalized,
                    **assignment,
                }
    expected = len(receipt_rows) * 2 * len(smoothing_indices)
    assignments = {
        tuple(row["orbit_indices"]) for row in reconstructions.values()
    }
    complete = len(reconstructions) == expected
    common_assignment = len(assignments) == 1
    critical_spans = [
        max(values, default=float("inf")) - min(values, default=-float("inf"))
        for values in normalized_criticals
    ]
    maximum_critical_span = max(critical_spans)
    maximum_absolute_residual = max(
        (
            abs(value)
            for row in reconstructions.values()
            for value in row["normalized_signed_residuals"]
        ),
        default=float("inf"),
    )
    acceptance = manifest["acceptance"]
    eligible = bool(
        complete
        and common_assignment
        and maximum_critical_span
        <= float(acceptance["maximum_normalized_critical_location_span"])
    )
    return {
        "id": candidate["id"],
        "grid_index": candidate.get("grid_index"),
        "parameters": candidate["parameters"],
        "complete": complete,
        "reconstruction_count": len(reconstructions),
        "common_assignment": common_assignment,
        "common_assignment_indices": list(next(iter(assignments))) if common_assignment else None,
        "normalized_critical_spans": critical_spans,
        "maximum_normalized_critical_span": maximum_critical_span,
        "maximum_absolute_residual": maximum_absolute_residual,
        "direct_gate_passed": bool(
            eligible
            and maximum_absolute_residual
            <= float(acceptance["maximum_direct_absolute_residual"])
        ),
        "eligible": eligible,
        "reasons": reasons,
        "reconstructions": reconstructions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()

    manifest_bytes = args.manifest.read_bytes()
    receipt_bytes = args.receipt.read_bytes()
    candidate_bytes = args.candidates.read_bytes()
    manifest = json.loads(manifest_bytes)
    receipt = json.loads(receipt_bytes)
    candidate_document = json.loads(candidate_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported scale-ensemble residual manifest")
    for evidence in manifest["evidence"]:
        if sha256_file(Path(evidence["path"])) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    if sha256_bytes(receipt_bytes) != manifest["receipt_input_sha256"]:
        raise SystemExit("receipt input hash mismatch")
    if sha256_bytes(candidate_bytes) != manifest["candidate_input_sha256"]:
        raise SystemExit("candidate input hash mismatch")
    if len(args.source_commit) != 40:
        raise SystemExit("a full source commit is required")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("source commit mismatch")

    qualified_ids = {
        row["id"] for row in receipt["combined_candidates"] if row["passed"]
    }
    if len(qualified_ids) != int(manifest["expected_candidate_count"]):
        raise SystemExit("unexpected EXP-201 qualified candidate count")
    candidate_lookup = {row["id"]: row for row in candidate_document["candidates"]}
    profile_lookup = {
        identifier: [
            (profile["name"], row)
            for profile in receipt["profiles"]
            for row in profile["rows"]
            if row["id"] == identifier
        ]
        for identifier in qualified_ids
    }
    rows = [
        _candidate_row(candidate_lookup[identifier], profile_lookup[identifier], manifest)
        for identifier in sorted(qualified_ids)
    ]
    eligible = [row for row in rows if row["eligible"]]
    ranked = sorted(
        eligible,
        key=lambda row: (row["maximum_absolute_residual"], row["id"]),
    )
    direct = [row for row in ranked if row["direct_gate_passed"]]
    bracket_cells = signed_residual_bracket_cells(rows)
    acceptance = manifest["acceptance"]
    coverage_passed = len(eligible) >= int(acceptance["minimum_eligible_candidates"])
    direct_passed = bool(coverage_passed and direct)
    bracket_passed = bool(
        coverage_passed
        and len(bracket_cells) >= int(acceptance["minimum_signed_bracket_cells"])
    )
    passed = direct_passed or bracket_passed
    output = {
        "schema": "butterfly.jones-scale-ensemble-residual.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "receipt_input_sha256": sha256_bytes(receipt_bytes),
        "candidate_input_sha256": sha256_bytes(candidate_bytes),
        "source": {
            "declared_commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "smoothing_indices": manifest["smoothing_indices"],
        "smoothing_values": manifest["smoothing_values"],
        "combined_candidates": rows,
        "eligible_candidate_count": len(eligible),
        "coverage_passed": coverage_passed,
        "ranked_candidate_ids": [row["id"] for row in ranked],
        "selected_candidate": ranked[0] if ranked else None,
        "direct_candidate_ids": [row["id"] for row in direct],
        "direct_candidate_passed": direct_passed,
        "signed_residual_bracket_cells": bracket_cells,
        "signed_residual_bracket_passed": bracket_passed,
        "passed": passed,
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "eligible": len(eligible),
                "direct": len(direct),
                "brackets": len(bracket_cells),
                "passed": passed,
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run published Rössler classifier controls and emit a provenance receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from butterfly import (
    LyapunovConfig,
    RosslerParameters,
    SolverConfig,
    classify_fundamental_period,
    classify_with_lyapunov,
    collect_crossings,
    legacy_rossler_section,
    lyapunov_block_estimates,
    lyapunov_spectrum,
)
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.manifest.read_bytes()
    manifest = json.loads(raw)
    if manifest.get("schema") != "butterfly.classifier-controls.v1":
        raise SystemExit("unsupported classifier-control manifest")

    solver = SolverConfig(**manifest["solver"])
    crossing_config = manifest["crossings"]
    lyapunov_config = manifest["lyapunov"]
    initial_state = tuple(manifest["initial_state"])
    b = float(manifest["fixed_parameters"]["b"])
    c = float(manifest["fixed_parameters"]["c"])
    results = []

    for case in manifest["cases"]:
        parameters = RosslerParameters(a=float(case["a"]), b=b, c=c)
        crossings = collect_crossings(
            parameters,
            initial_state,
            legacy_rossler_section(parameters),
            transient=float(crossing_config["transient"]),
            observation_horizon=float(crossing_config["observation_horizon"]),
            max_crossings=int(crossing_config["max_crossings"]),
            config=solver,
        )
        recurrence = classify_fundamental_period(
            crossings.states,
            max_period=int(crossing_config["max_period"]),
            required_repeats=int(crossing_config["required_repeats"]),
            atol=float(crossing_config["atol"]),
            rtol=float(crossing_config["rtol"]),
        )
        spectrum = lyapunov_spectrum(
            parameters,
            initial_state,
            config=LyapunovConfig(
                transient=float(lyapunov_config["transient"]),
                duration=float(lyapunov_config["duration"]),
                qr_interval=float(lyapunov_config["qr_interval"]),
                solver=solver,
            ),
        )
        blocks = lyapunov_block_estimates(
            spectrum, blocks=int(lyapunov_config["blocks"])
        )
        standard_error = np.std(blocks, axis=0, ddof=1) / np.sqrt(len(blocks))
        classification = classify_with_lyapunov(
            recurrence, spectrum.exponents, standard_error
        )
        expected = str(case["expected_label"])
        results.append(
            {
                "a": parameters.a,
                "b": parameters.b,
                "c": parameters.c,
                "paper_role": case["paper_role"],
                "expected_label": expected,
                "observed_label": classification.label.value,
                "match": classification.label.value == expected,
                "fundamental_period": classification.fundamental_period,
                "confidence": classification.confidence,
                "classification_reason": classification.reason,
                "evidence": list(classification.evidence),
                "crossing_count": len(crossings.times),
                "recurrence_error": recurrence.recurrence_error,
                "recurrence_tolerance": recurrence.recurrence_tolerance,
                "lyapunov_exponents": spectrum.exponents.tolist(),
                "lyapunov_block_standard_error": standard_error.tolist(),
                "trace_identity_error": spectrum.trace_identity_error,
            }
        )

    receipt = {
        "schema": "butterfly.classifier-controls-receipt.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(raw),
        "paper_source": manifest["source"],
        "all_expected_labels_matched": all(result["match"] for result in results),
        "results": results,
        "source": {
            "commit": git_value("rev-parse", "HEAD"),
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
    }
    atomic_write(args.output, canonical_json(receipt))
    print(json.dumps({"output": str(args.output), "passed": receipt["all_expected_labels_matched"]}))
    return 0 if receipt["all_expected_labels_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

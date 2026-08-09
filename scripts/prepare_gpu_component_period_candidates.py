#!/usr/bin/env python3
"""Extract a geometry-only sample of GPU period-component cycles."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform

import numpy as np

from butterfly import classify_fundamental_period
from butterfly.scan import atomic_write, canonical_json, git_value, sha256_bytes


SCHEMA = "butterfly.gpu-component-period-candidates-manifest.v1"


def farthest_component_sample(
    point_indices,
    parameter_rows: dict[int, tuple[float, float]],
    *,
    sample_count: int,
    anchor_point_index: int,
) -> tuple[list[int], float]:
    """Return a deterministic normalized farthest-point component sample."""

    indices = np.asarray(sorted(map(int, point_indices)), dtype=int)
    if not 1 <= sample_count <= len(indices):
        raise ValueError("sample count must be within the component size")
    if anchor_point_index not in set(indices.tolist()):
        raise ValueError("anchor point is not in the component")
    coordinates = np.asarray([parameter_rows[int(index)] for index in indices], dtype=float)
    spans = np.ptp(coordinates, axis=0)
    if np.any(spans <= 0.0):
        raise ValueError("component must span both sampled parameter axes")
    normalized = (coordinates - np.min(coordinates, axis=0)) / spans
    anchor_position = int(np.flatnonzero(indices == anchor_point_index)[0])
    selected_positions = [anchor_position]
    selected_mask = np.zeros(len(indices), dtype=bool)
    selected_mask[anchor_position] = True
    minimum_squared_distance = np.sum(
        (normalized - normalized[anchor_position]) ** 2,
        axis=1,
    )
    minimum_squared_distance[anchor_position] = -1.0
    while len(selected_positions) < sample_count:
        position = int(np.argmax(minimum_squared_distance))
        selected_positions.append(position)
        selected_mask[position] = True
        squared_distance = np.sum((normalized - normalized[position]) ** 2, axis=1)
        minimum_squared_distance = np.minimum(
            minimum_squared_distance,
            squared_distance,
        )
        minimum_squared_distance[selected_mask] = -1.0
    remaining = minimum_squared_distance[~selected_mask]
    fill_radius = 0.0 if len(remaining) == 0 else float(np.sqrt(np.max(remaining)))
    return [int(indices[position]) for position in selected_positions], fill_radius


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != SCHEMA:
        raise SystemExit("unsupported GPU component-candidate manifest")
    if len(args.source_commit) != 40 or any(
        character not in "0123456789abcdef"
        for character in args.source_commit.lower()
    ):
        raise SystemExit("--source-commit must be a full hexadecimal Git commit")
    observed_commit = git_value("rev-parse", "HEAD")
    if observed_commit is not None and observed_commit != args.source_commit:
        raise SystemExit("declared source commit differs from the checked-out commit")
    for evidence in manifest.get("evidence", ()):
        raw = Path(evidence["path"]).read_bytes()
        if sha256_bytes(raw) != evidence["sha256"]:
            raise SystemExit(f"evidence hash mismatch: {evidence['path']}")
    documents = {}
    document_bytes = {}
    for name, declared in manifest["inputs"].items():
        raw = Path(declared["path"]).read_bytes()
        if sha256_bytes(raw) != declared["sha256"]:
            raise SystemExit(f"input hash mismatch: {name}")
        document_bytes[name] = raw
        documents[name] = json.loads(raw)
    frame = documents["frame"]
    frame_receipt = documents["frame_receipt"]
    component = documents["component"]
    if frame_receipt.get("result_sha256") != sha256_bytes(document_bytes["frame"]):
        raise SystemExit("frame receipt does not bind the frame")
    if component.get("frame_sha256") != sha256_bytes(document_bytes["frame"]):
        raise SystemExit("component does not bind the frame")
    shape = tuple(map(int, frame["shape"]))
    rows_by_index = {int(row["point_index"]): row for row in frame["rows"]}
    parameters_by_index = {
        index: (float(row["a"]), float(row["c"]))
        for index, row in rows_by_index.items()
    }
    anchor_grid_index = tuple(map(int, component["anchor_index"]))
    anchor_point_index = anchor_grid_index[0] * shape[1] + anchor_grid_index[1]
    selection = manifest["selection"]
    selected_indices, fill_radius = farthest_component_sample(
        component["point_indices"],
        parameters_by_index,
        sample_count=int(selection["sample_count"]),
        anchor_point_index=anchor_point_index,
    )

    try:
        import torch
        import triton
        from gpu_crossing_qualify import integrate_gpu_crossings
    except ImportError as error:  # pragma: no cover - CUDA worker only
        raise SystemExit("CUDA, PyTorch, and Triton are required") from error
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available")
    parameter_array = np.asarray(
        [
            [
                rows_by_index[index]["a"],
                rows_by_index[index]["b"],
                rows_by_index[index]["c"],
            ]
            for index in selected_indices
        ],
        dtype=np.float64,
    )
    integration = manifest["integration"]
    initial_states = np.tile(
        np.asarray(integration["initial_state"], dtype=np.float64),
        (len(parameter_array), 1),
    )
    crossings, performance = integrate_gpu_crossings(
        parameter_array,
        initial_states,
        transient=float(integration["transient"]),
        observation_horizon=float(integration["observation_horizon"]),
        dt=float(integration["dt"]),
        chunk_steps=int(integration["chunk_steps"]),
        max_crossings=int(integration["max_crossings"]),
        dtype=torch.float64,
    )
    classifier = manifest["classifier"]
    expected_period = int(selection["target_period"])
    candidates = []
    for selection_index, (point_index, parameters, states) in enumerate(
        zip(selected_indices, parameter_array, crossings, strict=True)
    ):
        classification = classify_fundamental_period(
            states,
            max_period=int(classifier["max_period"]),
            required_repeats=int(classifier["required_repeats"]),
            atol=float(classifier["atol"]),
            rtol=float(classifier["rtol"]),
        )
        enough_states = len(states) >= 2 * expected_period
        finite = bool(np.all(np.isfinite(states[-expected_period:]))) if enough_states else False
        passed = bool(
            enough_states
            and finite
            and classification.fundamental_period == expected_period
        )
        candidates.append(
            {
                "id": f"component-sample-{selection_index:03d}",
                "selection_order": selection_index,
                "point_index": point_index,
                "grid_index": list(divmod(point_index, shape[1])),
                "parameters": {
                    "a": float(parameters[0]),
                    "b": float(parameters[1]),
                    "c": float(parameters[2]),
                },
                "classification": {
                    "label": classification.label.value,
                    "fundamental_period": classification.fundamental_period,
                    "recurrence_error": classification.recurrence_error,
                    "recurrence_tolerance": classification.recurrence_tolerance,
                    "crossing_count": len(states),
                },
                "section_states": states[-expected_period:].tolist()
                if enough_states
                else [],
                "passed": passed,
            }
        )
    passed_count = sum(row["passed"] for row in candidates)
    properties = torch.cuda.get_device_properties(0)
    output = {
        "schema": "butterfly.gpu-component-period-candidates.v1",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "source": {
            "declared_commit": args.source_commit,
            "observed_git_commit": observed_commit,
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
        "input_sha256": {
            name: sha256_bytes(raw) for name, raw in document_bytes.items()
        },
        "selection": {
            "method": "normalized deterministic farthest-point sampling anchored at the source landmark",
            "target_period": expected_period,
            "component_point_count": len(component["point_indices"]),
            "sample_count": len(selected_indices),
            "point_indices": selected_indices,
            "normalized_fill_radius": fill_radius,
        },
        "performance": performance,
        "environment": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "triton": triton.__version__,
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_bytes": properties.total_memory,
            "gpu_compute_capability": [properties.major, properties.minor],
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "passed_candidate_count": passed_count,
        "candidates": candidates,
        "passed": passed_count >= int(manifest["acceptance"]["minimum_passed_candidates"]),
        "claim_scope": manifest["claim_scope"],
    }
    output_bytes = canonical_json(output)
    atomic_write(args.output, output_bytes)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha256_bytes(output_bytes),
                "passed": output["passed"],
                "passed_candidate_count": passed_count,
                "normalized_fill_radius": fill_radius,
            },
            sort_keys=True,
        )
    )
    return 0 if output["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

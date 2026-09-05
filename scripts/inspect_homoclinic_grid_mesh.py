#!/usr/bin/env python3
"""Inspect the frozen EXP-476 meshes without integrating or solving any orbit.

This is a post-result diagnostic, not a protocol revision or new acceptance
test. It reconstructs the saved piecewise cubic Hermite polynomials and the
installed SciPy residual estimator from saved nodes, states, and analytic RHS
values only. No call to solve_bvp, solve_ivp, or an optimizer is made.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.integrate._bvp import collocation_fun, create_spline, estimate_rms_residuals


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_SHA256 = "c9818275ed3c585934cdeaa85857b04a5e9a6e1a6400f426a5cbf6e06d5b95bc"
SOURCE_COMMIT = "af90d04e6b484733bb2535a453157c4830691a34"


def quantiles(values):
    points = [0.0, 0.01, 0.1, 0.5, 0.9, 0.99, 1.0]
    return dict(zip((str(point) for point in points), np.quantile(values, points).tolist()))


def normalized_rhs(_mesh, states, parameters):
    a, b, c, duration = parameters
    x, y, z = states
    return duration * np.vstack((-y - z, x + a * y, b + z * (x - c)))


def runs(mask, mesh, duration):
    changes = np.diff(np.r_[False, mask, False].astype(int))
    starts, stops = np.flatnonzero(changes == 1), np.flatnonzero(changes == -1)
    groups = [{
        "first_interval": int(start), "interval_count": int(stop - start),
        "normalized_span": [float(mesh[start]), float(mesh[stop])],
        "physical_duration": float((mesh[stop] - mesh[start]) * duration),
    } for start, stop in zip(starts, stops)]
    return sorted(groups, key=lambda group: group["interval_count"], reverse=True)


def inspect_case(row, fixed, node_cap):
    mesh = np.asarray(row["normalized_mesh"], dtype=float)
    states = np.asarray(row["states"], dtype=float).T
    summary = row["collocation"]
    if states.shape != (3, len(mesh)) or not np.all(np.isfinite(mesh)) or not np.all(np.isfinite(states)):
        raise ValueError("saved mesh/states are malformed or nonfinite")
    h = np.diff(mesh)
    if not np.all(h > 0):
        raise ValueError("saved mesh is not strictly increasing")
    a, duration = summary["parameter"], summary["flight_time"]
    parameters = (a, fixed["b"], fixed["c"], duration)
    # These three SciPy helpers evaluate algebra and spline polynomials only.
    # Their source hashes below bind this use of an internal diagnostic API.
    col_res, _middle_states, f, f_middle = collocation_fun(normalized_rhs, states, parameters, mesh, h)
    middle_residual = 1.5 * col_res / h
    spline = create_spline(states, f, mesh, h)
    rms = estimate_rms_residuals(normalized_rhs, spline, mesh, h, parameters, middle_residual.copy(), f_middle)
    peak = int(np.argmax(rms))
    tolerance = row["case"]["tolerance"]
    insert_one = (rms > tolerance) & (rms < 100.0 * tolerance)
    insert_two = rms >= 100.0 * tolerance
    requested = int(np.sum(insert_one) + 2 * np.sum(insert_two))
    tiny = h < 1e-10
    delta = np.diff(states, axis=1)
    ulps = np.maximum(np.abs(np.spacing(states[:, :-1])), np.abs(np.spacing(states[:, 1:])))
    increment_ulps = np.abs(delta) / ulps
    midpoint = mesh[:-1] + 0.5 * h
    offset = 0.5 * h * np.sqrt(3.0 / 7.0)
    residuals = []
    for points in (midpoint + offset, midpoint - offset):
        values = spline(points)
        rhs = normalized_rhs(points, values, parameters)
        residuals.append((spline(points, 1) - rhs) / (1.0 + np.abs(rhs)))
    component_rms = np.sqrt(0.5 * (
        32.0 / 45.0 * (middle_residual / (1.0 + np.abs(f_middle)))**2
        + 49.0 / 90.0 * (residuals[0]**2 + residuals[1]**2)
    ))
    worst = np.argsort(rms)[-10:][::-1]
    diagnostic = {
        "case": row["case"], "original_status": row["status"],
        "original_solver_status": summary["solver_status"],
        "nodes": len(mesh), "iterations": summary["iterations"],
        "flight_time": duration, "parameter": a,
        "normalized_spacing_quantiles": quantiles(h),
        "physical_spacing_quantiles": quantiles(h * duration),
        "intervals_below_1e-10": int(np.sum(tiny)),
        "tiny_interval_groups": runs(tiny, mesh, duration),
        "identical_adjacent_state_vectors": int(np.sum(np.all(delta == 0.0, axis=0))),
        "state_increment_norm_quantiles": quantiles(np.linalg.norm(delta, axis=0)),
        "minimum_component_increment_in_ulps": np.min(increment_ulps, axis=1).tolist(),
        "intervals_with_component_increment_at_most_32_ulps": np.sum(increment_ulps <= 32.0, axis=1).tolist(),
        "reported_maximum_relative_rms": summary["maximum_collocation_relative_rms"],
        "recomputed_maximum_relative_rms": float(rms[peak]),
        "recomputed_minus_reported_maximum": float(rms[peak] - summary["maximum_collocation_relative_rms"]),
        "relative_rms_quantiles": quantiles(rms),
        "intervals_exceeding_tolerance": int(np.sum(rms > tolerance)),
        "exceeding_tolerance_groups": runs(rms > tolerance, mesh, duration),
        "maximum_rms_outside_tiny_intervals": float(np.max(rms[~tiny])),
        "requested_new_nodes_under_scipy_rule": requested,
        "next_mesh_nodes_under_scipy_rule": int(len(mesh) + requested),
        "frozen_maximum_nodes": node_cap,
        "node_cap_would_be_exceeded": bool(len(mesh) + requested > node_cap),
        "saved_replay": row["replay"],
        "worst_intervals": [{
            "index": int(index), "normalized_span": mesh[index:index + 2].tolist(),
            "normalized_spacing": float(h[index]), "physical_spacing": float(h[index] * duration),
            "relative_rms": float(rms[index]), "component_relative_rms": component_rms[:, index].tolist(),
            "left_state": states[:, index].tolist(), "right_state": states[:, index + 1].tolist(),
            "state_increment": delta[:, index].tolist(),
            "component_increment_in_ulps": increment_ulps[:, index].tolist(),
            "absolute_collocation_state_balance_defect": np.abs(col_res[:, index]).tolist(),
            "midpoint_relative_derivative_defect": (middle_residual[:, index] / (1.0 + np.abs(f_middle[:, index]))).tolist(),
            "one_ulp_derivative_scale": (ulps[:, index] / h[index] / (1.0 + np.abs(f_middle[:, index]))).tolist(),
        } for index in worst],
    }
    return diagnostic


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=ROOT / "artifacts/EXP-476/receipt.json")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/EXP-476/mesh-diagnostic.json")
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("diagnostic output already exists; refusing to overwrite")
    raw = args.receipt.read_bytes()
    if hashlib.sha256(raw).hexdigest() != RECEIPT_SHA256:
        raise SystemExit("raw EXP-476 receipt hash mismatch")
    receipt = json.loads(raw)
    if receipt["experiment_id"] != "EXP-476" or receipt["source"]["commit"] != SOURCE_COMMIT or receipt["source"]["dirty"]:
        raise SystemExit("unexpected frozen experiment/source identity")
    manifest_path = ROOT / "experiments/manifests/EXP-476-homoclinic-radius-tolerance-grid.json"
    manifest_raw = manifest_path.read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != receipt["manifest_sha256"]:
        raise SystemExit("frozen manifest hash mismatch")
    manifest = json.loads(manifest_raw)
    result = {
        "schema": "butterfly.homoclinic-grid-mesh-inspection.v1",
        "experiment_id": "EXP-476", "receipt_sha256": RECEIPT_SHA256,
        "source_commit": SOURCE_COMMIT, "manifest_sha256": receipt["manifest_sha256"],
        "diagnostic_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "scipy_helper_source_sha256": {
            function.__name__: hashlib.sha256(inspect.getsource(function).encode()).hexdigest()
            for function in (collocation_fun, create_spline, estimate_rms_residuals)
        },
        "scope": "post-result algebraic inspection of saved arrays only; no integration, optimization, new orbit, changed cap, or acceptance reclassification",
        "cases": [inspect_case(row, manifest["fixed_parameters"], manifest["budget"]["maximum_nodes"])
                  for row in receipt["cases"] if "states" in row],
        "limitations": [
            "only the final mesh is saved; the sequence of adaptivity decisions is not reconstructed",
            "one-ulp derivative scale is a floating-point sensitivity indicator, not an error bound",
            "endpoint replay defects and interval-relative derivative residuals are different diagnostics",
            "post-result mesh inspection cannot convert the failed frozen case into a pass",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as destination:
        destination.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n")
    print(json.dumps({"output": str(args.output), "cases": len(result["cases"]), "target_integrations": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

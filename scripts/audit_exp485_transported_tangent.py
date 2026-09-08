#!/usr/bin/env python3
"""Read-only full-grid EXP-485 replay; no target integration or paid service."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters
from scripts import run_exp485_transported_tangent as run
from scripts import audit_exp484_return_geometry as prior

SOURCE = "af72692499126fce3da0d887679d8ad384ffad69"


def descriptive_metrics(rows):
    """Post-run display summaries; sign changes are NOT certified fold brackets."""
    cases = {}
    for case in sorted({r["case"] for r in rows}):
        selected = sorted([r for r in rows if r["case"] == case], key=lambda r: r["initial_state"][0])
        directions = [r["audit"]["direction"] for r in selected if r["audit"]["direction"] is not None]
        defined = [r for r in selected if r["audit"]["qualified"] and r["audit"]["direction"]["projected"]["DOP853"]["graph_defined"]]
        ids = {r["bin"] for r in defined}
        changes = []
        for left, right in zip(selected[:-1], selected[1:]):
            if left["bin"] not in ids or right["bin"] not in ids:
                continue
            values = [r["audit"]["direction"]["projected"]["DOP853"]["x_graph_derivative"] for r in (left, right)]
            if values[0]*values[1] < 0:
                changes.append(dict(bins=[left["bin"], right["bin"]],
                                    observed_x=[left["initial_state"][0], right["initial_state"][0]], derivatives=values))
        cases[case] = dict(points=len(selected), distinct_seeds=len({r["global_seed_id"] for r in selected}),
            qualified_points=sum(r["audit"]["qualified"] for r in selected), defined_qualified_x_graph_points=len(defined),
            unreported_x_graph_bins=[r["bin"] for r in selected if r["bin"] not in ids],
            maximum_history_angle=max((v for d in directions for v in d["history_angles"].values()), default=None),
            maximum_solver_angle=max((v for d in directions for v in d["solver_angles"]), default=None),
            maximum_coordinate_partial_difference=max((abs(r["audit"]["direction"]["projected"]["DOP853"]["x_graph_derivative"]-r["audit"]["direction"]["projected"]["DOP853"]["coordinate_partial"]) for r in defined), default=None),
            descriptive_adjacent_sign_changes=changes)
    return cases


def independently_check_history(matrices, rows):
    """Unrenormalized product plus covariance eigenvector, separate from runner.

    Finite float products are checked explicitly. This independent algebraic
    implementation is not an independent experiment or scientific reviewer.
    """
    errors = []
    for row in rows:
        product = np.eye(2)
        for matrix in matrices[-row["depth"]:]:
            product = np.asarray(matrix) @ product
        scale = np.max(np.abs(product))
        if not np.isfinite(product).all() or scale == 0:
            raise ValueError("independent product became nonfinite or zero")
        product /= scale
        _, vectors = np.linalg.eigh(product @ product.T)
        direction = vectors[:, -1]
        saved = np.asarray(row["direction"])
        angle = float(np.arctan2(abs(np.linalg.det(np.column_stack([direction, saved]))), abs(direction @ saved)))
        singular = np.linalg.svd(product, compute_uv=False)
        ratio = singular[-1]/singular[0]
        if angle > 1e-9 or not np.isclose(ratio, row["singular_ratio"], atol=1e-12, rtol=1e-6):
            raise ValueError("independent endpoint direction or singular ratio differs")
        errors.append(angle)
    return errors


def audit(target, expected_sha):
    if sha256(target/"summary.json") != expected_sha:
        raise ValueError("completed EXP-485 summary anchor changed")
    result = json.loads((target/"summary.json").read_bytes())
    if result["status"] != "completed" or inventory(target, omit=("summary.json",)) != result["files"]:
        raise ValueError("incomplete or changed target inventory")
    plan = json.loads(run.PLAN.read_bytes())
    binding = result["binding"]
    if (binding["source_commit"] != SOURCE or binding["plan_sha256"] != sha256(run.PLAN)
            or binding["source_files"] != {p: sha256(ROOT/p) for p in run.SOURCE_FILES}
            or json.loads((target/"binding.json").read_bytes()) != binding):
        raise ValueError("frozen source/plan binding changed")
    marker = ROOT/"artifacts/EXP-485/target-once.json"
    if sha256(marker) != result["target_slot_sha256"] or json.loads(marker.read_bytes()) != binding:
        raise ValueError("consumed experiment slot changed")
    # No integrations: replay original geometry audit and exact raw histories.
    prior.audit()
    selections = run.prepare(plan)
    if selections != json.loads((target/"selection.json").read_bytes()):
        raise ValueError("reconstructed raw history selection differs")
    controls = json.loads((target/"controls.json").read_bytes())
    if [c["method"] for c in controls["flow"]] != plan["solvers"]:
        raise ValueError("analytic solver control grid differs")
    for row in controls["flow"]:
        r = row["result"]
        if not row["passed"] or r["status"] != "returned" or abs(r["return_time"]-2*np.pi) >= 1e-9 or np.max(np.abs(np.asarray(r["return_jacobian"])-np.diag([1., np.exp(-.3*2*np.pi)]))) >= 1e-9:
            raise ValueError("analytic flow control differs from known solution")
    if (not controls["tangent_positive"]["direction_consistent"]
            or controls["tangent_negative"]["direction_consistent"]
            or controls["tangent_negative"]["checks"]["separation"]):
        raise ValueError("positive/negative tangent controls differ")
    expected = {"binding.json", "selection.json", "controls.json"}
    rows, errors, count = [], [], 0
    if len(selections) != 2 or any([p["bin"] for p in s["points"]] != list(range(40)) for s in selections):
        raise ValueError("original 2 x 40 point matrix changed")
    for selection in selections:
        parameters = RosslerParameters(**selection["parameters"])
        for point in selection["points"]:
            if len(point["history"]["states"]) != 9:
                raise ValueError("eight-return history grid changed")
            label = f"{selection['case']}--bin-{point['bin']:02d}"
            segments = []
            for i in range(8):
                base = {}
                for method in ("DOP853", "Radau"):
                    stem = f"{label}--past-{i:02d}--{method}"
                    expected.update((f"trials/{stem}.json", f"trials/{stem}-started.json"))
                    state = point["history"]["states"][i]
                    if json.loads((target/"trials"/(stem+"-started.json")).read_bytes()) != dict(label=stem, initial_state=state, method=method):
                        raise ValueError("target start differs from exact expected grid")
                    value = json.loads((target/"trials"/(stem+".json")).read_bytes())
                    prior.audit_trial(value, state, method, plan, parameters)
                    base[method] = prior.restore(value)
                    count += 1
                segments.append(base)
            endpoints = {m: prior.restore(json.loads((prior.TARGET/"trials"/(label+"--"+m+".json")).read_bytes())) for m in plan["solvers"]}
            calculated = run.old.serial(run.analyze(point, segments, endpoints, plan))
            row = dict(case=selection["case"], bin=point["bin"], global_seed_id=point["global_seed_id"],
                       initial_state=point["initial_state"], audit=calculated)
            expected.add(f"comparisons/{label}.json")
            if json.loads((target/"comparisons"/(label+".json")).read_bytes()) != row:
                raise ValueError("saved numerical decision differs from replay")
            if calculated["direction"] is not None:
                scale = np.diag(plan["section_coordinate_scales"])
                for m in plan["solvers"]:
                    matrices = [np.linalg.solve(scale, s[m]["return_jacobian"] @ scale) for s in segments]
                    errors.extend(independently_check_history(matrices, calculated["histories"][m]))
            rows.append(row)
    if (set(result["files"]) != expected or count != 1280 or result["target_integrations"] != count
            or result["rows"] != rows or result["qualified_points"] != sum(r["audit"]["qualified"] for r in rows)):
        raise ValueError("full realized grid, decisions or count differs")
    if inventory(target, omit=("summary.json",)) != result["files"] or sha256(target/"summary.json") != expected_sha:
        raise ValueError("target changed during audit")
    return dict(experiment_id="EXP-485", status="completed-audited", source_commit=SOURCE,
        plan_sha256=sha256(run.PLAN), completed_summary_sha256=expected_sha,
        target_slot_sha256=result["target_slot_sha256"], target_integrations=count,
        qualified_points=result["qualified_points"], elapsed_seconds=result["elapsed_seconds"],
        inventory_files=len(expected), inventory_bytes=sum(r["bytes"] for r in result["files"].values()),
        complete_grid_and_decision_replay=True, independent_product_maximum_angle=max(errors, default=None),
        selection_sha256=sha256(target/"selection.json"), thresholds=plan["thresholds"],
        prior_audit_sha256=plan["exp484_audit_sha256"], rows=rows,
        descriptive_cases=descriptive_metrics(rows),
        historical_symbols_verified=False, paid_review="not_run", claim_boundary=plan["claim_boundary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--expected-summary-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result = audit(args.run_dir, args.expected_summary_sha256)
    write_json(args.output_dir/"summary.json", result)
    print(json.dumps({k: result[k] for k in ("status", "target_integrations", "qualified_points", "independent_product_maximum_angle")}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only EXP-486 matrix/decision replay with separate event algebra.

Same-agent local audit, not an independent human review or reintegration.
"""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters
from butterfly.poincare import legacy_rossler_section, PoincareSection
from scripts import run_exp486_return_image_folds as run


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_trial(value, initial, tangent, section, method, count, plan, field):
    """Recompute orientation, transversality and moving-time sensitivity."""
    require(value["initial_state"] == list(initial) and value["initial_tangent"] == list(tangent)
            and value["method"] == method and value["requested_returns"] == count,
            "trial identity changed")
    require(all(value[k] == v for k, v in run.solver_options(plan).items()), "solver configuration changed")
    n = np.asarray(section.normal)
    previous = plan["initial_root_guard"]
    require(section.direction*section.value(value["guarded_state"]) > 0, "invalid guarded side")
    require(len(value["events"]) <= count, "extra oriented returns")
    all_valid, errors = True, []
    for event in value["events"]:
        t = event["time"]
        q, raw = np.asarray(event["state"]), np.asarray(event["raw_tangent"])
        require(q.shape == raw.shape == (3,) and np.isfinite([*q, *raw, t]).all(), "malformed event")
        require(previous < t <= count*plan["time_per_return"], "event chronology changed")
        previous = t
        f = np.asarray(field(t, q))
        speed = n @ f
        denominator = np.linalg.norm(n)*np.linalg.norm(f)
        angle = abs(speed)/denominator if denominator else 0.
        accepted = section.accepts(q)
        valid = bool(accepted and section.direction*speed > 0 and angle >= plan["minimum_angle"])
        require(event["valid"] == valid and event["accepted"] == accepted, "event eligibility differs")
        require(abs(event["normalized_angle"]-angle) < 1e-13 and
                abs(event["section_residual"]-section.value(q)) < 1e-13 and abs(section.value(q)) < 1e-8,
                "event section/angle differs")
        all_valid &= valid
        if valid:
            dt = -float(n @ raw)/float(speed)
            corrected = raw+dt*f
            error = float(np.max(np.abs(corrected-event["tangent"]))/max(1., np.max(np.abs(corrected))))
            require(error < 1e-12 and abs(event["time_gradient"]-dt) <= 1e-12*max(1., abs(dt)),
                    "independent event-time derivative differs")
            errors.append(error)
        else:
            require(event["tangent"] is None and event["time_gradient"] is None, "invalid tangent published")
    require(value["status"] == ("returned" if len(value["events"]) == count and all_valid else "unresolved"),
            "return status differs")
    return max(errors, default=0.)


def separate_brackets(observations):
    """Independent explicit reconstruction, never trust the candidate count."""
    edges = []
    for i, left in enumerate(observations):
        for j in (i+1, i+2):
            if j >= len(observations):
                continue
            group = observations[i:j+1]
            if not all(o["valid"] for o in group):
                continue
            signs = {np.sign(o["input_x_tangent"]) for o in group}
            if len(signs) != 1 or 0 in signs:
                continue
            if left["x_graph_slope"]*group[-1]["x_graph_slope"] >= 0:
                continue
            if j == i+1 or group[1]["x_graph_slope"] == 0:
                edges.append([i, j])
    return edges


def audit(target, expected_sha, expected_source):
    require(sha256(target/"summary.json") == expected_sha, "summary anchor changed")
    result = json.loads((target/"summary.json").read_bytes())
    require(result["status"] == "completed" and inventory(target, omit=("summary.json",)) == result["files"],
            "incomplete or changed inventory")
    plan = json.loads(run.PLAN.read_bytes())
    binding = result["binding"]
    require(binding["source_commit"] == expected_source and binding["plan_sha256"] == sha256(run.PLAN)
            and binding["source_files"] == {p: sha256(ROOT/p) for p in run.SOURCE_FILES}
            and json.loads((target/"binding.json").read_bytes()) == binding, "source binding changed")
    marker = ROOT/"artifacts/EXP-486/target-once.json"
    require(sha256(marker) == result["target_slot_sha256"] and json.loads(marker.read_bytes()) == binding,
            "consumed slot changed")
    families = run.prepare(plan)
    expected_ids = {f"{c}--region-{r}--depth-{m}--direction-{d}"
                    for c in ("local-a025-c083", "local-a027-c083")
                    for r in (0, 1) for m in (4, 8) for d in (0, 1)}
    require({f["id"] for f in families} == expected_ids and len(families) == 16
            and families == json.loads((target/"selection.json").read_bytes()), "full input matrix differs")
    expected = {"binding.json", "selection.json", "controls.json"}
    controls = json.loads((target/"controls.json").read_bytes())
    require([(c["depth"], c["kind"]) for c in controls] == [(d, k) for d in (4, 8)
            for k in ("fold", "no-fold", "projection-degenerate")], "control matrix differs")
    for control in controls:
        depth, kind = control["depth"], control["kind"]
        k = 0. if kind == "no-fold" else 1.
        base = np.array([-4., 0., 0. if kind == "projection-degenerate" else .5])
        tangent = [0. if kind == "projection-degenerate" else 1., 0., 1.]
        records = iter(enumerate(control["raw"]))
        def replay_control(u):
            i, saved = next(records)
            require(u == saved["u"], "control evaluation grid/order differs")
            relative = f"control-trials/{kind}--depth-{depth}--eval-{i:04d}.json"
            expected.add(relative)
            require(json.loads((target/relative).read_bytes()) == saved, "raw control evidence differs")
            for method in ("DOP853", "Radau"):
                value = saved["results"][method]
                initial = base+u*np.asarray(tangent)
                check_trial(value, initial, tangent, PoincareSection((0., 1., 0.), 0., -1),
                            method, depth+1, plan, run.control_field(k)[0])
                require(value["status"] == "returned", "control missing return")
                for n, event in enumerate(value["events"], 1):
                    time = n*2*np.pi
                    rho = np.exp(-.03*time)
                    q = [initial[0]-k*initial[2]**2*(1-rho**2), 0., initial[2]*rho]
                    v = [tangent[0]-2*k*initial[2]*tangent[2]*(1-rho**2), 0., tangent[2]*rho]
                    require(np.max(np.abs(np.asarray(event["state"])-q)) <= plan["controls"]["state_error"]
                            and np.max(np.abs(np.asarray(event["tangent"])-v)) <= plan["controls"]["tangent_error"]
                            and abs(event["time"]-time) <= plan["controls"]["time_error"], "analytic control differs")
            return saved["results"]
        family = dict(grid=np.linspace(-.2, .2, 17).tolist())
        analysis = run.family_analysis(family, replay_control, plan, scales=(1., 1.))
        require(next(records, None) is None and analysis == control["analysis"] and control["passed"], "control replay differs")
        if kind == "fold":
            exact = 1/(2*(1-np.exp(-2*.03*2*np.pi*(depth+1))))-.5
            require(analysis["qualified"] and len(analysis["roots"]) == 1 and
                    abs(analysis["roots"][0]["u"]-exact) <= plan["controls"]["root_u_error"], "known fold missed")
        else:
            require(not analysis["qualified"] and not analysis["candidate_intervals"], "false control fold")
    rows, errors, count = [], [], 0
    for family in families:
        parameters = RosslerParameters(**family["parameters"])
        section = replace(legacy_rossler_section(parameters), direction=-1)
        def field(_t, q):
            x, y, z = q
            return np.array([-y-z, x+parameters.a*y, parameters.b+z*(x-parameters.c)])
        pair_count = 0
        def replay(u):
            nonlocal pair_count, count
            initial = (np.asarray(family["initial_state"])+u*np.asarray(family["initial_tangent"])).tolist()
            values = {}
            for method in ("DOP853", "Radau"):
                label = f"{family['id']}--eval-{pair_count:04d}--{method}"
                names = [f"trials/{label}{suffix}.json" for suffix in ("-started", "")]
                expected.update(names)
                require(json.loads((target/names[0]).read_bytes()) == dict(label=label, family_id=family["id"],
                        u=u, method=method, initial_state=initial, initial_tangent=family["initial_tangent"]), "target grid/start differs")
                value = json.loads((target/names[1]).read_bytes())
                errors.append(check_trial(value, initial, family["initial_tangent"], section,
                                          method, family["depth"]+1, plan, field))
                values[method] = value
                count += 1
            pair_count += 1
            return values
        analysis = run.family_analysis(family, replay, plan, scales=plan["scales"])
        require(separate_brackets(analysis["grid_observations"]) == analysis["candidate_intervals"], "separate bracket reconstruction differs")
        row = dict(family_id=family["id"], case=family["case"], region=family["region"],
                   analysis=analysis, trajectory_integrations=2*pair_count)
        relative = f"families/{family['id']}.json"
        expected.add(relative)
        require(json.loads((target/relative).read_bytes()) == row, "family decision replay differs")
        rows.append(row)
    regions = []
    for case in ("local-a025-c083", "local-a027-c083"):
        for region in (0, 1):
            members = [r for r in rows if r["case"] == case and r["region"] == region]
            states = [root["observations"]["DOP853"]["image_state"] for r in members
                      for root in r["analysis"]["roots"] if root["status"] == "qualified" and root["in_region"]]
            spread = run.state_spread(states, plan["scales"]) if states else None
            regions.append(dict(case=case, region=region, family_count=len(members), root_state_spread=spread,
                qualified=len(members) == 4 and all(r["analysis"]["qualified"] for r in members)
                and spread <= plan["thresholds"]["root_scaled_state_spread"]))
    require(set(result["files"]) == expected and result["rows"] == rows and result["regions"] == regions
            and result["target_integrations"] == count and count <= 4096
            and result["qualified_families"] == sum(r["analysis"]["qualified"] for r in rows)
            and result["qualified_regions"] == sum(r["qualified"] for r in regions), "realized matrix/result differs")
    require(inventory(target, omit=("summary.json",)) == result["files"] and sha256(target/"summary.json") == expected_sha,
            "evidence changed during audit")
    return dict(experiment_id="EXP-486", status="completed-audited", source_commit=expected_source,
        completed_summary_sha256=expected_sha, target_slot_sha256=result["target_slot_sha256"],
        plan_sha256=sha256(run.PLAN), audit_script_sha256=sha256(Path(__file__)),
        complete_grid_and_decision_replay=True, independent_event_algebra_max_relative_error=max(errors),
        target_integrations=count, elapsed_seconds=result["elapsed_seconds"], families=families, rows=rows,
        regions=regions, qualified_families=result["qualified_families"], qualified_regions=result["qualified_regions"],
        thresholds=plan["thresholds"], historical_symbols_verified=False, paid_review="not_run",
        claim_boundary=plan["claim_boundary"], inventory_files=len(expected),
        inventory_bytes=sum(r["bytes"] for r in result["files"].values()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--expected-summary-sha256", required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run_dir, args.expected_summary_sha256, args.expected_source_commit)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    write_json(args.output_dir/"summary.json", result)
    print(json.dumps({k: result[k] for k in ("status", "target_integrations", "qualified_families", "qualified_regions")}))


if __name__ == "__main__":
    main()

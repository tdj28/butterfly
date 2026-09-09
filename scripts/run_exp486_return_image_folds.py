#!/usr/bin/env python3
"""Bounded one-shot continuous finite-image-curve fold pilot; local CPU."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import scipy
from scipy.optimize import brentq
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.models import RosslerParameters, rossler_rhs, rossler_jacobian
from butterfly.poincare import PoincareSection, legacy_rossler_section
from butterfly.return_image_curve import image_returns, observe_curve, candidate_intervals

PLAN = ROOT/"experiments/manifests/EXP-486-return-image-fold-pilot.json"
SOURCE_FILES = ("scripts/run_exp486_return_image_folds.py", "python/butterfly/return_image_curve.py",
                "python/butterfly/return_geometry.py", "python/butterfly/models.py", "python/butterfly/poincare.py")


class CurveUnavailable(ValueError):
    pass


def prepare(plan):
    old = ROOT/plan["exp485_run"]
    if sha256(old/"summary.json") != plan["exp485_summary_sha256"] or sha256(ROOT/"docs/experiments/receipts/EXP-485-transported-tangent-result.json") != plan["exp485_audit_sha256"]:
        raise ValueError("EXP-485 input anchors changed")
    result = json.loads((old/"summary.json").read_bytes())
    if result["status"] != "completed" or inventory(old, omit=("summary.json",)) != result["files"]:
        raise ValueError("EXP-485 source inventory changed")
    selections = json.loads((old/"selection.json").read_bytes())
    families = []
    for case in plan["cases"]:
        selection = next(s for s in selections if s["case"] == case)
        parameters = RosslerParameters(**selection["parameters"])
        section = replace(legacy_rossler_section(parameters), direction=-1)
        if abs(section.gate_upper+parameters.a*section.offset) > 1e-12:
            raise ValueError("negative orientation does not imply the historical gate")
        for region, (left_bin, right_bin) in enumerate(plan["regions"]):
            left, anchor = [next(p for p in selection["points"] if p["bin"] == b) for b in (left_bin, right_bin)]
            x_interval = [left["initial_state"][0], anchor["initial_state"][0]]
            if x_interval[0] >= x_interval[1]:
                raise ValueError("prior observed interval is not ordered")
            for depth in plan["depths"]:
                product = np.eye(2)
                for i in range(8-depth, 8):
                    trial = json.loads((old/"trials"/f"{case}--bin-{right_bin:02d}--past-{i:02d}--DOP853.json").read_bytes())
                    product = np.asarray(trial["return_jacobian"]) @ product
                for direction_id, direction in enumerate(plan["normalized_directions"]):
                    physical = np.asarray(direction)*plan["scales"]
                    gain_x = float((product @ physical)[0])
                    if not np.isfinite(gain_x) or gain_x == 0:
                        raise ValueError("prior linear radius construction is degenerate")
                    radius = float(np.clip(plan["radius"]["gap_factor"]*np.ptp(x_interval)/abs(gain_x),
                                           plan["radius"]["minimum"], plan["radius"]["maximum"]))
                    initial = np.asarray(anchor["history"]["states"][-depth-1])
                    tangent = np.array([physical[0], 0., physical[1]])
                    grid = np.linspace(-radius, radius, plan["grid_points"])
                    for u in [*grid, *plan["finite_difference_steps"], *(-np.asarray(plan["finite_difference_steps"]))]:
                        state = initial+u*tangent
                        field = rossler_rhs(0., state, parameters)
                        angle = abs(field[1])/np.linalg.norm(field)
                        if not section.accepts(state) or field[1] >= 0 or angle < plan["minimum_angle"]:
                            raise ValueError("fixed curve grid has an invalid initial state; no replacement")
                    families.append(dict(id=f"{case}--region-{region}--depth-{depth}--direction-{direction_id}",
                        case=case, region=region, depth=depth, direction_id=direction_id,
                        parameters=selection["parameters"], anchor_bin=right_bin,
                        global_seed_id=anchor["global_seed_id"], old_x_interval=x_interval,
                        initial_state=initial.tolist(), initial_tangent=tangent.tolist(), radius=radius,
                        radius_source_gain_x=gain_x, grid=grid.tolist(),
                        expected_states=[anchor["initial_state"], anchor["saved_next_state"]],
                        expected_times=[anchor["saved_pair_times"][0]-anchor["history"]["times"][-depth-1],
                                        anchor["saved_pair_times"][1]-anchor["history"]["times"][-depth-1]]))
    if len(families) != 16 or len({f["id"] for f in families}) != 16:
        raise ValueError("fixed family matrix changed")
    return families


def pair_metrics(results, plan, scales):
    thresholds = plan["thresholds"]
    observations = {m: observe_curve(r, scales=scales,
        **{k: thresholds[k] for k in ("minimum_gain", "minimum_x_component")}) for m, r in results.items()}
    if any(r["status"] != "returned" for r in results.values()):
        return dict(passed=False, observations=observations, reason="missing or invalid return")
    a, b = (results[m] for m in plan["solvers"])
    errors = []
    for ra, rb in zip(a["events"][-2:], b["events"][-2:], strict=True):
        qa, qb = [np.asarray(r["state"])[[0, 2]]/scales for r in (ra, rb)]
        va, vb = [np.asarray(r["tangent"])[[0, 2]]/scales for r in (ra, rb)]
        errors.append(dict(state=float(np.max(np.abs(qa-qb))), time=abs(ra["time"]-rb["time"]),
                           tangent=float(np.max(np.abs(va-vb))/max(1., np.max(np.abs(vb))))))
    return dict(passed=all(e["state"] <= thresholds["solver_scaled_state"] and e["time"] <= thresholds["solver_time"] and e["tangent"] <= thresholds["solver_relative_scaled_tangent"] for e in errors),
                errors=errors, observations=observations)


def family_analysis(family, evaluate, plan, *, scales):
    """Same grid/control/refinement path for synthetic and target families."""
    scales = np.asarray(scales)
    cache = {}
    def point(u):
        u = float(u)
        if u.hex() not in cache:
            results = evaluate(u)
            cache[u.hex()] = dict(u=u, results=results, pair=pair_metrics(results, plan, scales))
        return cache[u.hex()]
    grid = [point(u) for u in family["grid"]]
    center = point(0.)
    fd = []
    for step in plan["finite_difference_steps"]:
        minus, plus = point(-step), point(step)
        for method in plan["solvers"]:
            records = [p["results"][method] for p in (minus, center, plus)]
            if any(r["status"] != "returned" for r in records):
                fd.append(dict(step=step, method=method, passed=False, reason="missing finite-difference return"))
                continue
            error = 0.
            for index in (-2, -1):
                measured = (np.asarray(records[2]["events"][index]["state"])[[0, 2]]-
                            np.asarray(records[0]["events"][index]["state"])[[0, 2]])/(2*step*scales)
                expected = np.asarray(records[1]["events"][index]["tangent"])[[0, 2]]/scales
                error = max(error, float(np.max(np.abs(measured-expected))/max(1., np.max(np.abs(expected)))))
            fd.append(dict(step=step, method=method, relative_scaled_error=error,
                           passed=error <= plan["thresholds"]["finite_difference_relative_scaled_tangent"]))
    anchor_checks = []
    if "expected_states" in family:
        for method in plan["solvers"]:
            result = center["results"][method]
            if result["status"] != "returned":
                anchor_checks.append(dict(method=method, passed=False))
                continue
            for i, row in enumerate(result["events"][-2:]):
                state_error = float(np.max(np.abs((np.asarray(row["state"])-family["expected_states"][i])[[0, 2]]/scales)))
                time_error = abs(row["time"]-family["expected_times"][i])
                anchor_checks.append(dict(method=method, return_index=i, state_error=state_error, time_error=time_error,
                    passed=state_error <= plan["thresholds"]["saved_scaled_state"] and time_error <= plan["thresholds"]["saved_time"]))
    observations = []
    for p in grid:
        o = dict(p["pair"]["observations"]["DOP853"])
        o["valid"] = o["valid"] and p["pair"]["passed"] and p["pair"]["observations"]["Radau"]["valid"]
        observations.append(o)
    brackets = candidate_intervals(observations)
    roots = []
    eligible_count = len(brackets) <= plan["root_search"]["maximum_brackets"]
    if eligible_count:
        for indices in brackets:
            interval = [family["grid"][i] for i in indices]
            input_sign = np.sign(observations[indices[0]]["input_x_tangent"])
            before = len(cache)
            def residual(u):
                if float(u).hex() not in cache and len(cache)-before >= plan["root_search"]["maximum_new_pairs_per_bracket"]:
                    raise CurveUnavailable("bracket evaluation limit reached")
                p = point(u)
                obs = p["pair"]["observations"]
                if not p["pair"]["passed"] or any(not v["valid"] or np.sign(v["input_x_tangent"]) != input_sign for v in obs.values()):
                    raise CurveUnavailable("invalid interior curve/solver/projection geometry")
                return obs["DOP853"]["normalized_output_derivative"]
            try:
                root, info = brentq(residual, *interval, xtol=plan["root_search"]["xtol"],
                    rtol=plan["root_search"]["rtol"], maxiter=plan["root_search"]["maximum_iterations"], full_output=True, disp=False)
                p = point(root)
                observed = p["pair"]["observations"]
                passed = bool(info.converged and p["pair"]["passed"] and all(o["valid"] and np.sign(o["input_x_tangent"]) == input_sign and abs(o["normalized_output_derivative"]) <= plan["thresholds"]["root_normalized_residual"] for o in observed.values()))
                x = observed["DOP853"]["image_state"][0]
                in_region = "old_x_interval" not in family or family["old_x_interval"][0] <= x <= family["old_x_interval"][1]
                roots.append(dict(status="qualified" if passed else "unresolved", u=root, original_u_bracket=interval,
                    observations=observed, in_region=bool(in_region), converged=bool(info.converged), new_paired_evaluations=len(cache)-before))
            except CurveUnavailable as error:
                roots.append(dict(status="unresolved", original_u_bracket=interval, reason=str(error), new_paired_evaluations=len(cache)-before))
    states = [r["observations"]["DOP853"]["image_state"] for r in roots if r["status"] == "qualified" and r["in_region"]]
    spread = state_spread(states, scales) if states else None
    numerical = all(p["pair"]["passed"] for p in cache.values()) and all(r["passed"] for r in fd+anchor_checks)
    qualified = numerical and eligible_count and bool(states) and all(r["status"] == "qualified" for r in roots) and spread <= plan["thresholds"]["root_scaled_state_spread"]
    return dict(qualified=bool(qualified), numerical_checks_passed=bool(numerical),
        finite_difference=fd, anchor_checks=anchor_checks, grid_observations=observations,
        candidate_intervals=brackets, excessive_brackets=not eligible_count, roots=roots,
        in_region_root_state_spread=spread, evaluated_u=[p["u"] for p in cache.values()])


def state_spread(states, scales):
    values = np.asarray(states)[:, [0, 2]]/np.asarray(scales)
    return float(np.max(np.ptp(values, axis=0)))


def control_field(k=1., decay=.03):
    def rhs(t, q):
        x, y, z = q
        return np.array([-y-2*k*decay*z*z, x-k*z*z, -decay*z])
    def jac(t, q):
        z = q[2]
        return np.array([[0., -1., -4*k*decay*z], [1., 0., -2*k*z], [0., 0., -decay]])
    return rhs, jac


def solver_options(plan):
    return {k: plan[k] for k in ("rtol", "atol", "max_step", "time_per_return", "initial_root_guard", "minimum_angle")}


def controls(plan, *, evidence_dir=None):
    rows = []
    section = PoincareSection((0., 1., 0.), 0., -1)
    for depth in plan["controls"]["depths"]:
        for kind, k, base, tangent in (("fold", 1., [-4., 0., .5], [1., 0., 1.]),
                                      ("no-fold", 0., [-4., 0., .5], [1., 0., 1.]),
                                      ("projection-degenerate", 1., [-4., 0., 0.], [0., 0., 1.])):
            family = dict(depth=depth, grid=np.linspace(-plan["controls"]["radius"], plan["controls"]["radius"], plan["controls"]["grid_points"]).tolist())
            raw = []
            def evaluate(u):
                initial = np.asarray(base)+u*np.asarray(tangent)
                results = {m: image_returns(*control_field(k), initial, tangent, section,
                    count=depth+1, method=m, **solver_options(plan)) for m in plan["solvers"]}
                raw.append(dict(u=u, results=results))
                if evidence_dir is not None:
                    write_json(evidence_dir/f"{kind}--depth-{depth}--eval-{len(raw)-1:04d}.json", raw[-1])
                for result in results.values():
                    if result["status"] != "returned":
                        raise ValueError("analytic control lost a return")
                    for n, event in enumerate(result["events"], 1):
                        rho = np.exp(-.03*2*np.pi*n)
                        expected = np.array([initial[0]-k*initial[2]**2*(1-rho*rho), 0., initial[2]*rho])
                        derivative = np.array([tangent[0]-2*k*initial[2]*tangent[2]*(1-rho*rho), 0., tangent[2]*rho])
                        if np.max(np.abs(np.asarray(event["state"])-expected)) > plan["controls"]["state_error"] or np.max(np.abs(np.asarray(event["tangent"])-derivative)) > plan["controls"]["tangent_error"] or abs(event["time"]-n*2*np.pi) > plan["controls"]["time_error"]:
                            raise ValueError("analytic state/tangent/count control failed")
                return results
            analysis = family_analysis(family, evaluate, plan, scales=(1., 1.))
            expected_u = 1/(2*(1-np.exp(-2*.03*2*np.pi*(depth+1))))-.5 if kind == "fold" else None
            passed = analysis["numerical_checks_passed"] and (
                analysis["qualified"] and len(analysis["roots"]) == 1 and abs(analysis["roots"][0]["u"]-expected_u) <= plan["controls"]["root_u_error"] if kind == "fold" else not analysis["qualified"] and not analysis["candidate_intervals"])
            rows.append(dict(kind=kind, depth=depth, passed=bool(passed), expected_root_u=expected_u, analysis=analysis, raw=raw))
            if not passed:
                raise ValueError(f"analytic {kind} depth-{depth} pipeline control failed")
    return rows


def execute(plan, families, output):
    rows, count = [], 0
    for family in families:
        parameters = RosslerParameters(**family["parameters"])
        section = replace(legacy_rossler_section(parameters), direction=-1)
        rhs = lambda t, q: rossler_rhs(t, q, parameters)
        jac = lambda t, q: rossler_jacobian(q, parameters)
        pair_count = 0
        def evaluate(u):
            nonlocal count, pair_count
            initial = np.asarray(family["initial_state"])+u*np.asarray(family["initial_tangent"])
            results = {}
            for method in plan["solvers"]:
                if count >= plan["limits"]["maximum_target_integrations"] or sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) >= plan["limits"]["maximum_output_bytes"]-plan["limits"]["summary_reserve_bytes"]:
                    raise TimeoutError("EXP-486 integration/output resource cap reached")
                label = f"{family['id']}--eval-{pair_count:04d}--{method}"
                write_json(output/"trials"/(label+"-started.json"), dict(label=label, family_id=family["id"], u=u, method=method, initial_state=initial.tolist(), initial_tangent=family["initial_tangent"]))
                count += 1
                result = image_returns(rhs, jac, initial, family["initial_tangent"], section,
                    count=family["depth"]+1, method=method, **solver_options(plan))
                write_json(output/"trials"/(label+".json"), result)
                results[method] = result
            pair_count += 1
            return results
        analysis = family_analysis(family, evaluate, plan, scales=plan["scales"])
        row = dict(family_id=family["id"], case=family["case"], region=family["region"],
                   analysis=analysis, trajectory_integrations=2*pair_count)
        write_json(output/"families"/(family["id"]+".json"), row)
        rows.append(row)
        print(f"{family['id']}: completed ({count} total integrations)", flush=True)
    regions = []
    for case in plan["cases"]:
        for region in range(2):
            members = [r for r in rows if r["case"] == case and r["region"] == region]
            states = [root["observations"]["DOP853"]["image_state"] for r in members for root in r["analysis"]["roots"] if root["status"] == "qualified" and root["in_region"]]
            spread = state_spread(states, plan["scales"]) if states else None
            regions.append(dict(case=case, region=region, family_count=len(members), root_state_spread=spread,
                qualified=len(members) == 4 and all(r["analysis"]["qualified"] for r in members) and spread <= plan["thresholds"]["root_scaled_state_spread"]))
    return dict(experiment_id="EXP-486", status="completed", rows=rows, regions=regions,
        target_integrations=count, qualified_families=sum(r["analysis"]["qualified"] for r in rows),
        qualified_regions=sum(r["qualified"] for r in regions), historical_symbols_verified=False,
        claim_boundary=plan["claim_boundary"], paid_review="not_run")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if ROOT/"artifacts/EXP-486" not in output.parents:
        parser.error("fresh output must be beneath artifacts/EXP-486")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        parser.error("clean committed source required")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if commit != subprocess.check_output(["git", "rev-parse", "@{upstream}"], cwd=ROOT, text=True).strip():
        parser.error("push this exact freeze first")
    plan = json.loads(PLAN.read_bytes())
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    binding = dict(source_commit=commit, plan_sha256=sha256(PLAN),
        source_files={p: sha256(ROOT/p) for p in SOURCE_FILES},
        runtime=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__),
        started_at_utc=datetime.now(timezone.utc).isoformat(), execution_mode="local-audited-no-paid-review")
    write_json(output/"binding.json", binding)
    start = time.monotonic()
    def timeout(*_):
        raise TimeoutError("EXP-486 wall bound reached")
    previous = signal.signal(signal.SIGALRM, timeout)
    signal.alarm(plan["limits"]["wall_seconds"])
    try:
        families = prepare(plan)
        write_json(output/"selection.json", families)
        (output/"control-trials").mkdir()
        write_json(output/"controls.json", controls(plan, evidence_dir=output/"control-trials"))
        if not args.execute:
            print("All 16 family inputs and six analytic pipeline controls passed; zero Rössler targets")
            return
        marker = ROOT/"artifacts/EXP-486/target-once.json"
        with marker.open("x") as handle:
            json.dump(binding, handle, sort_keys=True, allow_nan=False)
        (output/"trials").mkdir()
        (output/"families").mkdir()
        result = execute(plan, families, output)
        result.update(binding=binding, target_slot_sha256=sha256(marker), elapsed_seconds=time.monotonic()-start, files=inventory(output))
        if sum(r["bytes"] for r in result["files"].values())+len((json.dumps(result, sort_keys=True, indent=2)+"\n").encode()) > plan["limits"]["maximum_output_bytes"]-131072:
            raise TimeoutError("terminal summary exceeds output reserve")
        write_json(output/"summary.json", result)
        print(json.dumps({k: result[k] for k in ("status", "target_integrations", "qualified_families", "qualified_regions", "elapsed_seconds")}))
    except (Exception, KeyboardInterrupt) as error:
        write_json(output/"failure.json", dict(binding=binding, status="failed", error_type=type(error).__name__, message=str(error), elapsed_seconds=time.monotonic()-start))
        raise
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    main()

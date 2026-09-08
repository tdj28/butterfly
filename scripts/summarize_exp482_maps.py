#!/usr/bin/env python3
"""Audit completed EXP-482 and reproduce its analysis from all raw journals.

No integration, parameter changes, retry, upload or paid service. Figures are
descriptive views of the frozen primary projection, never replacement fits.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.paired_campaign import analyze_campaign, planned_seeds
from butterfly.paired_input_package import load_package
from butterfly.paired_inputs import load_references
from butterfly.paired_phases import from_reference_audit, _expectation
from butterfly.paired_replay import assemble_profile, replay_batch
from butterfly.paired_sampling import SECTIONS
from scripts.dispatch_paired_phases import completed_worker
from scripts.summarize_exp482_qualification import SOURCE, RUN, ANCHORS as QUALIFICATION_ANCHORS

CAMPAIGN_SHA = "c4ab5fb1fdd07273e5e5f4b2c7548b1d073e3645e1cc63f24738a2bf2418c27e"
ANALYSIS_SHA = "d43f996f0a9e24d959689fba975cb3f851505a5192a26e4dca006dcf2af2a27d"
METRICS = ("bins", "smoothing", "resolved", "reason", "coverage", "heldout_q90_error",
    "heldout_affine_q90_error", "heldout_unsupported_fraction", "normalized_domain",
    "bootstrap_consensus", "critical_intervals")


def support_counts(pairs, seed_ids, bounds, bins):
    """Distinct calibration seeds per input bin, independently of spline code."""
    pairs, seed_ids = np.asarray(pairs), np.asarray(seed_ids)
    lower, upper = bounds
    if pairs.ndim != 3 or pairs.shape[0] != len(seed_ids) or pairs.shape[-1] != 2 or upper <= lower:
        raise ValueError("invalid support display inputs")
    x = (pairs[..., 0]-lower)/(upper-lower)
    assigned = np.clip(np.floor(x*bins).astype(int), 0, bins-1)
    return np.array([len(np.unique(seed_ids[np.any(assigned == b, axis=1)])) for b in range(bins)])


def compact_result(analysis):
    """Keep every case/projection/window/variant; null means not evaluated."""
    output = {}
    for name, case in analysis["cases"].items():
        a, cohort = case["analysis"], case["cohort"]
        rows = []
        for projection in a["projections"]:
            for key, audit in projection["audits"].items():
                for variant in audit["variants"]:
                    rows.append(dict(role=projection["role"], projection=projection["projection"], key=key,
                        calibration_bounds=audit.get("calibration_bounds"),
                        **{k: variant.get(k) for k in METRICS}))
        output[name] = dict(cohort={k:v for k,v in cohort.items() if not isinstance(v,list)},
            retained_seeds=int(sum(cohort["retained"])), joint_primary=a["joint_primary"],
            critical_matrix=a["critical_matrix"], variants=rows,
            primary_failure_counts=dict(Counter(row["reason"] for row in rows if row["role"] == "primary")))
    return output


def audit():
    campaign = RUN/"campaign"
    if sha256(campaign/"receipt.json") != CAMPAIGN_SHA:
        raise ValueError("completed campaign anchor changed")
    receipt = json.loads((campaign/"receipt.json").read_bytes())
    if (receipt["status"] != "completed" or receipt["kind"] != "target"
            or receipt["target_slot_consumed"] is not True
            or inventory(campaign, omit=("receipt.json",)) != receipt["files"]):
        raise ValueError("campaign inventory or completed status differs")
    if sha256(ROOT/"artifacts/EXP-482/target-once.json") != receipt["campaign_slot_sha256"]:
        raise ValueError("consumed one-shot marker changed")
    if sha256(RUN/"preflight/receipt.json") != QUALIFICATION_ANCHORS["preflight/receipt.json"]:
        raise ValueError("completed setup anchor changed")
    pre = json.loads((RUN/"preflight/receipt.json").read_bytes())
    plan = load_package(RUN/"preflight/inputs", pre["inputs"]["sha256"])
    if pre["source_commit"] != SOURCE or pre["mode"] != "local-audited" or plan["experiment_id"] != "EXP-482":
        raise ValueError("wrong experiment/source/release mode")
    design, _ = from_reference_audit(plan, load_references(plan, RUN/"preflight/inputs"),
        source_commit=SOURCE, plan_sha256=pre["plan_sha256"])
    for stage, row in receipt["phases"].items():
        completed_worker(campaign/stage, row["receipts"], design, stage,
            row["grant_sha256"], pre["runtime"]["sha256"], target=True)
    analysis_path = campaign/"analysis/phase/analysis.json"
    if sha256(analysis_path) != ANALYSIS_SHA:
        raise ValueError("completed analysis anchor changed")
    analysis = json.loads(analysis_path.read_bytes())
    profiles, grid = {}, design.validate()
    for case in plan["candidate_ids"]:
        profiles[case] = {}
        for setting in plan["collection"]["profiles"]:
            name, batches = setting["name"], {}
            selected = [t for t in grid if t.stage == "collection" and t.candidate_id == case and t.profile == name]
            for trial in selected:
                source = campaign/"collection/phase"
                row = json.loads((source/"receipts"/(trial.trial_id+".json")).read_bytes())
                if row["trial_id"] != trial.trial_id or row["binding"] != design.binding(trial) or row["status"] != "completed":
                    raise ValueError("collection trial differs from fixed design")
                batches[trial.trial_id] = replay_batch(source/"trials"/trial.trial_id,
                    _expectation(design,trial,row), plan["sample"]["observation_windows"],
                    strata_per_window=plan["sample"]["strata_per_window"])
            joined = assemble_profile(batches, [t.trial_id for t in selected],
                planned_seeds(plan)["global_seed_ids"], design.initial[case])
            profiles[case][name] = joined
            print(f"raw replay complete: {case} {name}", flush=True)
    references = {case:design.sections[case][SECTIONS[0]].cycle_states for case in plan["candidate_ids"]}
    reproduced = analyze_campaign(profiles,design.initial,references,plan,source_commit=SOURCE,plan_sha256=pre["plan_sha256"])
    if reproduced != analysis:
        raise ValueError("full raw-data analysis replay differs from saved result")
    if inventory(campaign, omit=("receipt.json",)) != receipt["files"] or sha256(campaign/"receipt.json") != CAMPAIGN_SHA:
        raise ValueError("campaign changed during replay")
    summary = dict(experiment_id="EXP-482",status="completed-primary-unresolved", source_commit=SOURCE,
        campaign_sha256=CAMPAIGN_SHA, analysis_sha256=ANALYSIS_SHA,
        campaign_files=len(receipt["files"]), campaign_bytes=sum(r["bytes"] for r in receipt["files"].values()),
        complete_inventory_verified=True, all_raw_collection_and_analysis_replay_exact=True,
        reporting_thresholds=analysis["reporting_thresholds"], cases=compact_result(analysis),
        all_cases_primary_resolved=analysis["all_cases_primary_resolved"], historical_symbols_verified=False,
        paid_review="not_run", phases={s:json.loads((campaign/s/"supervisor/terminal.json").read_bytes())
                                      for s in receipt["phases"]},
        scope="Insufficient supported domain for the frozen test, not a symbolic or homoclinic refutation; no retry")
    return summary, profiles, analysis


def plot_support(output, profiles, analysis):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2,4,figsize=(16,8),layout="constrained",sharex=True,sharey=True)
    cases = list(analysis["cases"])
    names = ["rk4-00025","rk4-000125"]
    labels = {"rk4-00025":"RK4 .0025", "rk4-000125":"RK4 .00125"}
    support = []
    for row, case in enumerate(cases):
        cohort = analysis["cases"][case]["cohort"]
        for n,name in enumerate(names):
            data = profiles[case][name]["pair_states"][SECTIONS[0]][...,0]
            for window in range(2):
                ax = axes[row,2*n+window]
                audit = analysis["cases"][case]["analysis"]["primary_audits"][f"{name}/window-{window}"]
                cal = data[np.asarray(cohort["calibration"],bool),window]
                val = data[np.asarray(cohort["validation"],bool),window]
                ids = np.asarray(cohort["global_seed_ids"])[np.asarray(cohort["calibration"],bool)]
                bounds = audit["calibration_bounds"]
                lower = float(cal.min())
                if [lower,lower+float(np.ptp(cal))] != bounds:
                    raise ValueError("display calibration differs from original normalization")
                counts = support_counts(cal,ids,bounds,40)
                minimum = audit["options"]["minimum_bin_seeds"]
                coverage = float(np.mean(counts >= minimum))
                if coverage != audit["variants"][0]["coverage"]:
                    raise ValueError("display support differs from original 40-bin result")
                edges = np.linspace(*bounds,41)
                for i in np.flatnonzero(counts < minimum):
                    ax.axvspan(edges[i],edges[i+1],color="#f1bc99",alpha=.4,lw=0,zorder=0)
                ax.scatter(cal[...,0],cal[...,1],s=1,color="#606c80",alpha=.18,rasterized=True,label="Calibration")
                ax.scatter(val[...,0],val[...,1],s=1,color="#087f8c",alpha=.18,rasterized=True,label="Held out")
                ax.set_title(f"{labels[name]} | t={80 if window==0 else 180}–{140 if window==0 else 240}\n40-bin coverage {coverage:.1%}",fontsize=10)
                ax.set_xlim(-12,.2); ax.set_ylim(-12,.2)
                ax.set_xlabel("x at accepted crossing n")
                if n==0 and window==0:
                    ax.set_ylabel(f"{case}\nx at crossing n+1")
                support.append(dict(case=case,profile=name,window=window,calibration_bounds=bounds,
                    distinct_calibration_seeds_per_bin=counts.tolist(),coverage=coverage))
    fig.suptitle("EXP-482: return-map observations with incomplete calibration support",fontsize=16)
    fig.supxlabel("All retained seed blocks shown. Orange bands: fewer than 8 distinct calibration seeds in a 40-bin cell. No fitted curves or verified turns.",fontsize=10)
    fig.savefig(output/"primary-support.png",dpi=180)
    plt.close(fig)
    return support


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    output=args.output_dir.absolute()
    output.mkdir(parents=True,exist_ok=False,mode=0o700)
    try:
        summary,profiles,analysis=audit()
        summary["display_support"] = plot_support(output,profiles,analysis)
        write_json(output/"summary.json",summary)
        print(json.dumps(dict(status=summary["status"],raw_replay_exact=True,summary_sha256=sha256(output/"summary.json"))))
    except (Exception,KeyboardInterrupt) as error:
        write_json(output/"failure.json",dict(status="audit-failed",error_type=type(error).__name__,message=str(error)))
        raise


if __name__=="__main__":
    main()

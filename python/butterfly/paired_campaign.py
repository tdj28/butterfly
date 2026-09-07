"""Fixed trial enumeration and both-case analysis composition for EXP-481.

No integration, input loading or execution authorization. The production caller
must authenticate the plan, reference rows and source, and supply profiles from
complete externally bound journal replay. Matching strings are not authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np

from .paired_decisions import analyze_case, critical_matrix
from .paired_replay import intersect_profiles
from .paired_sampling import SECTIONS, seed_commitment, seed_table
from .seed_return_map import MapOptions, _validate_options


@dataclass(frozen=True)
class Trial:
    stage: str
    candidate_id: str
    profile: str
    trial_id: str
    global_seed_ids: tuple[int, ...]


def _names(values, count):
    names = list(values)
    if (len(names) != count or len(set(names)) != count
            or any(not isinstance(n, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,79}", n) is None
                   for n in names)):
        raise ValueError("exact distinct path-safe case/profile names required")
    return names


def planned_seeds(plan):
    """Reconstruct inputs only; reject a changed seed rectangle or split."""
    seed = plan["seeds"]
    table = seed_table(seed["count_per_case"], random_seed=seed["random_seed"])
    count = len(table["global_seed_ids"])
    if (seed["generator"] != "PCG64" or seed["xz_ranges"] != [[-14., -.2], [.008, .55]]
            or seed["y_rule"] != "candidate historical-section offset"
            or seed["same_xz_across_cases_and_profiles"] is not True
            or seed["global_seed_ids"] != [0, count-1] or seed["holdout_ids"] != [count//2, count-1]
            or seed_commitment(table) != seed["ordered_table_sha256"]):
        raise ValueError("seed declaration differs from deterministic table/split")
    return table


def trial_grid(plan):
    """Enumerate every trial before outcomes; never select surviving IDs.

    Qualification has all four profiles for each nominated original seed;
    collection has every contiguous batch for both cases and both RK4 profiles.
    This enumerator does not validate every numerical option or permit launch.
    """
    table = planned_seeds(plan)
    cases = _names(plan["candidate_ids"], 2)
    profiles = _names([p["name"] for p in plan["collection"]["profiles"]], 2)
    adaptive = _names([p["method"] for p in plan["adaptive_qualification"]["profiles"]], 2)
    if set(adaptive) != {"DOP853", "Radau"} or set(adaptive) & set(profiles):
        raise ValueError("distinct RK4, DOP853 and Radau profiles required")
    size, count = plan["collection"]["batch_size"], len(table["global_seed_ids"])
    if type(size) is not int or size < 1 or count % size:
        raise ValueError("positive batch size must exactly divide fixed seed count")
    qualification = plan["adaptive_qualification"]["global_seed_ids"]
    if (not qualification or any(type(i) is not int or not 0 <= i < count for i in qualification)
            or len(set(qualification)) != len(qualification)):
        raise ValueError("distinct declared qualification IDs from original table required")
    result = []
    for case in cases:
        for profile in [*profiles, *adaptive]:
            for seed_id in qualification:
                result.append(Trial("qualification", case, profile,
                    f"{case}--qualification--{profile}--seed-{seed_id:06d}", (seed_id,)))
    for case in cases:
        for profile in profiles:
            for start in range(0, count, size):
                result.append(Trial("collection", case, profile,
                    f"{case}--collection--{profile}--batch-{start//size:06d}", tuple(range(start, start+size))))
    return tuple(result)


def validate_analysis_plan(plan):
    """Validate the analysis design without opening or fitting observations."""
    windows = np.asarray(plan["sample"]["observation_windows"], float)
    strata = plan["sample"]["strata_per_window"]
    if (windows.shape != (2, 2) or not np.isfinite(windows).all()
            or np.any(windows[:, 0] >= windows[:, 1]) or windows[0, 0] < 0
            or windows[1, 0] < windows[0, 1] or windows[-1, 1] > plan["collection"]["horizon"]
            or type(strata) is not int or strata < 1):
        raise ValueError("two valid physical windows and positive pair strata required")
    analysis = plan["analysis"]
    options = MapOptions(**analysis["options"])
    _validate_options(options)
    if (analysis["primary"]["section"] != SECTIONS[0] or analysis["primary"]["axis"] != 0
            or analysis["fit_each_window_separately"] is not True
            or options.minimum_seeds != plan["sample"]["minimum_seeds_per_split"]
            or plan["critical_membership"]["enabled_only_after_joint_primary_gate"] is not True
            or plan["critical_membership"]["require_every_primary_window_profile_variant"] is not True
            or analysis["historical_z_or_barrio_z_can_rescue_primary"] is not False
            or [(p["section"], p["axis"]) for p in analysis["diagnostics"]] != [(SECTIONS[0], 2), (SECTIONS[1], 2)]):
        raise ValueError("historical x primary and fixed non-rescuing diagnostics required")
    variants = analysis["variants"]
    if (not variants or any(len(v) != 2 or type(v[0]) is not int or v[0] < 6
                           or not np.isfinite(v[1]) or v[1] <= 0 for v in variants)
            or len(set(tuple(v) for v in variants)) != len(variants)):
        raise ValueError("distinct valid frozen spline variants required")
    proximity = plan["critical_membership"]
    disagreement = plan["sample"]["maximum_profile_retention_disagreement_fraction"]
    if (not np.isfinite(disagreement) or not 0 <= disagreement <= 1
            or any(not np.isfinite(proximity[k]) or proximity[k] < 0 for k in
                   ("normalized_interval_padding", "maximum_absolute_normalized_spline_slope"))):
        raise ValueError("finite valid cohort/proximity thresholds required")
    return windows, strata, options


def analyze_campaign(profiles_by_case, initial_states_by_case, reference_states_by_case, plan,
                     *, source_commit, plan_sha256):
    """Analyze both complete cases; unresolved science is not missing evidence.

    No best-case selection, reindexing, refilling or chosen reference phase.
    Return all original-ID cohort masks and all six reference rows. Technical
    invalidity raises; a fully analyzed unresolved case is explicitly retained.
    This is an in-memory composition, not an authentication or journal auditor.
    """
    if (not isinstance(source_commit, str) or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None
            or not isinstance(plan_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", plan_sha256) is None):
        raise ValueError("full source commit and plan digest required")
    trials = trial_grid(plan)
    table = planned_seeds(plan)
    cases = plan["candidate_ids"]
    names = [p["name"] for p in plan["collection"]["profiles"]]
    for mapping in (profiles_by_case, initial_states_by_case, reference_states_by_case):
        if set(mapping) != set(cases):
            raise ValueError("exact both-case inputs required")
    ids = table["global_seed_ids"]
    windows, strata, options = validate_analysis_plan(plan)
    analysis = plan["analysis"]
    # Validate the entire case grid before fitting either case. Missing second-
    # case data must not leave a first-case-only scientific aggregate.
    cohorts = {}
    for case in cases:
        initial, reference = np.asarray(initial_states_by_case[case]), np.asarray(reference_states_by_case[case])
        if (initial.shape != (len(ids), 3) or not np.isfinite(initial).all()
                or not np.array_equal(initial[:, [0, 2]], table["xz"])
                or not np.all(initial[:, 1] == initial[0, 1])):
            raise ValueError("case initial states differ from fixed seed inputs/section plane")
        if reference.shape != (6, 3) or not np.isfinite(reference).all():
            raise ValueError("all six finite ordered historical reference states required")
        profiles = profiles_by_case[case]
        if set(profiles) != set(names):
            raise ValueError("exact two collection profiles required for every case")
        for name in names:
            profile = profiles[name]
            expected = [t for t in trials if t.stage == "collection" and t.candidate_id == case and t.profile == name]
            if (profile["binding"] != dict(candidate_id=case, profile=name, source_commit=source_commit, plan_sha256=plan_sha256)
                    or profile["batch_ids"] != [t.trial_id for t in expected]
                    or not np.array_equal(profile["global_seed_ids"], ids)
                    or not np.array_equal(profile["initial_states"], initial)
                    or not np.array_equal(profile["windows"], windows)
                    or profile["horizon"] != plan["collection"]["horizon"]
                    or len(profile["sources"]) != len(expected)
                    or not np.array_equal(profile["seed_batch_index"], np.repeat(np.arange(len(expected)), plan["collection"]["batch_size"]))):
                raise ValueError("profile differs from full ordered source/plan/case/batch grid")
            for section in SECTIONS:
                if (profile["pair_states"][section].shape != (len(ids), 2, strata, 2, 3)
                        or profile["pair_times"][section].shape != (len(ids), 2, strata, 2)):
                    raise ValueError("profile pair shape differs from fixed observation design")
        cohorts[case] = intersect_profiles(profiles, names, ids, table["holdout"],
            minimum_seeds=plan["sample"]["minimum_seeds_per_split"],
            maximum_disagreement=plan["sample"]["maximum_profile_retention_disagreement_fraction"])
    results = {}
    for case in cases:
        profiles = profiles_by_case[case]
        cohort = cohorts[case]
        result = analyze_case(profiles, names, cohort, primary=analysis["primary"], diagnostics=analysis["diagnostics"],
            options=options, variants=analysis["variants"], maximum_joint_span=options.maximum_critical_span)
        reference = np.asarray(reference_states_by_case[case])
        proximity = plan["critical_membership"]
        result["critical_matrix"] = critical_matrix(result["joint_primary"], result["primary_audits"], reference[:, 0],
            interval_padding=proximity["normalized_interval_padding"],
            maximum_slope=proximity["maximum_absolute_normalized_spline_slope"])
        results[case] = {"candidate_id": case,
            "cohort": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in cohort.items()},
            "reference_states": reference.tolist(), "reference_row_indices": list(range(6)), "analysis": result}
    return {"status": "analyzed", "candidate_ids": list(cases), "cases": results,
        "source_commit": source_commit, "plan_sha256": plan_sha256,
        "all_cases_primary_resolved": all(results[c]["analysis"]["joint_primary"]["resolved"] for c in cases),
        "historical_symbols_verified": False,
        "reporting_thresholds": {
            "supported_error_quantile": .9,
            "maximum_supported_q90_error": options.maximum_heldout_q90_error,
            "maximum_unsupported_fraction": options.maximum_heldout_unsupported_fraction,
            "minimum_coverage": options.minimum_coverage},
        "claim_scope": "Operational historical-x adequacy on supported observations from reference-conditioned "
            "retained finite-time cohorts; turns estimated from separate fresh trajectories. Report supported-row "
            "q90 error, unsupported fraction and covered domain. No exclusion of rare sheets, extrapolation through "
            "support gaps, alphabet, arrows or topological proof."}

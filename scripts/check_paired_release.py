#!/usr/bin/env python3
"""Outcome-free live-Git source/review preflight; never dispatch a target phase."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[1]
PLAN = "experiments/manifests/EXP-481-paired-design.json"
MANDATORY_TESTS = ("paired_release", "paired_journal", "paired_capture_inputs", "paired_sections", "paired_decisions",
    "paired_supervisor", "paired_startup", "paired_sampling_plan", "paired_adaptive_journal", "paired_sampling",
    "paired_campaign", "paired_adaptive", "paired_phases", "paired_sampling_preflight", "paired_replay", "paired_input_package",
    "seed_return_map", "poincare", "models")


def check(root, source_commit, remote_ref, *, mode="source",
          release=None, experiment_id="EXP-481"):
    """The actual command's check, also used directly by the campaign controller."""
    root = Path(root).resolve(strict=True)
    if mode not in ("source", "reviewed"):
        raise ValueError("unknown release check mode")
    gate = runpy.run_path(str(root/"python/butterfly/paired_release.py"))
    paths = gate["experiment_paths"](experiment_id)
    release = paths["release"] if release is None else release
    observed = gate["verify_pushed_source"](root, source_commit, remote_ref)
    # Pin this host-side consumer and the builder before evaluating its source
    # map. The worker still verifies the separate realized exact-file bundle.
    bootstrap = ("scripts/check_paired_release.py", "scripts/build_paired_runtime.py", "python/butterfly/paired_release.py")
    for path in bootstrap:
        raw = gate["committed_file"](root, source_commit, path)
        gate["read_bound"](root, dict(path=path, sha256=gate["digest"](raw)))
    mapping = runpy.run_path(str(root/"scripts/build_paired_runtime.py"))["SOURCE_MAP"]
    # Every tracked paired test plus direct numerical dependencies is included;
    # no release-supplied shortened allowlist can remove a required role.
    tracked = gate["git"](root, "ls-tree", "-r", "--name-only", source_commit).decode().splitlines()
    tests = {p for p in tracked if p.startswith("tests/test_paired_") or p in
             ("tests/test_seed_return_map.py", "tests/test_poincare.py", "tests/test_models.py")}
    tests |= {f"tests/test_{name}.py" for name in MANDATORY_TESTS}
    # Source-qualified checkout tests import the public package initializer and
    # older script helpers, not just the small sealed worker package. Bind that
    # broader executable tree too; this does not add it to the worker runtime.
    test_support = {p for p in tracked if p.endswith(".py") and
                    p.startswith(("python/butterfly/", "scripts/"))}
    required = set(mapping.values()) | set(bootstrap) | tests | {
        "tools/review_experiment_plan.py", "pyproject.toml", "uv.lock",
        "scripts/build_paired_inputs.py", "scripts/qualify_paired_startup.py", "scripts/qualify_paired_input_dispatch.py",
        "scripts/qualify_paired_phases.py", "scripts/qualify_paired_runtime.py", "scripts/qualify_paired_adaptive.py",
        "scripts/qualify_paired_sampling.py", "scripts/run_paired_campaign.py",
        # The source-qualified regression suite checks both designs and their
        # exact permitted differences, even when only one is selected to run.
        "experiments/manifests/EXP-481-paired-design.json",
        "experiments/manifests/EXP-482-paired-design.json",
        "experiments/manifests/EXP-481-paired-sampling-draft.json",
        "experiments/manifests/EXP-481-paired-sampling-proposal.json"} | test_support
    files = {}
    for path in sorted(required):
        raw = gate["committed_file"](root, source_commit, path)
        files[path] = dict(bytes=len(raw), sha256=gate["digest"](raw))
    inventory_sha = gate["verify_inventory"](root, source_commit, files, required_paths=required)
    if mode == "reviewed":
        result = gate["verify_reviewed_release"](root, release, source_commit, remote_ref,
            required_source_paths=required, plan_path=paths["plan"], experiment_id=experiment_id)
    else:
        result = dict(status="source-preflight-passed", source=observed, source_files=files,
            source_inventory_sha256=inventory_sha, target_execution_authorized=False,
            scope="live pushed source/test closure only; no review approval, input audit or runtime authorization")
    result["observed_at_utc"] = datetime.now(timezone.utc).isoformat()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--remote-ref", required=True)
    parser.add_argument("--mode", choices=("source", "reviewed"), default="source")
    parser.add_argument("--release")
    parser.add_argument("--experiment-id", choices=("EXP-481", "EXP-482"), default="EXP-481")
    parser.add_argument("--output-dir", type=Path, help="optional fresh local directory for the observed receipt")
    args = parser.parse_args()
    result = check(ROOT, args.source_commit, args.remote_ref, mode=args.mode, release=args.release,
        experiment_id=args.experiment_id)
    if args.output_dir is None:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=False, mode=0o700)
        api = runpy.run_path(str(ROOT/"python/butterfly/_paired_startup.py"))
        api["write_json"](output/"receipt.json", result)
        print(json.dumps(dict(status=result["status"], receipt_sha256=api["sha256"](output/"receipt.json"),
            receipt_bytes=(output/"receipt.json").stat().st_size, target_execution_authorized=False), indent=2))


if __name__ == "__main__":
    main()

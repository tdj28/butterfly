#!/usr/bin/env python3
"""Build an EXP-482 local-audit release candidate; no target/API authorization.

Run after pushing tested source and writing the actual local-audit narrative.
The candidate must be separately committed/pushed and pass the production gate
and fresh setup. No review response or approval is created by this builder.
"""
import argparse
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--remote-ref", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    gate = runpy.run_path(str(ROOT/"python/butterfly/paired_release.py"))
    check = runpy.run_path(str(ROOT/"scripts/check_paired_release.py"))["check"]
    source = check(ROOT, args.source_commit, args.remote_ref, experiment_id="EXP-482")
    def row(path):
        raw = (ROOT/path).read_bytes()
        result = dict(path=path, bytes=len(raw), sha256=gate["digest"](raw))
        gate["read_bound"](ROOT, result)
        return result
    plan = gate["experiment_paths"]("EXP-482")["plan"]
    release = dict(schema="butterfly.paired-local-audit-release.v1", experiment_id="EXP-482",
        paid_review="not_run", code_freeze_commit=args.source_commit, source_files=source["source_files"],
        plan=row(plan), audit=row(gate["LOCAL_AUDIT"]), context={p: row(p) for p in gate["LOCAL_CONTEXT"]})
    output = args.output_dir.absolute()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    api = runpy.run_path(str(ROOT/"python/butterfly/_paired_startup.py"))
    api["write_json"](output/"release.json", release)
    api["write_json"](output/"source.json", source)
    print(json.dumps(dict(status="candidate-only", source_inventory_sha256=source["source_inventory_sha256"],
        release_sha256=api["sha256"](output/"release.json"), target_execution_authorized=False)))


if __name__ == "__main__":
    main()

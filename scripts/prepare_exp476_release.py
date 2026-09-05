#!/usr/bin/env python3
"""Validate explicit EXP-476 assets and prepare local release metadata only.

No upload, archive, copy, Git mutation, or modification of research-core-v1 is
performed. Input files remain at their original paths. Output creation is
exclusive; an existing output directory is never reused or overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .check_public_repository import check_file
except ImportError:  # Direct invocation: python scripts/prepare_exp476_release.py.
    from check_public_repository import check_file


ROOT = Path(__file__).resolve().parents[1]
RELEASE_TAG = "research-exp476"
PROTOCOL_TAG = "exp-476-protocol"
SOURCE_COMMIT = "af90d04e6b484733bb2535a453157c4830691a34"
EXPECTED_HASHES = {
    "receipt.json": "c9818275ed3c585934cdeaa85857b04a5e9a6e1a6400f426a5cbf6e06d5b95bc",
    "mesh-diagnostic.json": "f27a842cc06b48ff8af19edeea83f6d167922e4a2d829f6fc2ce0ff033e8cb74",
    "arithmetic-diagnostic.json": "6efd6d9e5e78399d07880347b98dfd90bdc09fd2ee598a29b245567999ed0aa0",
}


def read_asset(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"asset must be a regular non-symlink file: {path.name}")
    data = path.read_bytes()
    issues = check_file(path.name, data)
    if issues:
        raise ValueError(f"public-file scan rejected {path.name}: {', '.join(issues)} (matching contents suppressed)")
    return data, {"name": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def validate_evidence(documents, hashes):
    raw, mesh, arithmetic = (documents[name] for name in EXPECTED_HASHES)
    if raw.get("experiment_id") != "EXP-476" or raw.get("schema") != "butterfly.projected-homoclinic-pilot-receipt.v2":
        raise ValueError("unexpected raw experiment/schema")
    if raw.get("complete") is not True or raw.get("passed") is not False:
        raise ValueError("EXP-476 must be a complete failed study, not a pass")
    source = raw.get("source", {})
    if source.get("commit") != SOURCE_COMMIT or source.get("dirty") is not False:
        raise ValueError("raw experiment must bind the clean frozen source commit")
    rows = raw.get("cases", [])
    expected_statuses = ["passed"] * 5 + ["failed"] + ["skipped"] * 3
    if [row.get("status") for row in rows] != expected_statuses:
        raise ValueError("expected exactly five passed, one failed, and three skipped cases in frozen order")
    if any(row.get("passed") is not (index < 5) for index, row in enumerate(rows)):
        raise ValueError("case pass flags disagree with the retained failed-study statuses")
    failed = rows[5]
    if failed.get("case", {}).get("name") != "r0.005-tol1e-8" or failed.get("collocation", {}).get("solver_status") != 1:
        raise ValueError("expected the frozen r0.005-tol1e-8 node-budget failure")
    if mesh.get("experiment_id") != "EXP-476" or mesh.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("mesh diagnostic experiment/source identity mismatch")
    if mesh.get("receipt_sha256") != hashes["receipt.json"]:
        raise ValueError("mesh diagnostic raw receipt link mismatch")
    if arithmetic.get("experiment_id") != "EXP-476" or arithmetic.get("raw_receipt_sha256") != hashes["receipt.json"]:
        raise ValueError("arithmetic diagnostic raw receipt link mismatch")
    if arithmetic.get("mesh_diagnostic_sha256") != hashes["mesh-diagnostic.json"]:
        raise ValueError("arithmetic diagnostic mesh receipt link mismatch")
    manifest_hash = raw.get("manifest_sha256")
    if not isinstance(manifest_hash, str) or len(manifest_hash) != 64:
        raise ValueError("raw receipt lacks a manifest hash")
    if any(row.get("manifest_sha256") != manifest_hash for row in (mesh, arithmetic)):
        raise ValueError("diagnostic manifest links differ from the frozen experiment")


def positive_count(value, label):
    if value is not None and (type(value) is not int or value <= 0):
        raise ValueError(f"{label} must be a positive integer when supplied")


def release_body(assets, manuscript_pages=None, manuscript_figures=None):
    positive_count(manuscript_pages, "manuscript pages")
    positive_count(manuscript_figures, "manuscript figures")
    counts = []
    if manuscript_pages is not None:
        counts.append(f"{manuscript_pages} pages")
    if manuscript_figures is not None:
        counts.append(f"{manuscript_figures} figures")
    manuscript_description = "Current illustrated manuscript"
    if counts:
        manuscript_description += f" ({', '.join(counts)}; counts supplied by the release operator)"
    lines = [
        "# EXP-476: retained failed refinement study",
        "",
        "This separate research-exp476 release preserves a prospectively frozen study that did **not** pass: five cases passed, the sixth failed, and the final three were skipped under the committed stop rule.",
        "",
        f"Frozen protocol: [{PROTOCOL_TAG}](https://github.com/tdj28/butterfly/tree/{PROTOCOL_TAG}), source commit `{SOURCE_COMMIT}` (clean at execution).",
        "",
        "The separate [research-exp476 source tag](https://github.com/tdj28/butterfly/tree/research-exp476) identifies the later diagnostic scripts, tests, and manuscript. Those post-result changes were not part of the frozen target run.",
        "",
        "The r0.005-tol1e-8 case failed when its requested mesh refinement exceeded the declared node budget. A small short-arc endpoint replay defect does not override the failed collocation residual gate. No target rerun, increased cap, or post-result acceptance change is included.",
        "",
        "The two post-hoc diagnostics inspect saved meshes and reevaluate two selected intervals at 80-digit arithmetic, with synthetic controls. They perform no new orbit integration or BVP solve. Their findings do not convert the failed case into a pass or establish a homoclinic existence proof, a rigorous parameter interval, trajectory uniqueness, Jones's printed coordinate, or the later continuation turn.",
        "",
        "## Assets",
        "",
        "- `receipt.json`: the complete original experiment receipt, including retained unsuccessful data and skipped statuses.",
        "- `mesh-diagnostic.json`: hash-bound, read-only saved-mesh inspection.",
        "- `arithmetic-diagnostic.json`: hash-bound, fixed-interval arithmetic inspection; archived binary64 inputs are interpreted exactly, without recovering lost digits.",
        f"- `manuscript.pdf`: {manuscript_description}.",
        "- `SHA256SUMS`: hashes of the four assets above, using their exact release basenames.",
        "",
        "After downloading all four assets and SHA256SUMS into one directory, verify with:",
        "",
        "```sh",
        "shasum -a 256 -c SHA256SUMS",
        "```",
        "",
        "The earlier research-core-v1 release is unchanged. This release is additional failed-study evidence, not a replacement for the original reproducible core.",
        "",
        "| Asset | Bytes | SHA-256 |",
        "| --- | ---: | --- |",
    ]
    lines.extend(f"| `{asset['name']}` | {asset['bytes']} | `{asset['sha256']}` |" for asset in assets)
    return "\n".join(lines) + "\n"


def prepare_release(input_dir, manuscript, output_dir, *, expected_hashes=None, manuscript_pages=None, manuscript_figures=None):
    """Prepare metadata after validation; hash overrides are for synthetic tests.

    The CLI always uses the frozen EXPECTED_HASHES and exposes no hash override.
    No source paths, host information, or credentials enter the release files.
    """
    if output_dir.exists() or output_dir.is_symlink():
        raise ValueError("release output already exists; refusing to overwrite or reuse it")
    if manuscript.name != "manuscript.pdf":
        raise ValueError("manuscript asset basename must remain manuscript.pdf")
    expected_hashes = EXPECTED_HASHES if expected_hashes is None else expected_hashes
    if set(expected_hashes) != set(EXPECTED_HASHES):
        raise ValueError("exactly the three frozen JSON inputs must be specified")
    assets, documents = [], {}
    for name in EXPECTED_HASHES:
        data, asset = read_asset(input_dir / name)
        if asset["sha256"] != expected_hashes[name]:
            raise ValueError(f"frozen asset hash mismatch: {name}")
        documents[name] = json.loads(data)
        assets.append(asset)
    validate_evidence(documents, expected_hashes)
    pdf, pdf_asset = read_asset(manuscript)
    if not pdf.startswith(b"%PDF-") or b"%%EOF" not in pdf[-1024:]:
        raise ValueError("manuscript does not have a complete PDF header/trailer; finish and verify the PDF build first")
    assets.append(pdf_asset)
    body = release_body(assets, manuscript_pages, manuscript_figures)
    checksum_text = "".join(f"{asset['sha256']}  {asset['name']}\n" for asset in assets)
    inventory = {
        "schema": "butterfly.exp476-release-preparation.v1", "release_tag": RELEASE_TAG,
        "protocol_tag": PROTOCOL_TAG, "experiment_id": "EXP-476", "source_commit": SOURCE_COMMIT,
        "experiment_passed": False, "case_status_counts": {"passed": 5, "failed": 1, "skipped": 3},
        "assets": assets, "uploaded": False, "copied": False,
        "credential_scan": "explicit inputs checked with check_public_repository.check_file; bounded pattern scan, not exhaustive detection",
    }
    outputs = {
        "SHA256SUMS": checksum_text.encode(), "release-body.md": body.encode(),
        "asset-inventory.json": (json.dumps(inventory, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(),
    }
    for name, data in outputs.items():
        if check_file(name, data):
            raise ValueError(f"public-file scan rejected generated metadata: {name} (matching contents suppressed)")
    output_dir.mkdir(parents=True, exist_ok=False)
    for name, data in outputs.items():
        with (output_dir / name).open("xb") as destination:
            destination.write(data)
    return inventory


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "artifacts/EXP-476")
    parser.add_argument("--manuscript", type=Path, default=ROOT / "paper/manuscript.pdf")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/EXP-476/release")
    parser.add_argument("--manuscript-pages", type=int)
    parser.add_argument("--manuscript-figures", type=int)
    args = parser.parse_args(argv)
    result = prepare_release(
        args.input_dir, args.manuscript, args.output_dir,
        manuscript_pages=args.manuscript_pages, manuscript_figures=args.manuscript_figures,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

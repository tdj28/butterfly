#!/usr/bin/env python3
"""Audit the fixed EXP-480 result and generate a descriptive figure/backup tar.

No solver, partition fit, word encoder or remote connection is invoked.
"""
import io
import json
from pathlib import Path
import tarfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from scripts import run_symbolic_center_pilot as evidence

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "artifacts/EXP-480/run-5b584f4"
RECEIPT_SHA = "aa4556cdfbca2fa277c8e77daec00f01190e0a8bfde33d9977e5a594c58127b9"
SOURCE = "5b584f4a0cf2fe4544e22d5288878300efd35469"


def audit():
    if evidence.sha256_file(RUN / "receipt.json") != RECEIPT_SHA:
        raise ValueError("fixed terminal receipt changed")
    receipt = json.loads((RUN / "receipt.json").read_bytes())
    if receipt["source"]["commit"] != SOURCE or receipt["status"] != "completed":
        raise ValueError("wrong source or incomplete run")
    names = {"receipt.json", "started.json"}
    for row in receipt["files"]:
        evidence.collection_file(RUN, row)
        names.add(row["path"])
    if {p.name for p in RUN.iterdir()} != names:
        raise ValueError("missing or unexpected run evidence")
    return receipt


def figure(receipt, output):
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), gridspec_kw={"height_ratios": [3, 1]})
    colors = {"historical-negative": "#008a91", "barrio-positive": "#d97928"}
    labels = {"historical-negative": "Historical section (6)", "barrio-positive": "Barrio section (8)"}
    for col, case in enumerate(receipt["case_outcomes"]):
        row = next(r for r in receipt["profiles"] if r["candidate_id"] == case["candidate_id"] and r["profile"]["name"] == "dop853")
        period = row["correction"]["period_time"]
        with np.load(RUN / row["raw"]["path"], allow_pickle=False) as raw:
            mask = (raw["integration_times"] >= .25*period) & (raw["integration_times"] < 1.25*period)
            path = raw["integration_states"][mask]
        ax, timeline = axes[:, col]
        ax.plot(path[:, 0], path[:, 1], color="#253c53", lw=.8, alpha=.7)
        for level, name in enumerate(colors):
            window = row["sections"][name]["windows"][0]
            states = np.asarray(window["states"])
            ax.scatter(states[:, 0], states[:, 1], color=colors[name], s=24, label=labels[name], zorder=3)
            timeline.scatter(window["phases"], np.full(len(states), level), color=colors[name], marker="|", s=180)
        value = "0.21575" if col == 0 else "0.21577"
        ax.set(title=f"a = {value}  |  T = {period:.6f}", xlabel="x", ylabel="y", aspect="equal")
        ax.legend(frameon=False, fontsize=8, loc="upper right")
        timeline.set(xlim=(0, 1), ylim=(-.5, 1.5), xlabel="Phase in fixed one-period window",
                     yticks=[0, 1], yticklabels=["Historical", "Barrio"])
        for axis in (ax, timeline):
            axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Same flow cycle, different section returns", fontsize=16, y=.99)
    fig.text(.5, .935, "EXP-480  ·  b = 0.2, c = 7.212  ·  all four solver profiles qualify", ha="center", color="#475569")
    fig.text(.5, .01, "Markers are observed events—not a symbolic partition or a verified cross-section correspondence.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, .91))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main():
    receipt = audit()
    output = ROOT / "artifacts/EXP-480/audit-and-archive"
    output.mkdir(parents=True, exist_ok=False)
    comparisons = [s for c in receipt["comparisons"] for s in c["sections"].values()]
    compact = {"experiment_id": "EXP-480", "source_commit": SOURCE, "raw_receipt_sha256": RECEIPT_SHA,
        "status": receipt["status"], "passed": receipt["passed"], "outcome": receipt["outcome"],
        "case_outcomes": receipt["case_outcomes"], "profile_count": len(receipt["profiles"]),
        "audited_files": len(receipt["files"]), "audited_bytes": sum(x["bytes"] for x in receipt["files"]),
        "elapsed_seconds": receipt["elapsed_seconds"],
        "maximum_cross_profile_scaled_state_error": max(x["maximum_scaled_state_error"] for x in comparisons),
        "maximum_cross_profile_phase_error": max(x["maximum_phase_error"] for x in comparisons),
        "claim_scope": receipt["claim_scope"]}
    evidence.write_new_json(output / "audit.json", compact)
    figure(receipt, output / "paired-section-events.png")
    entries = [("run/" + p.name, p) for p in sorted(RUN.iterdir())]
    # These exact inputs are already public-research evidence; never archive .env.
    entries += [("inputs/candidates.json", ROOT / "artifacts/EXP-204/candidates.json"),
                ("inputs/nomination-receipt.json", ROOT / "artifacts/EXP-479/analysis-30f6c5b/receipt.json")]
    for name, expected in [("candidates.json", "71aab52016abc8163887b2bdfd4e8124bde0e436be2239751f19d29bed490012"),
                           ("nomination-receipt.json", "4147ff20adefb6adf536137cb0a92809446ce66d40c20b6c00f909fa6235755f")]:
        path = dict(entries)["inputs/"+name]
        if evidence.sha256_file(path) != expected:
            raise ValueError("input changed")
    inventory = [{"path": name, "bytes": p.stat().st_size, "sha256": evidence.sha256_file(p)} for name, p in entries]
    manifest = {"schema": "butterfly.exp480-archive.v1", "source_commit": SOURCE,
                "source_remote_ref": "codex/exp480-execution", "assets": inventory}
    archive = output / "evidence.tar"
    with tarfile.open(archive, "x", format=tarfile.USTAR_FORMAT) as tar:
        data = evidence.encoded_json(manifest)
        member = tarfile.TarInfo("manifest.json")
        member.size, member.mode = len(data), 0o600
        tar.addfile(member, io.BytesIO(data))
        for name, path in entries:
            if path.is_symlink():
                raise ValueError("symlink refused")
            member = tarfile.TarInfo(name)
            member.size, member.mode = path.stat().st_size, 0o600
            with path.open("rb") as stream:
                tar.addfile(member, stream)
    archive.chmod(0o600)
    from scripts.archive_exp479_cpu import verify_tar
    verify_tar(archive, manifest)  # Generic streamed byte audit only; no EXP-479 upload/preparation.
    evidence.write_new_json(output / "archive.json", {"path": "evidence.tar", "bytes": archive.stat().st_size,
        "sha256": evidence.sha256_file(archive), "assets": len(inventory), "source_commit": SOURCE})
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()

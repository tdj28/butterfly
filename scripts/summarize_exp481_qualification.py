#!/usr/bin/env python3
"""Audit and preserve the stopped EXP-481 qualification; never integrate or retry.

Default: local raw replay, descriptive plot and fresh owner-only backup tar.
--upload: verify that prepared archive, copy once to a fresh task-owned prax
directory, and verify its bytes/modes remotely without extracting anything.
"""
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

from butterfly._paired_startup import inventory, sha256, write_json
from butterfly.paired_input_package import load_package
from butterfly.paired_inputs import load_references
from butterfly.paired_phases import from_reference_audit, _compare_qualification
from scripts.archive_exp479_cpu import remote_command, verify_tar
from scripts.symbolic_ssh_storage import ssh_options

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "83a737a74d64cacc4028c1bb624a9817f395dbbd"
RUN = ROOT/"artifacts/EXP-481/target-83a737a"
OUTPUT = ROOT/"artifacts/EXP-481/qualification-result-01"
REMOTE = "/home/ubuntu/butterfly-research/exp481-stopped-20260907-83a737a"
ANCHORS = {
    "preflight/receipt.json": "f020f833d467b450e56834c55d5501b40e8c8facfbc6959d5664899d7e75d756",
    "campaign/qualification/phase/terminal.json": "51e4cf10dc4c3c2a4706a321fec6314251e9ca59ff2e234c275ed32452ecf2d9",
    "campaign/qualification/phase-witness.json": "7286577ced87f3e33b6329bc64a6c09a8a09fab1a0abee1c3a5fd5859c6da8ad",
    "campaign/qualification/supervisor/terminal.json": "7a2d389991a2036f2874cb9edab131e76ea519445a86621b410de832c68fd8dd",
    "campaign/failure.json": "3d3445cb72cc0c216ca000317bd3072aba52146e16e270cd5cc353fdaa5f01c1",
}


def comparison_summary(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row["left"], row["right"])].append(row)
    result = []
    for pair, group in groups.items():
        sections = [s for r in group for s in r["sections"].values()]
        def maximum(key):
            values = [s.get(key) for s in sections if s.get(key) is not None]
            return max(values) if values else None
        result.append(dict(left=pair[0], right=pair[1], passed=sum(r["passed"] for r in group), total=len(group),
            maximum_scaled_state_difference=maximum("maximum_scaled_state_difference"),
            maximum_time_difference=maximum("maximum_time_difference"),
            capture_mismatches=sum(not r["capture_membership_agrees"] for r in group),
            count_mismatches=sum(s["left_raw_count"] != s["right_raw_count"] or
                s["left_accepted_count"] != s["right_accepted_count"] for s in sections)))
    return result


def audit():
    observed = inventory(RUN)
    for name, expected in ANCHORS.items():
        if observed[name]["sha256"] != expected:
            raise ValueError("stopped-run anchor changed")
    pre = json.loads((RUN/"preflight/receipt.json").read_bytes())
    package = RUN/"preflight/inputs"
    plan = load_package(package, pre["inputs"]["sha256"])
    references = load_references(plan, package)
    design, _ = from_reference_audit(plan, references, source_commit=SOURCE, plan_sha256=pre["plan_sha256"])
    phase = RUN/"campaign/qualification/phase"
    terminal = json.loads((phase/"terminal.json").read_bytes())
    trials = [t for t in design.validate() if t.stage == "qualification"]
    if (terminal["status"] != "completed" or terminal["passed"] is not False
            or terminal["design_sha256"] != design.identity()
            or terminal["trial_ids"] != [t.trial_id for t in trials]
            or inventory(phase, omit=("terminal.json",)) != terminal["files"]):
        raise ValueError("incomplete or changed qualification phase")
    rows = {t.trial_id: json.loads((phase/"receipts"/(t.trial_id+".json")).read_bytes()) for t in trials}
    for t in trials:
        if rows[t.trial_id]["binding"] != design.binding(t) or rows[t.trial_id]["status"] != "completed":
            raise ValueError("trial identity/status differs")
    # Replay all original RK4/adaptive journals and independently reconsume
    # their external descriptors; do not merely aggregate reported pass flags.
    recomputed = _compare_qualification(design, trials, rows, phase)
    if recomputed != json.loads((phase/"comparisons.json").read_bytes()):
        raise ValueError("raw replay differs from all recorded comparisons")
    supervisor = json.loads((RUN/"campaign/qualification/supervisor/terminal.json").read_bytes())
    if supervisor["status"] != "completed" or not supervisor["owned_group_cleanup_verified"]:
        raise ValueError("qualification worker did not cleanly finish")
    if any((RUN/"campaign"/p).exists() for p in ("collection", "analysis", "receipt.json")):
        raise ValueError("unexpected downstream execution")
    if inventory(RUN) != observed:
        raise ValueError("run changed during post-run audit")
    return dict(experiment_id="EXP-481", source_commit=SOURCE, status="numerically-not-qualified",
        qualification_trials=len(trials), comparison_count=len(recomputed),
        comparisons_passed=sum(r["passed"] for r in recomputed), groups=comparison_summary(recomputed),
        target_collection_batches=0, target_analysis_performed=False, target_attempt_consumed=True,
        raw_comparison_replay_exact=True, supervisor=supervisor,
        historical_symbols_verified=False, threshold=plan["adaptive_qualification"]["maximum_scaled_event_state_difference"],
        scope="RK4 step settings fail frozen early event-state accuracy; not a refutation of Jones or a map result",
        run_anchors={p:{"path":p, **observed[p]} for p in ANCHORS}), observed


def plot(summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = [r["left"].replace("rk4-001", "RK4 .01").replace("rk4-0005", "RK4 .005")+"\nvs "+
        r["right"].replace("rk4-0005", "RK4 .005") for r in summary["groups"]]
    errors = [r["maximum_scaled_state_difference"] for r in summary["groups"]]
    fig, ax = plt.subplots(figsize=(10, 4.7), layout="constrained")
    ax.bar(range(6), errors, color=["#c66c3a"]*5+["#237c83"], width=.65)
    ax.set_yscale("log")
    ax.axhline(summary["threshold"], color="#334155", linestyle="--", label="Frozen accuracy limit")
    ax.set_xticks(range(6), labels, fontsize=9)
    ax.set_ylabel("Maximum scaled event-state disagreement")
    ax.set_title("EXP-481: adaptive solvers agree; the chosen RK4 steps are too coarse", loc="left", fontsize=13)
    for i, row in enumerate(summary["groups"]):
        ax.text(i, errors[i]*1.45, f"{row['passed']}/{row['total']} pass", ha="center", fontsize=9)
    ax.set_ylim(min(errors)*.3, max(errors)*8)
    ax.legend(frameon=False, loc="lower left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(output/"qualification-errors.png", dpi=180)
    fig.savefig(output/"qualification-errors.pdf")
    plt.close(fig)


def prepare():
    summary, files = audit()
    OUTPUT.mkdir(parents=True, exist_ok=False, mode=0o700)
    write_json(OUTPUT/"summary.json", summary)
    plot(summary, OUTPUT)
    entries = [("run/"+p, RUN/p) for p in files]
    entries += [("audit/"+p, OUTPUT/p) for p in ("summary.json", "qualification-errors.png", "qualification-errors.pdf")]
    entries += [("target-once.json", ROOT/"artifacts/EXP-481/target-once.json"),
                ("audit-source.py", Path(__file__))]
    rows = [dict(path=name, bytes=p.stat().st_size, sha256=sha256(p)) for name,p in entries]
    if len(rows)>7000 or sum(r["bytes"] for r in rows)>128*1024**2:
        raise ValueError("archive exceeds fixed post-run bounds")
    manifest = dict(schema="butterfly.exp481-stopped-archive.v1", source_commit=SOURCE,
        assets=rows, local_originals_retained=True)
    data=(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode()
    archive=OUTPUT/"evidence.tar"
    with tarfile.open(archive,"x",format=tarfile.PAX_FORMAT) as tar:
        info=tarfile.TarInfo("manifest.json");info.size=len(data);info.mode=0o600
        tar.addfile(info,io.BytesIO(data))
        for row,(_,p) in zip(rows,entries,strict=True):
            if p.is_symlink():raise ValueError("symlink archive member")
            info=tarfile.TarInfo(row["path"]);info.size=row["bytes"];info.mode=0o600
            with p.open("rb") as stream:tar.addfile(info,stream)
    archive.chmod(0o600)
    verify_tar(archive,manifest)
    if inventory(RUN)!=files:raise ValueError("run changed during archive")
    write_json(OUTPUT/"manifest.json",manifest)
    receipt=dict(archive_bytes=archive.stat().st_size,archive_sha256=sha256(archive),
        manifest_sha256=sha256(OUTPUT/"manifest.json"),summary_sha256=sha256(OUTPUT/"summary.json"),
        source_commit=SOURCE,remote=REMOTE,originals_retained=True,uploaded=False)
    write_json(OUTPUT/"prepared.json",receipt)
    print(json.dumps(receipt,indent=2))


def upload():
    prepared=json.loads((OUTPUT/"prepared.json").read_bytes());archive=OUTPUT/"evidence.tar"
    if sha256(archive)!=prepared["archive_sha256"] or sha256(OUTPUT/"manifest.json")!=prepared["manifest_sha256"]:
        raise ValueError("prepared archive changed")
    verify_tar(archive,json.loads((OUTPUT/"manifest.json").read_bytes()))
    write_json(OUTPUT/"upload-started.json",dict(remote=REMOTE,archive_sha256=prepared["archive_sha256"],automatic_retry=False))
    create="import pathlib,shutil,sys\np=pathlib.Path(sys.argv[1])\nif any(q.is_symlink() for q in [p,*p.parents]): raise ValueError('symlink')\nif shutil.disk_usage(p.parent).free<268435456: raise ValueError('space')\np.mkdir(mode=0o700)"
    subprocess.run(remote_command(create,REMOTE),check=True,timeout=30,capture_output=True)
    subprocess.run(["scp",*ssh_options(),str(archive),"ubuntu@prax:"+REMOTE+"/evidence.tar"],check=True,timeout=180,capture_output=True)
    verify="import pathlib,hashlib,json,sys\np=pathlib.Path(sys.argv[1])\nwith p.open('rb') as f: h=hashlib.file_digest(f,'sha256').hexdigest()\nprint(json.dumps(dict(bytes=p.stat().st_size,sha256=h,file_mode=p.stat().st_mode&511,directory_mode=p.parent.stat().st_mode&511)))"
    result=subprocess.run(remote_command(verify,REMOTE+"/evidence.tar"),check=True,timeout=30,capture_output=True,text=True)
    observed=json.loads(result.stdout)
    if observed!=dict(bytes=prepared["archive_bytes"],sha256=prepared["archive_sha256"],file_mode=0o600,directory_mode=0o700):
        raise ValueError("remote archive mismatch; preserve partial transfer")
    write_json(OUTPUT/"upload.json",dict(verified=True,remote=REMOTE,observed=observed,originals_retained=True))
    print(json.dumps(dict(verified=True,remote=REMOTE,**observed)))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upload",action="store_true")
    upload() if parser.parse_args().upload else prepare()

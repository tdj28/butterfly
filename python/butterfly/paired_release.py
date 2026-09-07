"""Read-only source and adjudicated-review gates for the paired controller.

Standard library only; no target dispatch, key loading, API request or receipt
issuance. The caller supplies the complete frozen path closure. Git/SSH, the
host filesystem and the preserved provider response remain trust anchors, not
cryptographic proof of provider authorship or global one-call uniqueness.
"""
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess


CANONICAL_REVIEW_HELPER = "tools/review_experiment_plan.py"
CANONICAL_REVIEW_HELPER_SHA256 = "7ebe3185868e0f4ebe07c162a95c7c2195669e02ce5dde088aad0456859b6dff"
REMOTE = "git@github.com:tdj28/butterfly.git"
MAXIMUM_BYTES = 16*1024**2
HEADINGS = ("Verdict", "Blocking findings", "Important non-blocking findings", "What should remain unchanged",
            "Minimal revised design", "Freeze checklist")
VERDICTS = ("NOT READY TO FREEZE", "READY AFTER SPECIFIED FIXES", "READY TO FREEZE")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def relative_path(value):
    if (not isinstance(value, str) or not value or not Path(value).parts or Path(value).is_absolute()
            or Path(value).as_posix() != value or any(p in (".", "..") for p in Path(value).parts)
            or any(c in value for c in ("\0", "\n", "\r", "\t", "\\"))):
        raise ValueError("canonical repository-relative path required")
    return value


def hex_value(value, count):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{"+str(count)+"}", value) is None:
        raise ValueError("full hexadecimal binding required")
    return value


def read_bound(root, row):
    relative = relative_path(row["path"])
    path = Path(root).resolve(strict=True)
    for part in Path(relative).parts:
        path = path/part
        if path.is_symlink():
            raise ValueError("symlink in bound release file")
    if not path.is_file() or path.stat().st_size > MAXIMUM_BYTES:
        raise ValueError("missing, nonregular or oversized release file")
    with path.open("rb") as stream:
        raw = stream.read(MAXIMUM_BYTES+1)
    if (len(raw) > MAXIMUM_BYTES or digest(raw) != hex_value(row["sha256"], 64)
            or ("bytes" in row and (type(row["bytes"]) is not int or row["bytes"] != len(raw)))):
        raise ValueError("release file differs from bound bytes")
    return raw


def git(root, *args):
    result = subprocess.run(["git", "--no-replace-objects", "--no-optional-locks", "--literal-pathspecs",
        "-c", "core.fsmonitor=false", "-C", str(root), *args], capture_output=True, timeout=45)
    if result.returncode:
        raise ValueError("required Git source/remote check failed")
    return result.stdout


def committed_file(root, commit, path):
    hex_value(commit, 40)
    relative_path(path)
    row = git(root, "ls-tree", "-z", commit, "--", path)
    fields = row.rstrip(b"\0").split(b"\t")
    if len(fields) != 2 or fields[1].decode() != path:
        raise ValueError("path missing from exact commit")
    mode, kind, oid = fields[0].decode().split()
    if mode not in ("100644", "100755") or kind != "blob":
        raise ValueError("committed path must be an ordinary file")
    if int(git(root, "cat-file", "-s", oid)) > MAXIMUM_BYTES:
        raise ValueError("oversized committed release file")
    return git(root, "cat-file", "blob", oid)


def verify_inventory(root, commit, files, *, required_paths, current=True):
    """Verify exact required roles against Git objects, not copied hash fields."""
    if not files or set(files) != set(required_paths):
        raise ValueError("release inventory differs from complete required closure")
    for path, row in files.items():
        raw = committed_file(root, commit, path)
        if set(row) != {"bytes", "sha256"} or row != {"bytes": len(raw), "sha256": digest(raw)}:
            raise ValueError("inventory differs from independently committed bytes")
        if current and read_bound(root, {"path": path, **row}) != raw:
            raise ValueError("checkout differs from exact committed source")
    return digest(canonical(files))


def verify_pushed_source(root, commit, remote_ref, *, expected_remote=REMOTE):
    """Observe exact local HEAD and live remote ref; cannot prove a historic push time."""
    hex_value(commit, 40)
    if not isinstance(remote_ref, str) or re.fullmatch(r"refs/heads/[A-Za-z0-9][A-Za-z0-9._/-]*", remote_ref) is None:
        raise ValueError("explicit remote branch ref required")
    git(root, "check-ref-format", remote_ref)
    if git(root, "remote", "get-url", "origin").decode().strip() != expected_remote:
        raise ValueError("origin differs from independently declared repository")
    if git(root, "rev-parse", "HEAD").decode().strip() != commit:
        raise ValueError("local HEAD differs from execution freeze")
    # Tracked changes are forbidden. Ignored artifacts do not change source;
    # untracked modules cannot enter the separate exact-file sealed runtime.
    if git(root, "status", "--porcelain", "--untracked-files=no").strip():
        raise ValueError("tracked checkout changes invalidate execution freeze")
    actual = git(root, "ls-remote", "--exit-code", "origin", remote_ref).decode().splitlines()
    if actual != [commit+"\t"+remote_ref]:
        raise ValueError("live remote ref differs from exact execution freeze")
    return dict(commit=commit, remote=expected_remote, remote_ref=remote_ref, live_remote_matches=True)


def parse_review(text):
    """Exact terminal verdict inside # Verdict; structural B/I heading IDs only."""
    sections, active, fenced = {}, None, False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced and line.startswith("# "):
            heading = line[2:].strip()
            if heading not in HEADINGS or heading in sections:
                raise ValueError("review needs the exact unique top-level section set")
            active = heading
            sections[active] = []
        elif active is not None:
            # Quoted code cannot introduce a verdict or finding heading. Keep
            # ordinary prose, but exclude both fences and their quoted bodies.
            if not fenced and not line.lstrip().startswith(("```", "~~~")):
                sections[active].append(line)
        elif line.strip():
            raise ValueError("unexpected prose before review verdict")
    if fenced or tuple(sections) != HEADINGS:
        raise ValueError("review section structure is incomplete or reordered")
    lines = [s.strip() for s in sections["Verdict"] if s.strip()]
    verdicts = [s for s in lines if s in VERDICTS]
    if len(verdicts) != 1 or not lines or lines[-1] != verdicts[0]:
        raise ValueError("one exact terminal verdict line required")
    findings = {}
    for heading, prefix in (("Blocking findings", "B"), ("Important non-blocking findings", "I")):
        content = sections[heading]
        ids = []
        for line in content:
            if line.startswith("## "):
                match = re.fullmatch(r"## ([BI][0-9]{2})(?:\s+[—–:-]\s+.+)?\s*", line)
                if match is None or not match[1].startswith(prefix) or match[1] in findings:
                    raise ValueError("unparseable, misplaced or duplicate finding heading")
                findings[match[1]] = "blocking" if prefix == "B" else "important"
                ids.append(match[1])
        if not ids and " ".join(s.strip() for s in content if s.strip()).lower() not in ("none", "none."):
            raise ValueError("no-finding section must explicitly say none")
    return verdicts[0], findings


def adjudicate(review_text, adjudication, reviewed_files, final_files):
    """Account for every finding and every source/design change; no blanket approval."""
    verdict, findings = parse_review(review_text)
    if verdict == "NOT READY TO FREEZE":
        raise ValueError("negative review cannot authorize this release")
    if adjudication.get("approved_for_execution") is not True or adjudication.get("verdict") != verdict:
        raise ValueError("adjudication is not approved for the exact review verdict")
    rows = adjudication["findings"]
    by_id = {r["id"]: r for r in rows}
    if len(by_id) != len(rows) or set(by_id) != set(findings):
        raise ValueError("every actual finding must be adjudicated exactly once")
    for name, row in by_id.items():
        decision = row["decision"]
        if (decision not in ("accept", "accepted_modified", "reject", "defer")
                or not isinstance(row.get("rationale"), str) or not row["rationale"].strip()
                or not isinstance(row.get("resolution"), str) or not row["resolution"].strip()
                or type(row.get("authorizes_change")) is not bool
                or (findings[name] == "blocking" and decision == "defer")
                or (decision == "defer" and not row.get("claim_narrowing"))
                or (decision == "reject" and row["authorizes_change"])):
            raise ValueError("unresolved or invalid finding disposition")
    changed = {p for p in set(reviewed_files) | set(final_files) if reviewed_files.get(p) != final_files.get(p)}
    changes = adjudication["changes"]
    if len({r["path"] for r in changes}) != len(changes) or {r["path"] for r in changes} != changed:
        raise ValueError("every changed, added or removed path needs an exact change mapping")
    for row in changes:
        relative_path(row["path"])
        ids = row["findings"]
        if (row["before"] != reviewed_files.get(row["path"]) or row["after"] != final_files.get(row["path"])
                or not ids or len(set(ids)) != len(ids)
                or any(i not in by_id or not by_id[i]["authorizes_change"] for i in ids)):
            raise ValueError("change differs from inventories or authorized finding fixes")
    if verdict == "READY AFTER SPECIFIED FIXES" and not changes:
        raise ValueError("specified-fixes verdict needs recorded implemented changes")
    for key, expected in (("reviewed_inventory_sha256", digest(canonical(reviewed_files))),
                          ("final_inventory_sha256", digest(canonical(final_files))),
                          ("review_sha256", digest(review_text.encode()))):
        if adjudication.get(key) != expected:
            raise ValueError("adjudication refers to different review or inventories")
    own = {k: v for k, v in adjudication.items() if k != "self_sha256"}
    if adjudication.get("self_sha256") != digest(canonical(own)):
        raise ValueError("adjudication self-hash mismatch")
    return dict(verdict=verdict, finding_ids=list(findings), changed_paths=sorted(changed),
                claim="locally adjudicated review; changed source not inspected by provider")


def validate_review_bundle(root, declaration):
    """Use the byte-pinned canonical helper, only its credential-free validator.

    The enclosing source gate must bind declaration to committed release bytes.
    Matching a local response to a request is not a provider digital signature.
    """
    helper_raw = read_bound(root, dict(path=CANONICAL_REVIEW_HELPER, sha256=CANONICAL_REVIEW_HELPER_SHA256))
    helper = runpy.run_path(str(Path(root)/CANONICAL_REVIEW_HELPER))
    roles = declaration["artifacts"]
    if set(roles) != {"brief", "contexts", "bundle"} or not 1 <= len(roles["contexts"]) <= 3:
        raise ValueError("one brief and one to three compact contexts required")
    expected_names = {"manifest": "review_manifest.json", "request_payload": "request_payload.json",
                      "request": "review_request.md", "response": "response.json", "review": "review.md"}
    if set(roles["bundle"]) != set(expected_names):
        raise ValueError("complete actual request/response/review bundle required")
    before = {}
    for row in (roles["brief"], *roles["contexts"], *roles["bundle"].values()):
        if row["path"] in before:
            raise ValueError("review artifact roles must be distinct")
        before[row["path"]] = read_bound(root, row)
    brief = helper["read_artifact"](Path(root)/roles["brief"]["path"], "compact research-director plan brief")
    contexts = [helper["read_artifact"](Path(root)/row["path"], f"synthesized context {i}")
                for i, row in enumerate(roles["contexts"], 1)]
    paths = helper["CompletedReviewBundlePaths"](**{k: Path(root)/row["path"] for k, row in roles["bundle"].items()})
    result = helper["validate_completed_review_bundle"](plan=brief, contexts=contexts, paths=paths,
        researcher_question=None, review_kind="experiment-plan")
    manifest = json.loads(before[roles["bundle"]["manifest"]["path"]])
    if (manifest.get("researcher_emphasis") != {"present": False, "text": None, "sha256": None}
            or manifest.get("reasoning", {}).get("mode") != "pro"
            or manifest.get("reviewed_packet_git_head_commit") != declaration["reviewed_packet_commit"]
            or manifest.get("model") != declaration["model"] or result["response_id"] != declaration["response_id"]
            or result["review_input_sha256"] != declaration["review_input_sha256"]
            or manifest.get("completed_response_cost_exceeded_budget_authorization") is not False):
        raise ValueError("completed review differs from frozen packet/model/budget policy")
    for row in (roles["brief"], *roles["contexts"], *roles["bundle"].values()):
        if read_bound(root, row) != before[row["path"]]:
            raise ValueError("review bundle changed during validation")
    if read_bound(root, dict(path=CANONICAL_REVIEW_HELPER, sha256=CANONICAL_REVIEW_HELPER_SHA256)) != helper_raw:
        raise ValueError("canonical validator changed during validation")
    verdict, findings = parse_review(before[roles["bundle"]["review"]["path"]].decode())
    return {**result, "verdict": verdict, "finding_ids": list(findings), "target_execution_authorized": False}


def decision_context(plan, inventory_sha256):
    """Exact compact context submitted to Pro, independently rebuilt by the gate.

    The numeric design is an input, not the administratively mutable release.
    Review artifacts themselves are excluded from this inventory to avoid a
    self-referential hash. Their exact bytes are bound by the producer bundle.
    """
    hex_value(inventory_sha256, 64)
    return ("# EXP-481 decision context\n\nThe following is the complete machine design. "
        "The source/test inventory is verified locally, not inspected by the reviewer.\n\n"
        f"Source/design inventory SHA-256: `{inventory_sha256}`\n\n```json\n"
        +json.dumps(plan, sort_keys=True, indent=2, allow_nan=False)+"\n```\n")


def verify_reviewed_release(root, release_path, freeze_commit, remote_ref, *, required_source_paths, plan_path):
    """Compose source and review checks; runtime handshake/one-shot gate is separate.

    The production caller fixes the complete closure and plan role in source;
    never obtain those roles from the release being validated. This read-only
    check does not claim the as-yet-unimplemented launch gate has passed.
    """
    source = verify_pushed_source(root, freeze_commit, remote_ref)
    raw = committed_file(root, freeze_commit, release_path)
    if read_bound(root, dict(path=release_path, bytes=len(raw), sha256=digest(raw))) != raw:
        raise ValueError("release differs from pushed Git object")
    release = json.loads(raw)
    if (release.get("schema") != "butterfly.paired-reviewed-release.v1"
            or release.get("experiment_id") != "EXP-481" or release.get("approved_for_execution") is not True
            or release["plan"]["path"] != plan_path):
        raise ValueError("exact approved paired release and fixed plan role required")
    code_commit = hex_value(release["code_freeze_commit"], 40)
    reviewed_commit = hex_value(release["review"]["reviewed_packet_commit"], 40)
    for commit in (code_commit, reviewed_commit):
        git(root, "merge-base", "--is-ancestor", commit, freeze_commit)
    verify_inventory(root, code_commit, release["source_files"], required_paths=required_source_paths)
    required = set(required_source_paths) | {plan_path}
    # The scientific role set is fixed; review fixes can change bytes but cannot
    # silently add another design file or drop a required code/test role.
    before, after = release["reviewed_inventory"], release["final_inventory"]
    verify_inventory(root, reviewed_commit, before, required_paths=required, current=False)
    verify_inventory(root, freeze_commit, after, required_paths=required)
    if {p: after[p] for p in required_source_paths} != release["source_files"]:
        raise ValueError("final source differs from qualified code inventory")
    review = release["review"]
    artifacts = review["artifacts"]
    for row in (artifacts["brief"], *artifacts["contexts"], *artifacts["bundle"].values(), release["adjudication"], release["plan"]):
        if committed_file(root, freeze_commit, row["path"]) != read_bound(root, row):
            raise ValueError("review/release role differs from pushed bytes")
    old_plan = json.loads(committed_file(root, reviewed_commit, plan_path))
    expected_context = decision_context(old_plan, digest(canonical(before)))
    if read_bound(root, artifacts["contexts"][0]).decode() != expected_context:
        raise ValueError("review packet does not contain the exact committed design/inventory")
    for row in (artifacts["brief"], *artifacts["contexts"]):
        if committed_file(root, reviewed_commit, row["path"]) != read_bound(root, row):
            raise ValueError("reviewed brief/context changed after submitted packet commit")
    completed = validate_review_bundle(root, review)
    adjudication = json.loads(read_bound(root, release["adjudication"]))
    outcome = adjudicate(read_bound(root, artifacts["bundle"]["review"]).decode(), adjudication, before, after)
    # Git-free workers will later consume an independently issued authorization;
    # this gate is only a source/review prerequisite, never that authorization.
    return dict(status="source-and-review-verified", source=source, review=completed, adjudication=outcome,
        release_sha256=digest(raw), plan_sha256=release["plan"]["sha256"],
        target_execution_authorized=False, runtime_and_one_shot_gate_still_required=True)

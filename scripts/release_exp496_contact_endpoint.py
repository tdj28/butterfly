#!/usr/bin/env python3
"""Allowlisted complete raw-data release and safe zero-IVP public replay."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile

from butterfly._paired_startup import sha256, write_json
from scripts import audit_exp496_contact_endpoint as audit
from scripts.check_public_repository import check_file

CHUNK = 512*1024**2
INDEX = "EXP-496-full-data-index.json"


def safe_leaf(name):
    if (not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) is None
            or Path(name).name != name):
        raise ValueError("flat regular release member required")
    return name


def build(directory, anchor, output):
    result = audit.audit(directory, anchor)
    summary = json.loads((directory/"summary.json").read_bytes())
    entries = []
    for name in sorted([*summary["files"], "summary.json"]):
        safe_leaf(name)
        path = directory/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 64*1024**2:
            raise ValueError("unsafe/oversized release member")
        data = path.read_bytes()
        if check_file(name, data) or (name.endswith(".json") and re.search(rb"/(?:Users|home)/", data)):
            raise ValueError("public credential/private-path scan rejected member")
        entries.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    groups, group, size = [], [], 0
    for e in entries:
        if group and size+e["bytes"] > CHUNK:
            groups.append(group)
            group, size = [], 0
        group.append(e)
        size += e["bytes"]
    if group:
        groups.append(group)
    output.mkdir(parents=True, exist_ok=False)
    shards = []
    for i, members in enumerate(groups):
        name = f"EXP-496-full-data-{i:02d}.tar"
        with tarfile.open(output/name, "x", format=tarfile.USTAR_FORMAT) as archive:
            for row in members:
                info = tarfile.TarInfo(row["path"])
                info.size, info.mode, info.mtime = row["bytes"], 0o644, 0
                with (directory/row["path"]).open("rb") as stream:
                    archive.addfile(info, stream)
        shards.append(dict(path=name, bytes=(output/name).stat().st_size,
                           sha256=sha256(output/name), members=members))
    index = dict(schema="butterfly.exp496-full-data.v1", experiment_id="EXP-496",
        execution_source=result["source_commit"], summary_sha256=anchor, license="GPL-2.0-only",
        shards=shards, total_members=len(entries), total_bytes=sum(e["bytes"] for e in entries),
        builder_sha256=sha256(Path(__file__)), auditor_sha256=sha256(Path(audit.__file__)),
        scope="Every EXP-496 returned target mesh, profile, control, start record and summary. Public parent inputs are pinned in the source manifest.")
    write_json(output/INDEX, index)
    write_json(output/"EXP-496-contact-endpoint-result.json", result)
    return index


def unpack(index_path, anchor, output):
    if sha256(index_path) != anchor:
        raise ValueError("index anchor differs")
    index = json.loads(index_path.read_bytes())
    if (index["schema"] != "butterfly.exp496-full-data.v1" or index["experiment_id"] != "EXP-496"
            or not 1 <= len(index["shards"]) <= 5 or not 1 <= index["total_members"] <= 250
            or not 0 < index["total_bytes"] <= 2*1024**3):
        raise ValueError("release scope/count/size differs")
    names, total = set(), 0
    for s in index["shards"]:
        path = index_path.parent/safe_leaf(s["path"])
        if (path.is_symlink() or path.stat().st_size != s["bytes"] or not 0 < s["bytes"] <= CHUNK+1024**2
                or sha256(path) != s["sha256"]):
            raise ValueError("shard bytes differ")
        for row in s["members"]:
            name = safe_leaf(row["path"])
            if name in names or not 0 <= row["bytes"] <= 64*1024**2:
                raise ValueError("duplicate/oversized member")
            names.add(name)
            total += row["bytes"]
    if len(names) != index["total_members"] or total != index["total_bytes"]:
        raise ValueError("complete release denominator differs")
    output.mkdir(parents=True, exist_ok=False)
    raw_root = output/"raw"
    raw_root.mkdir()
    for shard in index["shards"]:
        with tarfile.open(index_path.parent/shard["path"], "r:") as archive:
            members = archive.getmembers()
            if [m.name for m in members] != [r["path"] for r in shard["members"]]:
                raise ValueError("archive member set/order differs")
            for m, r in zip(members, shard["members"], strict=True):
                if not m.isfile() or m.issparse() or m.size != r["bytes"]:
                    raise ValueError("only bound regular members allowed")
                digest = hashlib.sha256()
                with archive.extractfile(m) as stream, (raw_root/r["path"]).open("xb") as sink:
                    for chunk in iter(lambda: stream.read(1024**2), b""):
                        digest.update(chunk)
                        sink.write(chunk)
                if digest.hexdigest() != r["sha256"]:
                    raise ValueError("extracted bytes differ; failed partial root retained")
    result = audit.audit(raw_root, index["summary_sha256"], public=True)
    write_json(output/"public-replay.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--extract-and-replay", action="store_true")
    parser.add_argument("--run", type=Path)
    parser.add_argument("--summary-sha256")
    parser.add_argument("--index", type=Path)
    parser.add_argument("--index-sha256")
    parser.add_argument("--output-dir", type=Path, required=True)
    a = parser.parse_args()
    result = build(a.run, a.summary_sha256, a.output_dir) if a.build else unpack(a.index, a.index_sha256, a.output_dir)
    print(json.dumps({k: v for k, v in result.items() if k not in ("shards", "candidates", "ledger", "contact")}))


if __name__ == "__main__":
    main()

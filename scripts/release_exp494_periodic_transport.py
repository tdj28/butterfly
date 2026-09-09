#!/usr/bin/env python3
"""Allowlisted full-data sharding and safe, zero-integration public replay."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import tarfile
from unittest.mock import patch

from scripts import audit_exp494_periodic_winding_transport as audit
from scripts import audit_exp494_cached as cached
from scripts import run_exp494_periodic_winding_transport as run
from scripts.check_public_repository import check_file
from scripts.research_bundle import safe_name

CHUNK = 512*1024**2
DATA = "EXP-494-periodic-transport-data.json.gz"
INDEX = "EXP-494-full-data-index.json"
RECEIPT = "EXP-494-periodic-transport-result.json"


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()


def partition(entries, limit=CHUNK):
    chunks, current, size = [], [], 0
    for row in entries:
        if row["bytes"] > limit or row["bytes"] < 0:
            raise ValueError("member outside shard bound")
        if current and size+row["bytes"] > limit:
            chunks.append(current)
            current, size = [], 0
        current.append(row)
        size += row["bytes"]
    if current:
        chunks.append(current)
    return chunks


def build(directory, summary_sha, output):
    result = cached.audit(directory,summary_sha)
    summary = json.loads((directory/"summary.json").read_bytes())
    parent = run.parent_inputs(run.load_plan())
    files = {"artifacts/EXP-494/target-4e50549/"+name:directory/name for name in [*summary["files"],"summary.json"]}
    marker_path = run.ROOT/"artifacts/EXP-494/target-once.json"
    if json.loads(marker_path.read_bytes())["source_commit"] != summary["source_commit"]:
        raise ValueError("attempt marker source differs")
    files["artifacts/EXP-494/target-once.json"] = marker_path
    files.update({"artifacts/EXP-480/run-5b584f4/"+name:run.PARENT/name for name in [*[r["path"] for r in parent["files"]],"receipt.json","started.json"]})
    entries = []
    for name,path in sorted(files.items()):
        safe_name(name)
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 64*1024**2:
            raise ValueError("unsafe/oversized release member")
        data = path.read_bytes()
        if check_file(name,data) or (path.suffix == ".json" and re.search(rb"/(?:Users|home)/",data)):
            raise ValueError("public credential/private-path scan rejected member")
        entries.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    output.mkdir(parents=True,exist_ok=False)
    with (output/DATA).open("xb") as stream:
        stream.write(gzip.compress((directory/"summary.json").read_bytes(),mtime=0))
    shards = []
    for i,chunk in enumerate(partition(entries)):
        name = f"EXP-494-full-data-{i:02d}.tar"
        with tarfile.open(output/name,"x",format=tarfile.USTAR_FORMAT) as archive:
            for row in chunk:
                info = tarfile.TarInfo(row["path"])
                info.size,info.mode,info.mtime = row["bytes"],0o644,0
                with files[row["path"]].open("rb") as stream:
                    archive.addfile(info,stream)
        shards.append(dict(path=name,bytes=(output/name).stat().st_size,sha256=run.sha256(output/name),members=chunk))
    index = dict(schema="butterfly.exp494-full-data.v1",license="GPL-2.0-only",experiment_id="EXP-494",
        execution_source=summary["source_commit"],summary_sha256=summary_sha,shards=shards,
        total_members=len(entries),total_bytes=sum(e["bytes"] for e in entries),
        scope="Complete EXP-494 trial/observation evidence plus all required EXP-480 saved-cycle raw inputs; not the earlier discovery campaign.",
        builder_sha256=run.sha256(Path(__file__)),auditor_sha256=run.sha256(Path(audit.__file__)),
        io_adapter_sha256=run.sha256(Path(cached.__file__)))
    run.write_json(output/INDEX,index)
    run.write_json(output/RECEIPT,dict(result,compressed_summary=dict(path=DATA,bytes=(output/DATA).stat().st_size,sha256=run.sha256(output/DATA)),
                                    full_data_index=dict(path=INDEX,sha256=run.sha256(output/INDEX))))
    return index


def unpack(index_path, index_sha, output):
    if run.sha256(index_path) != index_sha:
        raise ValueError("release index hash differs")
    index = json.loads(index_path.read_bytes())
    if (index.get("schema") != "butterfly.exp494-full-data.v1" or index.get("experiment_id") != "EXP-494"
            or not 0 < len(index["shards"]) <= 20 or not 0 < index["total_members"] <= 20000
            or not 0 < index["total_bytes"] <= 9*1024**3):
        raise ValueError("release index identity/size limits differ")
    expected, total = set(), 0
    for shard in index["shards"]:
        if Path(shard["path"]).name != shard["path"] or not 0 < shard["bytes"] <= CHUNK+64*1024**2:
            raise ValueError("invalid shard path/size")
        path = index_path.parent/shard["path"]
        if path.is_symlink() or path.stat().st_size != shard["bytes"] or run.sha256(path) != shard["sha256"]:
            raise ValueError("shard bytes differ")
        for row in shard["members"]:
            name = safe_name(row["path"])
            if (not (name == "artifacts/EXP-494/target-once.json" or name.startswith(("artifacts/EXP-494/target-4e50549/","artifacts/EXP-480/run-5b584f4/")))
                    or name in expected or not 0 <= row["bytes"] <= 64*1024**2):
                raise ValueError("unsafe duplicate/out-of-scope member")
            expected.add(name)
            total += row["bytes"]
    if len(expected) != index["total_members"] or total != index["total_bytes"]:
        raise ValueError("release denominator differs")
    output.mkdir(parents=True,exist_ok=False)
    # A fresh root and exclusive files prevent overwriting a checkout or old run.
    for shard in index["shards"]:
        with tarfile.open(index_path.parent/shard["path"],"r:") as archive:
            members = archive.getmembers()
            if [m.name for m in members] != [r["path"] for r in shard["members"]]:
                raise ValueError("archive member set/order differs")
            for member,row in zip(members,shard["members"],strict=True):
                if not member.isfile() or member.issparse() or member.size != row["bytes"]:
                    raise ValueError("only bound regular members allowed")
                target = output/row["path"]
                target.parent.mkdir(parents=True,exist_ok=True)
                for part in target.parents:
                    if part == output.parent:
                        break
                    if part.is_symlink():
                        raise ValueError("symlink in extraction root")
                stream = archive.extractfile(member)
                digest = hashlib.sha256()
                with target.open("xb") as sink:
                    for chunk in iter(lambda:stream.read(1024**2),b""):
                        digest.update(chunk)
                        sink.write(chunk)
                if digest.hexdigest() != row["sha256"]:
                    raise ValueError("extracted member hash differs; partial root retained")
    with patch.object(run,"PARENT",output/"artifacts/EXP-480/run-5b584f4"):
        result = cached.audit(output/"artifacts/EXP-494/target-4e50549",index["summary_sha256"])
    run.write_json(output/"public-replay.json",result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build",action="store_true")
    mode.add_argument("--extract-and-replay",action="store_true")
    parser.add_argument("--run",type=Path)
    parser.add_argument("--summary-sha256")
    parser.add_argument("--index",type=Path)
    parser.add_argument("--index-sha256")
    parser.add_argument("--output-dir",type=Path,required=True)
    args = parser.parse_args()
    result = build(args.run,args.summary_sha256,args.output_dir) if args.build else unpack(args.index,args.index_sha256,args.output_dir)
    print(json.dumps({k:v for k,v in result.items() if k != "shards"}))


if __name__ == "__main__":
    main()

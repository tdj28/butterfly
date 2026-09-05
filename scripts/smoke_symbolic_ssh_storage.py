#!/usr/bin/env python3
"""Source-bound, target-free prax storage and Linux writer-quiescence smoke.

Default is local source preflight only. --execute creates one fresh authorized
prax directory, retains a 16 MiB synthetic roundtrip, and runs tiny owned Linux
parent/grandchild controls. It never creates a Runpod worker or runs trajectories.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import shlex
import subprocess

from scripts import symbolic_ssh_storage as storage
from scripts.check_public_repository import check_file


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = ("scripts/smoke_symbolic_ssh_storage.py", "scripts/symbolic_ssh_storage.py",
                "scripts/execute_symbolic_center_cloud.py")


def frozen_source(commit, *, root=ROOT):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise storage.StorageError("a full lowercase frozen source commit is required")
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL, timeout=30)
    if git("rev-parse", "HEAD").decode().strip() != commit or git("status", "--porcelain", "--untracked-files=all").strip():
        raise storage.StorageError("smoke requires the declared clean source commit")
    refs = git("for-each-ref", "--format=%(objectname) %(refname)", "refs/remotes/origin").decode().splitlines()
    matches = [line.split(" ", 1)[1] for line in refs if line.startswith(commit + " ")]
    if not matches:
        raise storage.StorageError("smoke source lacks an exact origin remote-tracking ref")
    hashes = {}
    for name in SOURCE_FILES:
        path = Path(root) / name
        content = path.read_bytes()
        if path.is_symlink() or git("show", f"{commit}:{name}") != content:
            raise storage.StorageError("smoke source file differs from committed bytes")
        if check_file(name, content):
            raise storage.StorageError("smoke source failed credential scan; contents suppressed")
        hashes[name] = hashlib.sha256(content).hexdigest()
    return {"commit": commit, "source_files": hashes, "exact_origin_refs": matches,
            "remote_check": "local remote-tracking refs only; no Git network call"}


def worker_literal(content):
    module = ast.parse(content)
    values = [node.value for node in module.body if isinstance(node, ast.Assign)
              and any(isinstance(target, ast.Name) and target.id == "REMOTE_PROGRAM" for target in node.targets)]
    if len(values) != 1:
        raise storage.StorageError("wrapper must contain one frozen worker bootstrap literal")
    value = ast.literal_eval(values[0])
    if not isinstance(value, str):
        raise storage.StorageError("worker bootstrap is not a string literal")
    return value


QUIESCENCE_BOOTSTRAP = r'''
import ast,base64,hashlib,json,pathlib,re,sys
p=json.loads(sys.stdin.buffer.read(4194305)); root=pathlib.Path(p['remote_directory'])
base=pathlib.Path('/home/ubuntu/butterfly-research')
if root.parent!=base or str(root)!=p['remote_directory'] or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',root.name): raise RuntimeError('invalid task directory')
if any(x.is_symlink() for x in (root,*root.parents)): raise RuntimeError('symlink in task directory')
if not re.fullmatch(r'[0-9a-f]{40}',p['source_commit']): raise RuntimeError('invalid source commit')
helper=root/'_storage_helper.py'; helper_bytes=helper.read_bytes(); expected=root/'expected.json'
if helper.is_symlink() or expected.is_symlink() or hashlib.sha256(helper_bytes).hexdigest()!=p['helper_sha256'] or hashlib.sha256(expected.read_bytes()).hexdigest()!=p['expected_binding_sha256']: raise RuntimeError('frozen storage helper/binding changed')
wrapper=base64.b64decode(p['wrapper_base64'],validate=True)
if len(wrapper)>1048576 or hashlib.sha256(wrapper).hexdigest()!=p['wrapper_sha256']: raise RuntimeError('frozen wrapper hash mismatch')
tree=ast.parse(wrapper); values=[n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REMOTE_PROGRAM' for t in n.targets)]
if len(values)!=1: raise RuntimeError('ambiguous worker bootstrap')
program=ast.literal_eval(values[0])
if not isinstance(program,str): raise RuntimeError('worker bootstrap is not a literal string')
namespace={'__name__':'frozen_symbolic_storage','__file__':str(helper)}
exec(compile(helper_bytes,str(helper),'exec'),namespace)
namespace['write_new'](root/'frozen-worker-wrapper.py',wrapper)
result=namespace['quiescence_smoke'](root/'quiescence',program)
result.update(source_commit=p['source_commit'],wrapper_sha256=p['wrapper_sha256'],helper_sha256=p['helper_sha256'])
namespace['write_new'](root/'quiescence-source-receipt.json',namespace['encoded'](result))
sys.stdout.buffer.write(namespace['encoded'](result))
'''


def run_quiescence(store, wrapper, source, output_directory):
    worker_literal(wrapper)  # Reject non-literals before staging any extra bytes.
    expected = source["source_files"]["scripts/execute_symbolic_center_cloud.py"]
    if hashlib.sha256(wrapper).hexdigest() != expected:
        raise storage.StorageError("wrapper changed after source preflight")
    payload = {**store.binding, "source_commit": source["commit"], "wrapper_sha256": expected,
               "wrapper_base64": base64.b64encode(wrapper).decode()}
    argv = ["/usr/bin/ssh", *storage.ssh_options(), storage.HOST,
            shlex.join(["python3", "-B", "-c", QUIESCENCE_BOOTSTRAP])]
    output = io.BytesIO()
    with (Path(output_directory) / "quiescence-ssh.log").open("xb") as log:
        storage.bounded_output(argv, output, maximum_bytes=storage.MAXIMUM_CONTROL_BYTES,
                               seconds=120, log=log, input_bytes=storage.encoded(payload))
    result = json.loads(output.getvalue())
    if (result.get("schema") != "butterfly.symbolic-quiescence-smoke.v1" or result.get("passed") is not True
            or result.get("source_commit") != source["commit"] or result.get("wrapper_sha256") != expected
            or result.get("helper_sha256") != store.binding["helper_sha256"]):
        raise storage.StorageError("remote quiescence receipt did not pass its frozen source binding")
    return result


def execute_smoke(commit, remote_directory, output_directory, *, root=ROOT):
    output = Path(output_directory)
    storage.validate_directory(remote_directory)
    if output.exists() or output.is_symlink():
        raise storage.StorageError("local smoke output must be new")
    source = frozen_source(commit, root=root)
    wrapper = (Path(root) / SOURCE_FILES[2]).read_bytes()
    worker_literal(wrapper)
    result = {"schema": "butterfly.symbolic-ssh-qualification-smoke.v1", "source": source,
              "source_commit": commit, "remote_directory": remote_directory, "passed": False,
              "runpod_calls_performed": False, "target_computation_performed": False}
    try:
        transport = storage.storage_smoke(remote_directory, output,
                            helper_sha256=source["source_files"]["scripts/symbolic_ssh_storage.py"])
        result["storage"] = transport
        store = storage.SshEvidenceStore.open_existing(transport["remote_storage_binding"], local_control_directory=output)
        result["quiescence"] = run_quiescence(store, wrapper, source, output)
        if frozen_source(commit, root=root) != source:
            raise storage.StorageError("smoke source changed during qualification")
        result["passed"] = True
    except BaseException as error:
        result["failure"] = {"type": type(error).__name__, "message": str(error)}
    finally:
        if output.is_dir():
            storage.write_new(output / "qualification-smoke.json", storage.encoded(result))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--remote-dir", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="explicitly run the target-free SSH smoke")
    args = parser.parse_args(argv)
    storage.validate_directory(args.remote_dir)
    if not args.execute:
        source = frozen_source(args.source_commit)
        print(json.dumps({"preflight_passed": True, "source": source, "ssh_calls_performed": False,
                          "runpod_calls_performed": False}))
        return 0
    result = execute_smoke(args.source_commit, args.remote_dir, args.output_dir)
    print(json.dumps({"passed": result["passed"], "receipt": str(args.output_dir / "qualification-smoke.json"),
                      "runpod_calls_performed": False, "target_computation_performed": False}))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

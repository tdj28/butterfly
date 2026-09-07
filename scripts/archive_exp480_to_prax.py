#!/usr/bin/env python3
"""Back up the exact audited EXP-480 tar, without extracting it on prax.

Default is read-only local preflight. --execute makes one fresh upload; it
never overwrites a prior attempt or removes local/remote data.
"""
import argparse
import json
from pathlib import Path
import subprocess

from scripts import run_symbolic_center_pilot as evidence
from scripts.archive_exp479_cpu import remote_command
from scripts.symbolic_ssh_storage import reject_symlink_chain, ssh_options

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts/EXP-480/audit-and-archive"
REMOTE = "/home/ubuntu/butterfly-research/exp480-complete-20260907-5b584f4"
ARCHIVE_SHA = "d2070e1d676b30f5dcbf5ecddf8814d3cee76fb8c12a2284084bb34e5f2d9cd5"
ARCHIVE_BYTES = 12349440


def preflight():
    path = OUTPUT / "evidence.tar"
    reject_symlink_chain(path)
    if (not path.is_file() or path.stat().st_size != ARCHIVE_BYTES
            or evidence.sha256_file(path) != ARCHIVE_SHA or path.stat().st_mode & 0o777 != 0o600):
        raise ValueError("exact owner-only EXP-480 archive required")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    archive = preflight()
    if not args.execute:
        print(json.dumps({"prepared": True, "bytes": ARCHIVE_BYTES, "sha256": ARCHIVE_SHA, "remote": REMOTE}))
        return 0
    evidence.write_new_json(OUTPUT / "upload-started.json", {"remote": REMOTE, "sha256": ARCHIVE_SHA,
        "started_utc": evidence.utc_now(), "automatic_retry": False})
    result = {"passed": False, "remote": REMOTE, "local_originals_retained": True}
    try:
        create = ("import pathlib,shutil,sys\np=pathlib.Path(sys.argv[1])\n"
                  "if any(q.is_symlink() for q in [p,*p.parents]): raise ValueError('symlink')\n"
                  "if shutil.disk_usage(p.parent).free<550000000: raise ValueError('space')\n"
                  "p.mkdir(mode=0o700)")
        subprocess.run(remote_command(create, REMOTE), check=True, timeout=30, capture_output=True)
        subprocess.run(["scp", *ssh_options(), str(archive), "ubuntu@prax:"+REMOTE+"/evidence.tar"],
                       check=True, timeout=180, capture_output=True)
        verify = ("import pathlib,hashlib,json,sys\np=pathlib.Path(sys.argv[1])\n"
                  "with p.open('rb') as f: h=hashlib.file_digest(f,'sha256').hexdigest()\n"
                  "print(json.dumps({'bytes':p.stat().st_size,'sha256':h,'file_mode':p.stat().st_mode&511,'directory_mode':p.parent.stat().st_mode&511}))")
        response = subprocess.run(remote_command(verify, REMOTE+"/evidence.tar"),
                                  check=True, timeout=30, capture_output=True, text=True)
        observed = json.loads(response.stdout)
        if observed != {"bytes": ARCHIVE_BYTES, "sha256": ARCHIVE_SHA, "file_mode": 0o600, "directory_mode": 0o700}:
            raise ValueError("remote archive differs")
        preflight()
        result.update(passed=True, remote_archive_verified=True, archive=observed)
    except Exception as error:
        result["failure"] = {"type": type(error).__name__, "message": "Preserve partial remote/local evidence; no automatic retry."}
    result["finished_utc"] = evidence.utc_now()
    evidence.write_new_json(OUTPUT / "upload.json", result)
    print(json.dumps(result))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Start one frozen local CPU scout in launchd; never contact a GPU provider.

The source directory should be a detached frozen worktree. State and logs stay
in a fresh ignored directory. KeepAlive is false: failures are never restarted.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-directory", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--state-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--qualification-sha256", required=True)
    args = parser.parse_args()
    source, state = args.source_directory.resolve(), args.state_directory.resolve()
    base = [str(Path(sys.executable).absolute()), "-m", "scripts.run_symbolic_center_cpu",
            "--source-commit", args.source_commit, "--output-dir", str(args.output_directory.resolve()),
            "--qualification", str(args.qualification.resolve()),
            "--qualification-sha256", args.qualification_sha256]
    environment = {"PATH": os.defpath, "PYTHONPATH": ".:python"}
    subprocess.run(base + ["--mode", "preflight"], cwd=source, env=environment, check=True)
    state.mkdir(parents=True, exist_ok=False, mode=0o700)
    label = "io.butterfly.exp479." + uuid.uuid4().hex
    service = f"gui/{os.getuid()}/{label}"
    plist = state / "job.plist"
    with plist.open("xb") as stream:
        plistlib.dump({"Label": label, "ProgramArguments": ["/usr/bin/caffeinate", "-i", *base, "--mode", "collect"],
            "WorkingDirectory": str(source), "EnvironmentVariables": environment,
            "RunAtLoad": True, "KeepAlive": False,
            "StandardOutPath": str(state / "stdout.log"), "StandardErrorPath": str(state / "stderr.log")}, stream)
    receipt = {"service": service, "plist": str(plist), "source_commit": args.source_commit,
               "source_directory": str(source), "output_directory": str(args.output_directory.resolve()),
               "automatic_restart": False, "provider_calls": False}
    (state / "launch.json").write_text(json.dumps(receipt, indent=2) + "\n")
    subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist)], check=True)
    subprocess.run(["launchctl", "print", service], check=True, stdout=subprocess.DEVNULL)
    print(json.dumps({"launched": True, "service": service}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build a fresh result-free, exact-file paired runtime bundle (stdlib only).

This development producer is not a reviewed execution authorization. It hashes
the installed NumPy/SciPy trees without copying inputs, credentials or outcomes.
The final controller must bind the emitted contract and actual pushed source.
"""
import argparse
from pathlib import Path
import runpy
import shutil
import sys
import sysconfig


ROOT = Path(__file__).resolve().parents[1]
MODULES = ("_process_guard", "models", "integrate", "poincare", "saddle", "paired_sections",
    "paired_journal", "paired_sampling", "seed_return_map", "paired_replay", "paired_decisions",
    "paired_campaign", "paired_adaptive", "paired_adaptive_journal", "paired_supervisor")
SOURCE_MAP = {"worker.py": "scripts/paired_worker.py", "startup.py": "python/butterfly/_paired_startup.py",
    "python/butterfly/__init__.py": "runtime/paired/butterfly/__init__.py",
    **{f"python/butterfly/{name}.py": f"python/butterfly/{name}.py" for name in MODULES}}


def build(output, *, root=ROOT, site_packages=None, startup_guard_seconds=120.):
    root, output = Path(root).resolve(strict=True), Path(output).absolute()
    api = runpy.run_path(str(root/"python/butterfly/_paired_startup.py"))
    site = Path(site_packages or sysconfig.get_path("purelib")).resolve(strict=True)
    if not (site/"numpy").is_dir() or not (site/"scipy").is_dir():
        raise ValueError("installed NumPy and SciPy package roots required")
    if type(startup_guard_seconds) not in (int, float) or not 0 < startup_guard_seconds <= 300:
        raise ValueError("bounded startup-only guard deadline required")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    source_map = {}
    for destination, source in SOURCE_MAP.items():
        path = api["safe_file"](root, source)
        target = output/destination
        target.parent.mkdir(parents=True, exist_ok=True)
        with path.open("rb") as reader, target.open("xb") as writer:
            shutil.copyfileobj(reader, writer)
        source_map[destination] = {"repository_path": source, "sha256": api["sha256"](path)}
    dependencies = []
    # Wheel-native BLAS libraries are frequently siblings of their package on
    # Linux; on macOS they may be inside it. Bind either exact layout observed.
    for name in ("numpy", "scipy", "numpy.libs", "scipy.libs"):
        path = site/name
        if path.exists():
            dependencies.append({"path": str(path), "files": api["inventory"](path)})
    executable = Path(sys.executable).resolve(strict=True)
    contract = {"schema": api["SCHEMA"], "target_execution_authorized": False,
        "source_map": source_map, "source_files": api["inventory"](output),
        "builder_sha256": api["sha256"](Path(__file__)),
        "environment": api["canonical_environment"](), "site_packages": str(site),
        "stdlib": str(Path(sysconfig.get_path("stdlib")).resolve(strict=True)),
        "interpreter": {"path": str(executable), "sha256": api["sha256"](executable), "version": sys.version},
        "dependency_roots": dependencies, "startup_guard_seconds": startup_guard_seconds,
        "scope": "host-specific sealed source/scientific-package inventory; not review, remote proof or OS confinement"}
    api["write_json"](output/"runtime-contract.json", contract)
    return {"path": str(output/"runtime-contract.json"), "sha256": api["sha256"](output/"runtime-contract.json"),
        "source_files": len(source_map), "dependency_files": sum(len(r["files"]) for r in dependencies),
        "target_execution_authorized": False}


def main():
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), indent=2))


if __name__ == "__main__":
    main()

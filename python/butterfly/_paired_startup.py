"""Stdlib-only sealed runtime checks, loaded by exact path before numerics.

This checks a caller-bound local inventory, not a signature or review approval.
It is not OS confinement: native loader/system libraries remain host trust.
"""
from __future__ import annotations

import hashlib
import importlib.abc
import importlib.machinery
import json
import os
from pathlib import Path
import re
import stat
import sys
import sysconfig


SCHEMA = "butterfly.paired-runtime.v1"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024**2), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_environment():
    """One declared CPU environment; no inherited credentials or Python paths."""
    env = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "LC_CTYPE": "C",
        "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"}
    if sys.platform == "darwin":
        env["__CF_USER_TEXT_ENCODING"] = f"0x{os.getuid():X}:0:0"
    return env


def safe_file(root, relative):
    root = Path(root)
    rel = Path(relative)
    if not rel.parts or rel.is_absolute() or any(p in (".", "..") for p in rel.parts) or str(rel) != relative:
        raise ValueError("noncanonical inventory path")
    path = root
    for part in rel.parts:
        path = path/part
        if path.is_symlink():
            raise ValueError("symlink in bound file path")
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("bound file is not regular")
    return path


def inventory(root, *, omit=()):
    """All files in a small sealed tree, rejecting links and special files."""
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("regular inventory directory required")
    result = {}
    for base, directories, files in os.walk(root, followlinks=False):
        for name in directories:
            if (Path(base)/name).is_symlink():
                raise ValueError("symlink directory in sealed tree")
        for name in files:
            relative = (Path(base)/name).relative_to(root).as_posix()
            if relative in omit:
                continue
            path = safe_file(root, relative)
            result[relative] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return dict(sorted(result.items()))


def write_json(path, value):
    """Exclusive durable startup evidence, with no automatic overwrite."""
    path = Path(path)
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def load_contract(bundle, expected_sha256):
    root = Path(bundle).resolve(strict=True)
    path = safe_file(root, "runtime-contract.json")
    if (not isinstance(expected_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
            or path.stat().st_size > 16*1024**2 or sha256(path) != expected_sha256):
        raise ValueError("runtime contract differs from external digest")
    contract = json.loads(path.read_bytes())
    if contract["schema"] != SCHEMA or contract["target_execution_authorized"] is not False:
        raise ValueError("startup contract is not a target authorization")
    return contract


def validate_environment(contract):
    expected = contract["environment"]
    if expected != canonical_environment() or dict(os.environ) != expected:
        raise ValueError("worker environment differs from canonical contract")
    if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode and sys.flags.utf8_mode):
        raise ValueError("worker requires -I -S -B -X utf8=1")


def verify_runtime(bundle, contract):
    root = Path(bundle).resolve(strict=True)
    if inventory(root, omit=("runtime-contract.json",)) != contract["source_files"]:
        raise ValueError("sealed runtime contains missing, extra or changed files")
    if (set(contract["source_map"]) != set(contract["source_files"])
            or any(row["sha256"] != contract["source_files"][name]["sha256"]
                   for name, row in contract["source_map"].items())):
        raise ValueError("copied files differ from declared repository source hashes")
    executable = Path(sys.executable).resolve(strict=True)
    if (str(executable) != contract["interpreter"]["path"]
            or sha256(executable) != contract["interpreter"]["sha256"]
            or sys.version != contract["interpreter"]["version"]):
        raise ValueError("interpreter differs from bound host runtime")
    if str(Path(sysconfig.get_path("stdlib")).resolve(strict=True)) != contract["stdlib"]:
        raise ValueError("standard-library root differs from actual interpreter")
    site = Path(contract["site_packages"])
    if site.resolve(strict=True) != site or not site.is_dir():
        raise ValueError("noncanonical scientific-package parent")
    names = [Path(row["path"]).name for row in contract["dependency_roots"]]
    if (len(set(names)) != len(names) or not {"numpy", "scipy"} <= set(names)
            or not set(names) <= {"numpy", "scipy", "numpy.libs", "scipy.libs"}
            or any(Path(row["path"]).parent != site for row in contract["dependency_roots"])):
        raise ValueError("unexpected scientific dependency roots")
    for row in contract["dependency_roots"]:
        directory = Path(row["path"])
        if directory.resolve(strict=True) != directory or inventory(directory) != row["files"]:
            raise ValueError("scientific dependency tree differs from bound runtime")
    return root


class BoundImports(importlib.abc.MetaPathFinder):
    """Check each file-backed Python module before its normal loader executes.

    Builtin/frozen modules and the host standard library are runtime trust.
    Native extensions' transitive system-library loads are not Python imports.
    This hook is an integrity tripwire for trusted code, not a security sandbox.
    """
    def __init__(self, root, contract):
        self.root, self.contract = Path(root), contract
        self.loaded = {}
        self.stdlib = Path(contract["stdlib"])
        self.allowed = {str(self.root/name): row for name, row in contract["source_files"].items()}
        for dependency in contract["dependency_roots"]:
            self.allowed.update({str(Path(dependency["path"])/name): row for name, row in dependency["files"].items()})

    def check(self, name, origin):
        if origin in (None, "built-in", "frozen"):
            return
        path = Path(origin)
        resolved = path.resolve(strict=True)
        record = self.allowed.get(str(path))
        if record is not None:
            if path != resolved or path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
                raise ImportError("bound module bytes changed")
            kind = "bound-file"
        elif resolved.is_relative_to(self.stdlib) and not any(p in ("site-packages", "dist-packages") for p in resolved.parts):
            kind = "host-stdlib"
        else:
            raise ImportError("module origin lies outside sealed import closure")
        self.loaded[name] = {"path": str(resolved), "sha256": sha256(resolved), "kind": kind}

    def find_spec(self, fullname, path=None, target=None):
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec is not None:
            if spec.origin is None:
                self.check_namespace(fullname, spec.submodule_search_locations)
            else:
                self.check(fullname, spec.origin)
        return spec

    def check_namespace(self, name, locations):
        # SciPy's vendored _external tree contains a namespace package. Permit
        # only a single exact real directory backed by inventoried descendants,
        # never a search location added by another checkout/package tree.
        paths = list(locations or ())
        if len(paths) != 1:
            raise ImportError("namespace package has unbound search locations")
        path = Path(paths[0])
        expected = {base/Path(*name.split(".")) for base in (self.root/"python", Path(self.contract["site_packages"]))}
        if (path not in expected or path.resolve(strict=True) != path
                or not any(p.startswith(str(path)+os.sep) for p in self.allowed)):
            raise ImportError("namespace package outside fixed package inventory")
        self.loaded[name] = {"path": str(path), "sha256": None, "kind": "bound-namespace"}

    def check_loaded(self):
        for name, module in list(sys.modules.items()):
            spec = getattr(module, "__spec__", None)
            origin = getattr(spec, "origin", None) or getattr(module, "__file__", None)
            if origin is None and getattr(spec, "submodule_search_locations", None) is not None:
                self.check_namespace(name, spec.submodule_search_locations)
                continue
            # The executable script itself was bound before this hook existed.
            self.check(name, origin)
        return dict(sorted(self.loaded.items()))


def install_import_gate(root, contract):
    if any(n.split(".")[0] in ("numpy", "scipy", "butterfly") for n in sys.modules):
        raise ValueError("scientific imports preceded guarded startup")
    finder = BoundImports(root, contract)
    # -S skips site initialization, .pth execution and editable-checkout hooks.
    # The only added search roots are the sealed package and bound dependency
    # parent. An unlisted sibling package is rejected by the finder.
    stdlib = Path(contract["stdlib"])
    sys.path[:] = [str(Path(root)/"python"), contract["site_packages"], str(stdlib), str(stdlib/"lib-dynload")]
    sys.meta_path.insert(0, finder)
    finder.check_loaded()
    return finder

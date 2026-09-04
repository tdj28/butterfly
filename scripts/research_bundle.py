"""Deterministic, allowlisted research archives with verified safe extraction.

This module uses only the standard library. Bundle data are passive: no file
inside an archive is executed, and extraction never calls tarfile.extractall.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile


SPEC_SCHEMA = "butterfly.core-bundle-spec.v1"
INDEX_SCHEMA = "butterfly.core-bundle-index.v1"
SPEC_PATH = "experiments/core-bundle.json"
SUPPORT_PATHS = ("LICENSE", "pyproject.toml", "uv.lock", SPEC_PATH)
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_INDEX_BYTES = 1024 * 1024
MAX_MEMBERS = 100


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_name(name: str) -> str:
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_./-]+", name):
        raise ValueError("invalid archive path")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name or name == ".":
        raise ValueError("unsafe archive path")
    return name


def read_regular(root: Path, name: str) -> bytes:
    """Reject symlinks at every member component before reading local inputs."""
    current = root.resolve()
    for component in PurePosixPath(safe_name(name)).parts:
        current /= component
        if current.is_symlink():
            raise ValueError(f"symlink is not allowed: {name}")
    if not current.is_file():
        raise ValueError(f"missing regular file: {name}")
    if current.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f"input exceeds size limit: {name}")
    return current.read_bytes()


def file_entry(name: str, data: bytes, role: str) -> dict:
    return {"path": safe_name(name), "bytes": len(data), "sha256": sha256(data), "role": role}


def validate_entries(entries: list) -> dict[str, dict]:
    if not isinstance(entries, list) or not entries or len(entries) > MAX_MEMBERS:
        raise ValueError("invalid file inventory")
    result = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid file entry")
        name = safe_name(entry.get("path"))
        size = entry.get("bytes")
        digest = entry.get("sha256")
        if name == "index.json" or name in result:
            raise ValueError("duplicate or reserved file entry")
        if type(size) is not int or not 0 <= size <= MAX_FILE_BYTES:
            raise ValueError("invalid file size")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid SHA-256")
        result[name] = entry
    if sum(entry["bytes"] for entry in result.values()) > MAX_TOTAL_BYTES:
        raise ValueError("bundle exceeds size limit")
    return result


def load_spec(root: Path) -> dict:
    spec = json.loads(read_regular(root, SPEC_PATH))
    if spec.get("schema") != SPEC_SCHEMA:
        raise ValueError("unsupported bundle specification")
    entries = validate_entries(spec.get("files"))
    for name in entries:
        if not re.fullmatch(r"(?:artifacts/EXP-[0-9]+/[^/]+\.json|experiments/manifests/[^/]+\.json)", name):
            raise ValueError("data inventory permits only explicit research JSON files")
    return spec


def inventory(root: Path) -> tuple[dict, dict[str, bytes]]:
    """Read exactly the frozen data inventory and four named support files."""
    spec = load_spec(root)
    expected = validate_entries(spec["files"])
    payload = {}
    entries = []
    for name, entry in sorted(expected.items()):
        data = read_regular(root, name)
        if len(data) != entry["bytes"] or sha256(data) != entry["sha256"]:
            raise ValueError(f"frozen input hash/size mismatch: {name}")
        payload[name] = data
        entries.append(file_entry(name, data, entry.get("role", "frozen research input")))
    for name in SUPPORT_PATHS:
        if name in payload:
            raise ValueError("support file must not be a frozen data entry")
        payload[name] = read_regular(root, name)
        entries.append(file_entry(name, payload[name], "source license, environment, or bundle policy"))
    # Apply the same bounded credential check used by the public-source CI.
    try:
        from scripts.check_public_repository import check_file
    except ModuleNotFoundError:
        from check_public_repository import check_file
    for name, data in payload.items():
        issues = check_file(name, data)
        if issues:
            raise ValueError(f"publication guard rejected {name}: {', '.join(issues)}")
    validate_entries(entries)
    return {"spec": spec, "files": sorted(entries, key=lambda entry: entry["path"])}, payload


def source_revision(root: Path, *, allow_dirty: bool) -> dict:
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL).decode().strip()

    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    if dirty and not allow_dirty:
        raise ValueError("export requires a clean source checkout; --allow-dirty is for local review only")
    return {"commit": commit, "dirty": dirty, "tree": git("rev-parse", "HEAD^{tree}")}


def build_archive(root: Path, output: Path, *, allow_dirty: bool = False) -> dict:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"refusing to overwrite: {output}")
    value, payload = inventory(root)
    index = {
        "schema": INDEX_SCHEMA,
        "bundle_id": value["spec"]["bundle_id"],
        "license": value["spec"]["license"],
        "scope": value["spec"]["scope"],
        "source": source_revision(root, allow_dirty=allow_dirty),
        "environment": {
            "uv_lock_sha256": sha256(payload["uv.lock"]),
            "pyproject_sha256": sha256(payload["pyproject.toml"]),
            "install_command": "uv sync --locked --extra dev",
        },
        "files": value["files"],
    }
    payload["index.json"] = canonical_json(index)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".bundle-", delete=False) as handle:
            temporary = Path(handle.name)
            with gzip.GzipFile(fileobj=handle, mode="wb", filename="", mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                    for name, data in sorted(payload.items()):
                        member = tarfile.TarInfo(name)
                        member.size = len(data)
                        member.mode = 0o644
                        member.mtime = 0
                        archive.addfile(member, io.BytesIO(data))
        # Link atomically: unlike replace(), this refuses a racing existing output.
        os.link(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {"archive": str(output), "bytes": output.stat().st_size, "sha256": file_sha256(output), "index": index}


def read_archive(archive_path: Path, *, expected_sha256: str) -> tuple[dict, dict[str, bytes]]:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("a lowercase SHA-256 from the release is required")
    with archive_path.open("rb") as handle:
        raw_archive = handle.read(MAX_TOTAL_BYTES + 1)
    if len(raw_archive) > MAX_TOTAL_BYTES:
        raise ValueError("compressed archive exceeds size limit")
    if sha256(raw_archive) != expected_sha256:
        raise ValueError("archive SHA-256 mismatch")
    payload = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(raw_archive), mode="r:gz") as archive:
        for member in archive:
            name = safe_name(member.name)
            if name in payload or len(payload) >= MAX_MEMBERS:
                raise ValueError("duplicate or excessive archive members")
            if not member.isfile() or member.issparse():
                raise ValueError("only nonsparse regular archive files are allowed")
            limit = MAX_INDEX_BYTES if name == "index.json" else MAX_FILE_BYTES
            if not 0 <= member.size <= limit:
                raise ValueError("archive member exceeds size limit")
            total += member.size
            if total > MAX_TOTAL_BYTES:
                raise ValueError("archive exceeds total size limit")
            handle = archive.extractfile(member)
            if handle is None:
                raise ValueError("archive member has no data")
            with handle:
                data = handle.read(limit + 1)
            if len(data) != member.size:
                raise ValueError("archive member length mismatch")
            payload[name] = data
    if "index.json" not in payload:
        raise ValueError("archive has no index")
    index = json.loads(payload.pop("index.json"))
    if index.get("schema") != INDEX_SCHEMA:
        raise ValueError("unsupported bundle index")
    entries = validate_entries(index.get("files"))
    if set(entries) != set(payload):
        raise ValueError("archive contents do not match exact index inventory")
    for name, entry in entries.items():
        if len(payload[name]) != entry["bytes"] or sha256(payload[name]) != entry["sha256"]:
            raise ValueError(f"archive member hash/size mismatch: {name}")
    validate_core_index(index, payload)
    return index, payload


def validate_core_index(index: dict, payload: dict[str, bytes]) -> None:
    """Bind the inventory to its frozen policy and packaged environment."""
    if not set(SUPPORT_PATHS).issubset(payload):
        raise ValueError("bundle is missing policy, license, or locked environment")
    spec = json.loads(payload[SPEC_PATH])
    if spec.get("schema") != SPEC_SCHEMA:
        raise ValueError("unsupported frozen bundle policy")
    expected = validate_entries(spec.get("files"))
    if set(payload) != set(expected) | set(SUPPORT_PATHS):
        raise ValueError("bundle differs from frozen data allowlist")
    for name, entry in expected.items():
        if len(payload[name]) != entry["bytes"] or sha256(payload[name]) != entry["sha256"]:
            raise ValueError(f"frozen policy hash/size mismatch: {name}")
    if any(index.get(key) != spec.get(key) for key in ("bundle_id", "license", "scope")):
        raise ValueError("index metadata differs from frozen policy")
    environment = index.get("environment", {})
    if environment.get("uv_lock_sha256") != sha256(payload["uv.lock"]) or environment.get("pyproject_sha256") != sha256(payload["pyproject.toml"]):
        raise ValueError("index environment hashes do not match packaged files")
    source = index.get("source", {})
    if type(source.get("dirty")) is not bool or any(
        not isinstance(source.get(key), str) or not re.fullmatch(r"[0-9a-f]{40}", source[key])
        for key in ("commit", "tree")
    ):
        raise ValueError("index lacks a valid source revision")


def verify_bundle(root: Path) -> dict:
    """Verify an extracted directory against its index without following links."""
    index = json.loads(read_regular(root, "index.json"))
    if index.get("schema") != INDEX_SCHEMA:
        raise ValueError("unsupported bundle index")
    entries = validate_entries(index.get("files"))
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() or path.is_symlink()}
    if actual != set(entries) | {"index.json"}:
        raise ValueError("directory contents do not match exact index inventory")
    payload = {}
    for name, entry in entries.items():
        data = read_regular(root, name)
        if len(data) != entry["bytes"] or sha256(data) != entry["sha256"]:
            raise ValueError(f"bundle member hash/size mismatch: {name}")
        payload[name] = data
    validate_core_index(index, payload)
    return index


def check_replay_environment(bundle_dir: Path, source_dir: Path) -> None:
    """Require the active replay policy and declared environment to match."""
    for name in ("uv.lock", "pyproject.toml", SPEC_PATH):
        if read_regular(bundle_dir, name) != read_regular(source_dir, name):
            raise ValueError(f"active checkout differs from bundle {name}; use the release source revision")


def extract_archive(archive_path: Path, destination: Path, *, expected_sha256: str) -> dict:
    """Validate the entire archive before creating a fresh destination."""
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"refusing to overwrite: {destination}")
    index, payload = read_archive(archive_path, expected_sha256=expected_sha256)
    # The destination is a fresh directory; no pre-existing child can redirect writes.
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for name, data in payload.items():
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(data)
        with (destination / "index.json").open("xb") as handle:
            handle.write(canonical_json(index))
    except BaseException:
        # Remove only the new directory created by this call, never an input tree.
        shutil.rmtree(destination)
        raise
    return index

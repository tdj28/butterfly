"""Immutable scan tiles with hash-verified resume and aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import platform
import time
from typing import Any

import numpy as np
import scipy

from .scan import (
    ScanManifest,
    atomic_write,
    canonical_json,
    git_value,
    run_scan,
    sha256_bytes,
)


@dataclass(frozen=True, slots=True)
class TileSpec:
    index: int
    count: int
    point_indices: tuple[int, ...]

    @classmethod
    def for_manifest(
        cls, manifest: ScanManifest, *, index: int, count: int
    ) -> "TileSpec":
        if count < 1:
            raise ValueError("tile count must be positive")
        if index < 0 or index >= count:
            raise ValueError("tile index must be in [0, tile_count)")
        total = manifest.a_count * manifest.c_count
        quotient, remainder = divmod(total, count)
        start = index * quotient + min(index, remainder)
        length = quotient + (1 if index < remainder else 0)
        return cls(index=index, count=count, point_indices=tuple(range(start, start + length)))

    @property
    def directory_name(self) -> str:
        return f"tile-{self.index:05d}-of-{self.count:05d}"

    def tile_id(self, *, plan_hash: str, source_commit: str) -> str:
        payload = {
            "schema": "butterfly.scan-tile-plan.v1",
            "plan_hash": plan_hash,
            "source_commit": source_commit,
            "tile_index": self.index,
            "tile_count": self.count,
            "point_indices": list(self.point_indices),
        }
        return sha256_bytes(canonical_json(payload))


def _source(require_clean: bool) -> dict[str, Any]:
    source = {
        "commit": git_value("rev-parse", "HEAD"),
        "branch": git_value("branch", "--show-current"),
        "dirty": bool(git_value("status", "--porcelain")),
    }
    if source["commit"] is None:
        raise RuntimeError("tiled scans require a Git source commit")
    if require_clean and source["dirty"]:
        raise RuntimeError("tiled scans require a clean source tree")
    return source


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_completed_tile(
    directory: Path, *, expected_tile_id: str | None = None
) -> dict[str, Any]:
    completion_path = directory / "complete.json"
    result_path = directory / "result.json"
    receipt_path = directory / "receipt.json"
    if not completion_path.exists():
        raise ValueError(f"tile has no completion marker: {directory}")
    completion = _read_json(completion_path)
    receipt_bytes = receipt_path.read_bytes()
    result_bytes = result_path.read_bytes()
    if completion.get("schema") != "butterfly.scan-tile-completion.v1":
        raise ValueError("unsupported tile completion schema")
    if sha256_bytes(receipt_bytes) != completion.get("receipt_sha256"):
        raise ValueError("tile receipt hash mismatch")
    if sha256_bytes(result_bytes) != completion.get("result_sha256"):
        raise ValueError("tile result hash mismatch")
    receipt = json.loads(receipt_bytes)
    result = json.loads(result_bytes)
    tile_id = completion.get("tile_id")
    if expected_tile_id is not None and tile_id != expected_tile_id:
        raise ValueError("completed tile ID does not match requested tile")
    if receipt.get("tile_id") != tile_id or result.get("tile_id") != tile_id:
        raise ValueError("tile ID mismatch across completion, receipt, and result")
    if receipt.get("result_sha256") != completion.get("result_sha256"):
        raise ValueError("receipt does not bind completed result")
    if result.get("row_count") != receipt.get("row_count"):
        raise ValueError("tile row count mismatch")
    return receipt


def verify_completed_aggregate(directory: Path) -> dict[str, Any]:
    completion_path = directory / "complete.json"
    result_path = directory / "result.json"
    receipt_path = directory / "receipt.json"
    if not completion_path.exists():
        raise ValueError(f"aggregate has no completion marker: {directory}")
    completion = _read_json(completion_path)
    result_bytes = result_path.read_bytes()
    receipt_bytes = receipt_path.read_bytes()
    if completion.get("schema") != "butterfly.tiled-scan-completion.v1":
        raise ValueError("unsupported aggregate completion schema")
    if sha256_bytes(result_bytes) != completion.get("result_sha256"):
        raise ValueError("aggregate result hash mismatch")
    if sha256_bytes(receipt_bytes) != completion.get("receipt_sha256"):
        raise ValueError("aggregate receipt hash mismatch")
    receipt = json.loads(receipt_bytes)
    if receipt.get("result_sha256") != completion.get("result_sha256"):
        raise ValueError("aggregate receipt does not bind completed result")
    return receipt


def execute_scan_tile(
    manifest_path: Path,
    output_root: Path,
    *,
    tile_index: int,
    tile_count: int,
    resume: bool = False,
    require_clean: bool = True,
) -> dict[str, Any]:
    raw_manifest = manifest_path.read_bytes()
    manifest = ScanManifest.from_dict(json.loads(raw_manifest))
    source = _source(require_clean)
    spec = TileSpec.for_manifest(manifest, index=tile_index, count=tile_count)
    tile_id = spec.tile_id(
        plan_hash=manifest.plan_hash, source_commit=str(source["commit"])
    )
    directory = output_root / spec.directory_name
    completion_path = directory / "complete.json"
    if completion_path.exists():
        if not resume:
            raise FileExistsError(f"completed tile already exists: {directory}")
        return verify_completed_tile(directory, expected_tile_id=tile_id)
    if directory.exists() and any(directory.iterdir()) and not resume:
        raise FileExistsError(f"incomplete tile directory exists: {directory}")

    started_at = datetime.now(UTC)
    started = time.perf_counter()
    rows = run_scan(manifest, spec.point_indices)
    elapsed = time.perf_counter() - started
    result = {
        "schema": "butterfly.scan-tile-result.v1",
        "experiment_id": manifest.experiment_id,
        "plan_hash": manifest.plan_hash,
        "tile_id": tile_id,
        "tile_index": spec.index,
        "tile_count": spec.count,
        "point_indices": list(spec.point_indices),
        "row_count": len(rows),
        "rows": rows,
    }
    result_bytes = canonical_json(result)
    result_hash = sha256_bytes(result_bytes)
    receipt = {
        "schema": "butterfly.scan-tile-receipt.v1",
        "experiment_id": manifest.experiment_id,
        "plan_hash": manifest.plan_hash,
        "input_manifest_sha256": sha256_bytes(raw_manifest),
        "tile_id": tile_id,
        "tile_index": spec.index,
        "tile_count": spec.count,
        "point_indices": list(spec.point_indices),
        "row_count": len(rows),
        "result_sha256": result_hash,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "elapsed_seconds": elapsed,
        "source": source,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "label_counts": {
            label: sum(row["label"] == label for row in rows)
            for label in sorted({row["label"] for row in rows})
        },
    }
    receipt_bytes = canonical_json(receipt)
    completion = {
        "schema": "butterfly.scan-tile-completion.v1",
        "tile_id": tile_id,
        "result_sha256": result_hash,
        "receipt_sha256": sha256_bytes(receipt_bytes),
    }
    atomic_write(
        directory / "manifest.normalized.json", canonical_json(manifest.canonical_dict())
    )
    atomic_write(directory / "result.json", result_bytes)
    atomic_write(directory / "receipt.json", receipt_bytes)
    atomic_write(completion_path, canonical_json(completion))
    return receipt


def aggregate_scan_tiles(
    manifest_path: Path,
    output_root: Path,
    *,
    tile_count: int,
    require_clean: bool = True,
) -> dict[str, Any]:
    manifest = ScanManifest.from_path(manifest_path)
    source = _source(require_clean)
    receipts = []
    rows = []
    for index in range(tile_count):
        spec = TileSpec.for_manifest(manifest, index=index, count=tile_count)
        expected_id = spec.tile_id(
            plan_hash=manifest.plan_hash, source_commit=str(source["commit"])
        )
        directory = output_root / spec.directory_name
        receipt = verify_completed_tile(directory, expected_tile_id=expected_id)
        result = _read_json(directory / "result.json")
        receipts.append(receipt)
        rows.extend(result["rows"])
    rows.sort(key=lambda row: row["point_index"])
    expected_indices = list(range(manifest.a_count * manifest.c_count))
    if [row["point_index"] for row in rows] != expected_indices:
        raise ValueError("tiles do not form an exact, non-overlapping grid partition")

    result = {
        "schema": "butterfly.tiled-scan-result.v1",
        "experiment_id": manifest.experiment_id,
        "plan_hash": manifest.plan_hash,
        "tile_count": tile_count,
        "shape": [manifest.a_count, manifest.c_count],
        "row_count": len(rows),
        "rows": rows,
    }
    result_bytes = canonical_json(result)
    result_hash = sha256_bytes(result_bytes)
    receipt = {
        "schema": "butterfly.tiled-scan-receipt.v1",
        "experiment_id": manifest.experiment_id,
        "plan_hash": manifest.plan_hash,
        "tile_count": tile_count,
        "tile_ids": [item["tile_id"] for item in receipts],
        "tile_result_sha256": [item["result_sha256"] for item in receipts],
        "row_count": len(rows),
        "result_sha256": result_hash,
        "source": source,
        "label_counts": {
            label: sum(row["label"] == label for row in rows)
            for label in sorted({row["label"] for row in rows})
        },
    }
    aggregate_directory = output_root / "aggregate"
    completion_path = aggregate_directory / "complete.json"
    if completion_path.exists():
        existing = verify_completed_aggregate(aggregate_directory)
        comparable_keys = ("plan_hash", "tile_count", "tile_ids", "result_sha256")
        if any(existing.get(key) != receipt.get(key) for key in comparable_keys):
            raise ValueError("completed aggregate does not match current tiles")
        return existing
    receipt_bytes = canonical_json(receipt)
    completion = {
        "schema": "butterfly.tiled-scan-completion.v1",
        "result_sha256": result_hash,
        "receipt_sha256": sha256_bytes(receipt_bytes),
    }
    atomic_write(aggregate_directory / "result.json", result_bytes)
    atomic_write(aggregate_directory / "receipt.json", receipt_bytes)
    atomic_write(completion_path, canonical_json(completion))
    return receipt

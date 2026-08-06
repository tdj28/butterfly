"""Manifest-driven CPU parameter scans with hashed result receipts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np
import scipy

from .classify import classify_fundamental_period
from .integrate import SolverConfig
from .models import RosslerParameters
from .poincare import collect_crossings, legacy_rossler_section


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(value)
    temporary.replace(path)


@dataclass(frozen=True, slots=True)
class ScanManifest:
    experiment_id: str
    a_min: float
    a_max: float
    a_count: int
    b: float
    c_min: float
    c_max: float
    c_count: int
    initial_state: tuple[float, float, float]
    transient: float
    observation_horizon: float
    max_crossings: int
    solver: SolverConfig
    classifier_max_period: int
    classifier_required_repeats: int
    classifier_atol: float
    classifier_rtol: float

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ScanManifest":
        if value.get("schema") != "butterfly.scan-manifest.v1":
            raise ValueError("unsupported or missing scan manifest schema")
        grid = value["grid"]
        integration = value["integration"]
        classifier = value["classifier"]
        solver = SolverConfig(**integration["solver"])
        manifest = cls(
            experiment_id=str(value["experiment_id"]),
            a_min=float(grid["a"]["min"]),
            a_max=float(grid["a"]["max"]),
            a_count=int(grid["a"]["count"]),
            b=float(grid["b"]),
            c_min=float(grid["c"]["min"]),
            c_max=float(grid["c"]["max"]),
            c_count=int(grid["c"]["count"]),
            initial_state=tuple(map(float, integration["initial_state"])),
            transient=float(integration["transient"]),
            observation_horizon=float(integration["observation_horizon"]),
            max_crossings=int(integration["max_crossings"]),
            solver=solver,
            classifier_max_period=int(classifier["max_period"]),
            classifier_required_repeats=int(classifier["required_repeats"]),
            classifier_atol=float(classifier["atol"]),
            classifier_rtol=float(classifier["rtol"]),
        )
        manifest.validate()
        return manifest

    @classmethod
    def from_path(cls, path: Path) -> "ScanManifest":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def validate(self) -> None:
        if not self.experiment_id:
            raise ValueError("experiment_id is required")
        if self.a_count < 1 or self.c_count < 1:
            raise ValueError("grid counts must be positive")
        if self.a_max < self.a_min or self.c_max < self.c_min:
            raise ValueError("grid maxima must not be smaller than minima")
        if len(self.initial_state) != 3 or not np.all(np.isfinite(self.initial_state)):
            raise ValueError("initial_state must contain three finite values")
        if self.transient < 0.0 or self.observation_horizon <= 0.0:
            raise ValueError("invalid integration horizons")
        if self.max_crossings < 1:
            raise ValueError("max_crossings must be positive")

    def canonical_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["solver"] = asdict(self.solver)
        return {"schema": "butterfly.normalized-scan-manifest.v1", **value}

    @property
    def plan_hash(self) -> str:
        return sha256_bytes(canonical_json(self.canonical_dict()))


def git_value(*arguments: str) -> str | None:
    try:
        return subprocess.check_output(
            ("git", *arguments), text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run_scan(manifest: ScanManifest) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for a in np.linspace(manifest.a_min, manifest.a_max, manifest.a_count):
        for c in np.linspace(manifest.c_min, manifest.c_max, manifest.c_count):
            parameters = RosslerParameters(a=float(a), b=manifest.b, c=float(c))
            section = legacy_rossler_section(parameters)
            crossings = collect_crossings(
                parameters,
                manifest.initial_state,
                section,
                transient=manifest.transient,
                observation_horizon=manifest.observation_horizon,
                max_crossings=manifest.max_crossings,
                config=manifest.solver,
            )
            classification = classify_fundamental_period(
                crossings.states,
                max_period=manifest.classifier_max_period,
                required_repeats=manifest.classifier_required_repeats,
                atol=manifest.classifier_atol,
                rtol=manifest.classifier_rtol,
            )
            rows.append(
                {
                    "a": parameters.a,
                    "b": parameters.b,
                    "c": parameters.c,
                    "label": classification.label.value,
                    "fundamental_period": classification.fundamental_period,
                    "confidence": classification.confidence,
                    "recurrence_error": classification.recurrence_error,
                    "recurrence_tolerance": classification.recurrence_tolerance,
                    "crossing_count": len(crossings.times),
                    "integration_success": crossings.integration_success,
                    "integration_message": crossings.integration_message,
                }
            )
    return rows


def execute_scan(manifest_path: Path, output_directory: Path) -> dict[str, Any]:
    raw_manifest = manifest_path.read_bytes()
    manifest = ScanManifest.from_dict(json.loads(raw_manifest))
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    rows = run_scan(manifest)
    elapsed = time.perf_counter() - started
    result = {
        "schema": "butterfly.scan-result.v1",
        "experiment_id": manifest.experiment_id,
        "plan_hash": manifest.plan_hash,
        "shape": [manifest.a_count, manifest.c_count],
        "row_count": len(rows),
        "rows": rows,
    }
    result_bytes = canonical_json(result)
    result_hash = sha256_bytes(result_bytes)
    receipt = {
        "schema": "butterfly.scan-receipt.v1",
        "experiment_id": manifest.experiment_id,
        "plan_hash": manifest.plan_hash,
        "input_manifest_sha256": sha256_bytes(raw_manifest),
        "result_file": "result.json",
        "result_sha256": result_hash,
        "row_count": len(rows),
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "elapsed_seconds": elapsed,
        "source": {
            "commit": git_value("rev-parse", "HEAD"),
            "branch": git_value("branch", "--show-current"),
            "dirty": bool(git_value("status", "--porcelain")),
        },
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
    atomic_write(output_directory / "manifest.normalized.json", canonical_json(manifest.canonical_dict()))
    atomic_write(output_directory / "result.json", result_bytes)
    atomic_write(output_directory / "receipt.json", canonical_json(receipt))
    return receipt

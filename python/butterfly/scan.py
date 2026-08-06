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

from .classify import (
    OrbitLabel,
    classify_fundamental_period,
    classify_with_lyapunov,
    closest_recurrence_candidate,
)
from .integrate import SolverConfig
from .lyapunov import LyapunovConfig, lyapunov_block_estimates, lyapunov_spectrum
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
    lyapunov_transient: float | None = None
    lyapunov_duration: float | None = None
    lyapunov_qr_interval: float | None = None
    lyapunov_blocks: int | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ScanManifest":
        schema = value.get("schema")
        if schema not in ("butterfly.scan-manifest.v1", "butterfly.scan-manifest.v2"):
            raise ValueError("unsupported or missing scan manifest schema")
        grid = value["grid"]
        integration = value["integration"]
        classifier = value["classifier"]
        solver = SolverConfig(**integration["solver"])
        lyapunov = value.get("lyapunov")
        if schema == "butterfly.scan-manifest.v2" and lyapunov is None:
            raise ValueError("v2 scan manifests require Lyapunov configuration")
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
            lyapunov_transient=(
                float(lyapunov["transient"]) if lyapunov is not None else None
            ),
            lyapunov_duration=(
                float(lyapunov["duration"]) if lyapunov is not None else None
            ),
            lyapunov_qr_interval=(
                float(lyapunov["qr_interval"]) if lyapunov is not None else None
            ),
            lyapunov_blocks=(
                int(lyapunov["blocks"]) if lyapunov is not None else None
            ),
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
        lyapunov_values = (
            self.lyapunov_transient,
            self.lyapunov_duration,
            self.lyapunov_qr_interval,
            self.lyapunov_blocks,
        )
        if any(value is not None for value in lyapunov_values):
            if any(value is None for value in lyapunov_values):
                raise ValueError("Lyapunov scan configuration must be complete")
            assert self.lyapunov_transient is not None
            assert self.lyapunov_duration is not None
            assert self.lyapunov_qr_interval is not None
            assert self.lyapunov_blocks is not None
            if (
                self.lyapunov_transient < 0.0
                or self.lyapunov_duration <= 0.0
                or self.lyapunov_qr_interval <= 0.0
                or self.lyapunov_blocks < 2
            ):
                raise ValueError("invalid Lyapunov scan configuration")
            available_steps = self.lyapunov_duration / self.lyapunov_qr_interval
            if available_steps < self.lyapunov_blocks:
                raise ValueError("Lyapunov duration cannot supply the requested blocks")

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


def parameter_grid(manifest: ScanManifest) -> list[RosslerParameters]:
    """Return the deterministic row-major parameter grid."""

    return [
        RosslerParameters(a=float(a), b=manifest.b, c=float(c))
        for a in np.linspace(manifest.a_min, manifest.a_max, manifest.a_count)
        for c in np.linspace(manifest.c_min, manifest.c_max, manifest.c_count)
    ]


def run_scan(
    manifest: ScanManifest, point_indices: tuple[int, ...] | None = None
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    grid = parameter_grid(manifest)
    selected = tuple(range(len(grid))) if point_indices is None else point_indices
    if len(set(selected)) != len(selected):
        raise ValueError("point indices must be unique")
    if any(index < 0 or index >= len(grid) for index in selected):
        raise ValueError("point index outside manifest grid")
    for point_index in selected:
        parameters = grid[point_index]
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
        recurrence = classify_fundamental_period(
            crossings.states,
            max_period=manifest.classifier_max_period,
            required_repeats=manifest.classifier_required_repeats,
            atol=manifest.classifier_atol,
            rtol=manifest.classifier_rtol,
        )
        candidate = closest_recurrence_candidate(
            crossings.states,
            max_period=manifest.classifier_max_period,
            required_repeats=manifest.classifier_required_repeats,
            atol=manifest.classifier_atol,
            rtol=manifest.classifier_rtol,
        )
        row: dict[str, Any] = {
            "a": parameters.a,
            "b": parameters.b,
            "c": parameters.c,
            "label": recurrence.label.value,
            "fundamental_period": recurrence.fundamental_period,
            "confidence": recurrence.confidence,
            "classification_reason": recurrence.reason,
            "classification_evidence": ["period-recurrence"],
            "recurrence_label": recurrence.label.value,
            "recurrence_error": recurrence.recurrence_error,
            "recurrence_tolerance": recurrence.recurrence_tolerance,
            "candidate_period": candidate.period if candidate is not None else None,
            "candidate_recurrence_error": (
                candidate.error if candidate is not None else None
            ),
            "candidate_recurrence_tolerance": (
                candidate.tolerance if candidate is not None else None
            ),
            "candidate_normalized_error": (
                candidate.normalized_error if candidate is not None else None
            ),
            "crossing_count": len(crossings.times),
            "integration_success": crossings.integration_success,
            "integration_message": crossings.integration_message,
            "lyapunov_success": None,
            "lyapunov_exponents": None,
            "lyapunov_block_standard_error": None,
            "lyapunov_trace_identity_error": None,
        }
        if point_indices is not None:
            row["point_index"] = point_index
        if not crossings.integration_success:
            row.update(
                {
                    "label": OrbitLabel.NUMERICAL_FAILURE.value,
                    "fundamental_period": None,
                    "confidence": 0.0,
                    "classification_reason": crossings.integration_message,
                    "classification_evidence": ["crossing-integration-failure"],
                }
            )
        elif manifest.lyapunov_duration is not None:
            assert manifest.lyapunov_transient is not None
            assert manifest.lyapunov_qr_interval is not None
            assert manifest.lyapunov_blocks is not None
            spectrum = lyapunov_spectrum(
                parameters,
                manifest.initial_state,
                config=LyapunovConfig(
                    transient=manifest.lyapunov_transient,
                    duration=manifest.lyapunov_duration,
                    qr_interval=manifest.lyapunov_qr_interval,
                    solver=manifest.solver,
                ),
            )
            row["lyapunov_success"] = spectrum.success
            row["lyapunov_trace_identity_error"] = spectrum.trace_identity_error
            if spectrum.success and spectrum.qr_steps >= manifest.lyapunov_blocks:
                blocks = lyapunov_block_estimates(
                    spectrum, blocks=manifest.lyapunov_blocks
                )
                standard_error = np.std(blocks, axis=0, ddof=1) / np.sqrt(
                    len(blocks)
                )
                dynamics = classify_with_lyapunov(
                    recurrence, spectrum.exponents, standard_error
                )
                row.update(
                    {
                        "label": dynamics.label.value,
                        "fundamental_period": dynamics.fundamental_period,
                        "confidence": dynamics.confidence,
                        "classification_reason": dynamics.reason,
                        "classification_evidence": list(dynamics.evidence),
                        "lyapunov_exponents": spectrum.exponents.tolist(),
                        "lyapunov_block_standard_error": standard_error.tolist(),
                    }
                )
            else:
                row.update(
                    {
                        "label": OrbitLabel.NUMERICAL_FAILURE.value,
                        "fundamental_period": None,
                        "confidence": 0.0,
                        "classification_reason": spectrum.message,
                        "classification_evidence": ["lyapunov-failure"],
                    }
                )
        rows.append(row)
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

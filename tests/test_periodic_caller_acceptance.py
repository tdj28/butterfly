"""Failure-injection tests: unsuccessful corrections must not become evidence."""

import argparse
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from butterfly import RosslerParameters, SolverConfig
from butterfly.scan import sha256_bytes

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def _correction(success=True, *, optimizer_success=True):
    return SimpleNamespace(
        initial_state=np.asarray((1.0, 0.0, 0.0)),
        period_time=12.0,
        closure_error=1e-12,
        phase_residual=0.0 if success else 1e-3,
        correction_norm=0.0,
        evaluations=1,
        optimizer_success=optimizer_success,
        success=success,
        message="injected correction status",
    )


def _monodromy():
    return SimpleNamespace(
        success=True,
        multipliers=np.asarray((1.0, -0.9, -0.01), dtype=complex),
        closure_error=1e-12,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "compare_periodic_orbit_identity",
        "qualify_separated_normal_form",
        "refine_identity_constrained_flip",
    ],
)
@pytest.mark.parametrize(
    ("success", "optimizer_success"), [(True, True), (False, True), (False, False)]
)
def test_periodic_wrappers_require_correction_success(
    monkeypatch, module_name, success, optimizer_success
):
    module = importlib.import_module(module_name)
    correction = _correction(success, optimizer_success=optimizer_success)
    monodromy_calls = []
    monkeypatch.setattr(module, "correct_periodic_orbit", lambda *a, **kw: correction)

    def monodromy(*args, **kwargs):
        monodromy_calls.append(args)
        return _monodromy()

    monkeypatch.setattr(module, "flow_monodromy", monodromy)
    solver = SolverConfig()
    parameters = RosslerParameters(a=0.2, b=0.2, c=5.0)

    def invoke():
        if module_name == "compare_periodic_orbit_identity":
            return module.corrected_from_rows(
                [{"b": 0.2, "initial_state": [1, 0, 0], "period_time": 12}],
                target_b=0.2,
                parameters=parameters,
                solver=solver,
                tolerance=1e-11,
                max_evaluations=4,
            )
        if module_name == "qualify_separated_normal_form":
            return module.correct_fixed_b(
                a=0.2,
                b=0.2,
                c=5.0,
                initial_state=correction.initial_state,
                period_time=12.0,
                solver=solver,
                tolerance=1e-11,
                max_evaluations=4,
            )
        monkeypatch.setattr(module, "crossing_count", lambda *args: (2, True))
        return module.multiplier(
            0.2, 0.2, 5.0, correction.initial_state, 12.0, solver,
            {"tolerance": 1e-11, "max_evaluations": 4},
        )

    if success:
        assert invoke()[0] is correction
        assert len(monodromy_calls) == 1
    else:
        # A closed trajectory can fail its phase condition; it must not be
        # used to update a Floquet bracket or qualify orbit identity.
        with pytest.raises(RuntimeError, match="correction failed"):
            invoke()
        assert monodromy_calls == []


def _cli_inputs(monkeypatch, tmp_path, module, manifest, source=None):
    arguments = SimpleNamespace(
        manifest=tmp_path / "manifest.json", output=tmp_path / "output.json"
    )
    if source is not None:
        source_bytes = json.dumps(source).encode()
        arguments.source_receipt = tmp_path / "source.json"
        arguments.source_receipt.write_bytes(source_bytes)
        manifest["source_receipt_sha256"] = sha256_bytes(source_bytes)
    arguments.manifest.write_text(json.dumps(manifest))
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: arguments)
    monkeypatch.setattr(
        module, "git_value", lambda *args: "" if args[0] == "status" else "test-source"
    )
    return arguments.output


def test_natural_b_continuation_rejects_failed_seed(monkeypatch, tmp_path):
    module = importlib.import_module("continue_periodic_orbits_in_b")
    manifest = {
        "schema": "butterfly.periodic-b-continuation-manifest.v1",
        "solver": {},
        "crossings": {
            "initial_state": [1, 0, 0], "transient": 0, "observation_horizon": 20,
            "max_crossings": 4, "max_period": 2, "required_repeats": 2,
            "atol": 1e-8, "rtol": 1e-8,
        },
        "continuation": {},
        "families": [{"id": "test", "period": 1, "start": {"a": 0.2, "b": 0.2, "c": 5}}],
        "corrector": {"max_evaluations": 4, "tolerance": 1e-11},
    }
    output = _cli_inputs(monkeypatch, tmp_path, module, manifest)
    monkeypatch.setattr(
        module, "collect_crossings",
        lambda *args, **kwargs: SimpleNamespace(states=np.zeros((3, 3)), times=np.arange(3.0)),
    )
    monkeypatch.setattr(
        module, "classify_fundamental_period",
        lambda *args, **kwargs: SimpleNamespace(fundamental_period=1),
    )
    monkeypatch.setattr(module, "correct_periodic_orbit", lambda *a, **kw: _correction(False))
    consumed = []
    monkeypatch.setattr(module, "orbit_row", lambda *args: consumed.append(args))
    with pytest.raises(RuntimeError, match="seed periodic correction failed"):
        module.main()
    assert consumed == []
    assert not output.exists()


def _continuation_inputs(schema):
    manifest = {
        "schema": schema,
        "source_direction": 1,
        "fixed_a": 0.2,
        "fixed_b": 0.2,
        "reference_solver": {},
        "independent_solver": {"method": "Radau"},
        "corrector": {"tolerance": 1e-11, "maximum_evaluations": 4},
        "continuation": {
            "start_c": 5.0, "end_c": 5.01, "maximum_points": 1,
            "initial_step_length": 0.001, "maximum_steps": 1,
            "maximum_retries_per_step": 0,
        },
        "acceptance": {
            "maximum_bracket_multiplier_imaginary": 1e-8,
            "minimum_half_period_closure": 0.1,
        },
        "orbit_sample_count": 8,
        "independent_check_stride": 1,
    }
    source = {
        "schema": "butterfly.period2-c-flip-switch-receipt.v1",
        "branches": [{"direction": 1, "rows": [
            {"parameters": {"c": c}, "initial_state": [1, 0, 0], "period_time": 12.0}
            for c in (5.0, 5.01)
        ]}],
    }
    return manifest, source


def test_natural_c_continuation_rejects_failed_independent_check(monkeypatch, tmp_path):
    module = importlib.import_module("continue_period2_c_to_flip")
    manifest, source = _continuation_inputs("butterfly.period2-c-to-flip-manifest.v1")
    output = _cli_inputs(monkeypatch, tmp_path, module, manifest, source)
    corrections = iter((_correction(), _correction(False)))
    monkeypatch.setattr(module, "correct_periodic_orbit", lambda *a, **kw: next(corrections))
    monodromy_calls = []

    def monodromy(*args, **kwargs):
        monodromy_calls.append(args)
        return _monodromy()

    monkeypatch.setattr(module, "flow_monodromy", monodromy)
    monkeypatch.setattr(module, "_half_period_closure", lambda *args: 1.0)
    monkeypatch.setattr(module, "_winding", lambda *args: 2.0)
    dense_calls = []
    monkeypatch.setattr(module, "dense_orbit", lambda *args: dense_calls.append(args))
    with pytest.raises(RuntimeError, match="independent periodic correction failed"):
        module.main()
    assert len(monodromy_calls) == 1  # Only the successful reference orbit.
    assert dense_calls == []
    assert not output.exists()


@pytest.mark.parametrize("period", [2, 4])
@pytest.mark.parametrize("failed_role", ["independent", "reference"])
def test_arclength_verification_rejects_failed_correction(
    monkeypatch, tmp_path, period, failed_role
):
    module = importlib.import_module(f"continue_period{period}_c_arclength_to_flip")
    manifest, source = _continuation_inputs(
        f"butterfly.period{period}-c-arclength-to-flip-manifest.v1"
    )
    output = _cli_inputs(monkeypatch, tmp_path, module, manifest, source)
    monkeypatch.setattr(
        module, "correct_arclength_c", lambda predictor, *a, **kw: (predictor, {"success": True})
    )
    monkeypatch.setattr(
        module, "_diagnose",
        lambda point, **kwargs: {
            "parameters": {"c": float(point[4])}, "half_period_closure": 1.0,
            "dominant_nontrivial_multiplier": {"real": -0.9, "imag": 0.0},
        },
    )
    monkeypatch.setattr(module, "first_real_minus_one_bracket", lambda *args: None)
    correction_calls = []

    def correct(*args, **kwargs):
        role = "independent" if not correction_calls else "reference"
        correction_calls.append(role)
        return _correction(role != failed_role)

    monkeypatch.setattr(module, "correct_periodic_orbit", correct)
    monodromy_calls = []

    def monodromy(*args, **kwargs):
        monodromy_calls.append(args)
        return _monodromy()

    monkeypatch.setattr(module, "flow_monodromy", monodromy)
    dense_calls = []
    monkeypatch.setattr(module, "dense_orbit", lambda *args: dense_calls.append(args))
    with pytest.raises(RuntimeError, match=f"{failed_role} periodic correction failed"):
        module.main()
    assert correction_calls[-1] == failed_role
    assert len(monodromy_calls) == (0 if failed_role == "independent" else 1)
    assert dense_calls == []
    assert not output.exists()

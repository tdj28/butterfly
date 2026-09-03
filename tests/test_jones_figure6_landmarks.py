import copy
import json
from pathlib import Path

from scripts.classify_jones_figure6_landmarks import load_inputs, summarize_rows


MANIFEST = Path("experiments/manifests/EXP-174-jones-figure6-landmark-classification.json")


def _manifest_for_tests() -> dict:
    manifest, _raw, _source = load_inputs(MANIFEST)
    manifest = copy.deepcopy(manifest)
    manifest["initial_states"] = [[0.0, 4.0, 0.0]]
    manifest["acceptance"]["required_landmark_count"] = 1
    return manifest


def _row(profile: str, solver: str, label: str = "periodic", period: int | None = 5) -> dict:
    return {
        "landmark_index": 0,
        "initial_state_index": 0,
        "profile": profile,
        "solver": solver,
        "integration_success": True,
        "crossing_count": 160,
        "recurrence": {"label": label, "fundamental_period": period},
    }


def test_manifest_binds_the_source_transcription() -> None:
    manifest, raw, source = load_inputs(MANIFEST)
    assert json.loads(raw)["experiment_id"] == "EXP-174"
    assert len(source["figure6"]["parameter_landmarks"]) == 10
    assert "expected_period" not in json.dumps(manifest)


def test_summary_passes_consistent_solver_and_profile_signatures() -> None:
    rows = [
        _row("early", "dop853"),
        _row("qualified", "dop853"),
        _row("qualified", "radau"),
    ]
    summary = summarize_rows(rows, _manifest_for_tests())
    assert summary["passed"]
    assert summary["resolved_periodic_count"] == 1


def test_summary_retains_solver_disagreement_as_failure() -> None:
    rows = [
        _row("early", "dop853"),
        _row("qualified", "dop853"),
        _row("qualified", "radau", period=6),
    ]
    summary = summarize_rows(rows, _manifest_for_tests())
    assert not summary["passed"]
    assert not summary["qualified_solver_agreement"]


def test_summary_allows_consistently_unresolved_landmark() -> None:
    rows = [
        _row("early", "dop853", label="unresolved", period=None),
        _row("qualified", "dop853", label="unresolved", period=None),
        _row("qualified", "radau", label="unresolved", period=None),
    ]
    summary = summarize_rows(rows, _manifest_for_tests())
    assert summary["passed"]
    assert summary["resolved_periodic_count"] == 0

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "qualify_atlas_transients.py"
SPEC = importlib.util.spec_from_file_location("qualify_atlas_transients", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def initial(label: str, period: int | None) -> dict:
    return {"timeline": [{"label": label, "fundamental_period": period}]}


def test_final_outcome_detects_common_capture() -> None:
    outcome = MODULE.final_outcome([initial("periodic", 6), initial("periodic", 6)])
    assert outcome["status"] == "common_periodic_capture"
    assert outcome["consensus_period"] == 6


def test_final_outcome_preserves_distinct_periods() -> None:
    outcome = MODULE.final_outcome([initial("periodic", 3), initial("periodic", 12)])
    assert outcome["status"] == "distinct_periodic_endpoints"
    assert outcome["consensus_period"] is None


def test_final_outcome_retains_unresolved_state() -> None:
    outcome = MODULE.final_outcome([initial("periodic", 2), initial("unresolved", None)])
    assert outcome["status"] == "unresolved_or_nonperiodic"

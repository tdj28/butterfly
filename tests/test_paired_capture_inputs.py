"""Pure synthetic raw/summary concordance tests; no private artifact inputs."""
from dataclasses import asdict, replace
import copy
import json

import numpy as np
import pytest

from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.poincare import legacy_rossler_section, barrio_rossler_section
from scripts.verify_paired_capture_inputs import extract_references, load_legacy_raw


def fixture():
    parameters = RosslerParameters(.2, .2, 7.)
    sections = {"historical-negative": replace(legacy_rossler_section(parameters), direction=-1),
                "barrio-positive": barrio_rossler_section(parameters)}
    raw = {}
    row = {"correction": {"period_time": 10.}, "integration": {"sections": {}}, "sections": {}}
    for name, section in sections.items():
        n = 6 if name == "historical-negative" else 8
        states = np.zeros((n, 3))
        states[:, 2] = .01
        if n == 6:
            states[:, 0], states[:, 1] = -np.arange(1, n+1), section.offset
        else:
            states[:, 0], states[:, 1] = section.offset, -np.arange(1, n+1)
        times = np.linspace(3, 11, n)
        fields = np.array([rossler_rhs(t, state, parameters) for t, state in zip(times, states)])
        raw.update({name+"_times": times, name+"_states": states,
                    name+"_normal_velocity": fields @ section.normal, name+"_accepted": np.ones(n, bool)})
        row["integration"]["sections"][name] = {"section": json.loads(json.dumps(asdict(section)))}
        row["sections"][name] = {"windows": [{"states": states.tolist(), "phases": (times/10-.25).tolist(),
                                             "count": n, "passed": True}]}
    return raw, row, parameters


def test_exact_ordered_raw_rows_reconstruct_declared_reference():
    raw, row, parameters = fixture()
    result = extract_references(raw, row, parameters)
    assert [r["count"] for r in result.values()] == [6, 8]
    assert result["historical-negative"]["raw_event_indices"] == list(range(6))


@pytest.mark.parametrize("kind", ["summary", "phase", "gate", "velocity", "membership", "time-order"])
def test_copying_a_summary_cannot_substitute_for_raw_concordance(kind):
    raw, row, parameters = fixture()
    name = "historical-negative"
    if kind == "summary":
        row["sections"][name]["windows"][0]["states"].reverse()
    elif kind == "phase":
        row["sections"][name]["windows"][0]["phases"][0] += .001
    elif kind == "gate":
        row["integration"]["sections"][name]["section"]["gate_upper"] += .001
    elif kind == "velocity":
        raw[name+"_normal_velocity"][0] += .001
    elif kind == "membership":
        raw[name+"_accepted"][0] = False
    else:
        raw[name+"_times"] = raw[name+"_times"][::-1]
    with pytest.raises(ValueError):
        extract_references(raw, row, parameters)


def test_unknown_legacy_npz_members_are_not_allowed(tmp_path):
    path = tmp_path/"raw.npz"
    np.savez(path, unexpected=np.zeros(2))
    with pytest.raises(ValueError, match="unexpected"):
        load_legacy_raw(path)

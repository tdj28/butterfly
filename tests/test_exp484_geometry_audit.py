import numpy as np
import pytest
from butterfly.models import RosslerParameters, rossler_rhs
from butterfly.poincare import legacy_rossler_section
from scripts import audit_exp484_return_geometry as a


def fixture():
    parameters = RosslerParameters(.2, .2, 7.)
    section = legacy_rossler_section(parameters)
    initial, final = [-2., section.offset, .02], [-3., section.offset, .03]
    phi = np.array([[1., 2.], [3., 4.], [5., 6.]])
    normal = np.array([0., 1., 0.])
    velocity = rossler_rhs(5., final, parameters)
    corrected = phi + np.outer(velocity, -(normal @ phi)/(normal @ velocity))
    plan = dict(rtol=1e-10, atol=1e-12, max_step=.02, horizon=20., minimum_angle=1e-7, initial_root_guard=1e-8)
    value = dict(plan, initial_state=initial, method="DOP853", axes=[0, 2], status="returned",
        raw_event_times=[0., 5.], raw_event_states=[initial, final], raw_event_tangents=[phi.tolist(), phi.tolist()],
        raw_event_gate_accepted=[True, True], selected_event=1, return_time=5., return_state=final,
        section_tangent=corrected.tolist(), return_jacobian=corrected[[0, 2]].tolist())
    return value, initial, plan, parameters


def test_separate_derivative_algebra_agrees():
    value, initial, plan, parameters = fixture()
    assert a.audit_trial(value, initial, "DOP853", plan, parameters) < 1e-12


def test_wrong_event_gate_or_first_return_is_rejected():
    value, initial, plan, parameters = fixture()
    value["raw_event_gate_accepted"][1] = False
    with pytest.raises(ValueError, match="gate membership"):
        a.audit_trial(value, initial, "DOP853", plan, parameters)
    value["raw_event_gate_accepted"][1] = True
    value["selected_event"] = 0
    with pytest.raises(ValueError, match="first eligible"):
        a.audit_trial(value, initial, "DOP853", plan, parameters)


def test_wrong_derivative_or_configuration_is_rejected():
    value, initial, plan, parameters = fixture()
    value["return_jacobian"][0][0] += 1
    with pytest.raises(ValueError, match="2D derivative"):
        a.audit_trial(value, initial, "DOP853", plan, parameters)
    value["rtol"] = 1e-4
    with pytest.raises(ValueError, match="configuration"):
        a.audit_trial(value, initial, "DOP853", plan, parameters)


def test_wrong_completed_anchor_stops_before_input_selection(tmp_path, monkeypatch):
    (tmp_path/"summary.json").write_text("{}")
    monkeypatch.setattr(a, "TARGET", tmp_path)
    monkeypatch.setattr(a.run, "prepare", lambda p: pytest.fail("read source after invalid anchor"))
    with pytest.raises(ValueError, match="receipt anchor"):
        a.audit()

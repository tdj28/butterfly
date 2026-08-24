from scripts.register_jones_period1536_decimal_event_phase import (
    SCHEMA,
    direct_node_rms,
    roll_nodes,
)


def test_phase_registration_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period1536-decimal-phase-registration-manifest.v1"


def test_roll_nodes_uses_numpy_roll_convention():
    assert roll_nodes([0, 1, 2, 3], 1) == [3, 0, 1, 2]


def test_direct_node_rms_is_zero_for_identity():
    nodes = [["1", "2", "3"], ["4", "5", "6"]]
    assert direct_node_rms(nodes, nodes) == 0.0

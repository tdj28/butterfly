from scripts.qualify_jones_returning_period12_children import SCHEMA, parameter_side


def test_returning_child_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period12-child-qualification-manifest.v1"


def test_parameter_side_is_directional_and_tolerance_aware():
    assert parameter_side(0.9, 1.0) == -1
    assert parameter_side(1.1, 1.0) == 1
    assert parameter_side(1.0 + 1e-13, 1.0) == 0

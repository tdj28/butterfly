from scripts.qualify_jones_returning_period12_children_multiscale import SCHEMA


def test_returning_child_multiscale_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period12-child-multiscale-manifest.v1"

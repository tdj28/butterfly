from scripts.switch_jones_returning_period24_multiscale import SCHEMA, source_event


def test_returning_period24_switch_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-returning-period24-multiscale-switch-manifest.v1"


def test_period12_root_maps_to_generic_event():
    receipt = {
        "root_results": {
            "dop853": {
                "root": {"a": 0.24, "c": 7.62},
                "root_full": {
                    "b": 0.2,
                    "child": {"initial_state": [1, 2, 3], "period_time": 90.0},
                },
            }
        }
    }
    assert source_event(receipt, "dop853") == {
        "a": 0.24,
        "b": 0.2,
        "c": 7.62,
        "initial_state": [1, 2, 3],
        "period_time": 90.0,
    }

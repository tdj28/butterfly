from scripts.qualify_jones_period6_flip_extremum_count import SCHEMA


def test_flip_extremum_count_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-extremum-count-manifest.v1"

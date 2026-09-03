from scripts.continue_jones_period6_flip_through_grazing import (
    SCHEMA,
    _invariant_row_passes,
)


def test_through_grazing_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-through-grazing-manifest.v1"


def test_invariant_pass_ignores_only_raw_historical_count():
    row = {"checks": {"orbit": True, "historical_section": False, "barrio_section": True}}
    assert _invariant_row_passes(row)
    row["checks"]["barrio_section"] = False
    assert not _invariant_row_passes(row)

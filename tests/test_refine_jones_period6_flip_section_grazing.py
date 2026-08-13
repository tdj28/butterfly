from scripts.refine_jones_period6_flip_section_grazing import (
    SCHEMA,
    _scientific_event_passes,
)


def test_flip_section_grazing_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-section-grazing-manifest.v1"


def test_scientific_event_pass_ignores_only_historical_count():
    row = {"checks": {"orbit": True, "historical_section": False, "barrio_section": True}}
    assert _scientific_event_passes(row)
    row["checks"]["orbit"] = False
    assert not _scientific_event_passes(row)

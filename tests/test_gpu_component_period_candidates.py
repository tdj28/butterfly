import math

from scripts.prepare_gpu_component_period_candidates import farthest_component_sample


def test_farthest_component_sample_starts_at_anchor_and_is_deterministic() -> None:
    rows = {
        10: (0.0, 0.0),
        11: (1.0, 0.0),
        12: (0.0, 1.0),
        13: (1.0, 1.0),
        14: (0.5, 0.5),
    }
    selected, radius = farthest_component_sample(
        [14, 13, 12, 11, 10],
        rows,
        sample_count=3,
        anchor_point_index=14,
    )
    assert selected == [14, 10, 11]
    assert math.isclose(radius, math.sqrt(0.5))


def test_farthest_component_sample_rejects_anchor_outside_component() -> None:
    try:
        farthest_component_sample(
            [1, 2],
            {1: (0.0, 0.0), 2: (1.0, 1.0)},
            sample_count=1,
            anchor_point_index=3,
        )
    except ValueError as error:
        assert "anchor" in str(error)
    else:
        raise AssertionError("missing anchor must fail")

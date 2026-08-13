import numpy as np

from scripts.plot_exp215_217_folded_flip_locus import SCHEMA, arm_separation


def test_folded_flip_locus_figure_schema_is_versioned():
    assert SCHEMA == "butterfly.exp215-217-folded-flip-locus-figure.v1"


def test_arm_separation_interpolates_common_c_values():
    original = [{"c": 1.0, "a": 0.1}, {"c": 2.0, "a": 0.2}]
    returning = [{"c": 1.0, "a": 0.4}, {"c": 2.0, "a": 0.6}]
    np.testing.assert_allclose(arm_separation(original, returning, [1.0, 1.5, 2.0]), [0.3, 0.35, 0.4])

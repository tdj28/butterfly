from scripts.plot_exp324_325_target_collapse import SCHEMA, accepted_factors


def test_target_collapse_figure_schema_is_versioned():
    assert SCHEMA == "butterfly.exp324-325-target-collapse-figure.v1"


def test_accepted_factor_matches_history_decimal_residual():
    receipt = {
        "history": [
            {"iteration": 0, "matching_residual_decimal": "1E-2"},
            {"iteration": 1, "matching_residual_decimal": "4E-3"},
        ],
        "trial_history": [
            {"update": 1, "factor": 1.0, "matching_residual_decimal": "2E-2"},
            {"update": 1, "factor": 0.5, "matching_residual_decimal": "4E-3"},
        ],
    }
    assert accepted_factors(receipt) == [0.5]

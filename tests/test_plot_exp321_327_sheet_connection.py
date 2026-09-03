from scripts.plot_exp321_327_sheet_connection import SCHEMA, signed_multiplier


def test_sheet_connection_figure_schema_is_versioned():
    assert SCHEMA == "butterfly.exp321-327-sheet-connection-figure.v1"


def test_signed_multiplier_preserves_real_sign():
    row = {"spectrum": {"products": [{"dominant_transverse_decimal": "-1.25"}]}}
    assert signed_multiplier(row) == -1.25

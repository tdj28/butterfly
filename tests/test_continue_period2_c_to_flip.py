from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from continue_period2_c_to_flip import first_real_minus_one_bracket  # noqa: E402


def _row(c: float, real: float, imag: float = 0.0) -> dict:
    return {
        "parameters": {"c": c},
        "dominant_nontrivial_multiplier": {
            "real": real,
            "imag": imag,
            "modulus": abs(complex(real, imag)),
        },
    }


def test_first_real_minus_one_bracket_selects_first_sign_change() -> None:
    rows = [_row(3.2, 0.5), _row(3.3, -0.8), _row(3.4, -1.2), _row(3.5, -1.5)]
    bracket = first_real_minus_one_bracket(rows, 1e-8)
    assert bracket is not None
    assert bracket["c"] == [3.3, 3.4]
    assert bracket["residuals"] == [0.19999999999999996, -0.19999999999999996]


def test_complex_crossing_is_not_accepted_as_real_flip() -> None:
    rows = [_row(3.2, -0.8, 0.1), _row(3.3, -1.2, 0.1)]
    assert first_real_minus_one_bracket(rows, 1e-6) is None

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.refine_jones_period1536_decimal_augmented_bracket import line_identity


def test_line_identity_ignores_tangent_sign_and_scale() -> None:
    nodes = [[Decimal("1"), Decimal("2"), Decimal("3")]]
    source_tangents = [[Decimal("1"), Decimal("0"), Decimal("0")]]
    tangents = [[Decimal("-7"), Decimal("0"), Decimal("0")]]
    identity = line_identity(nodes, source_tangents, nodes, tangents)
    assert identity["maximum_node_displacement"] == 0.0
    assert identity["minimum_tangent_line_cosine"] == 1.0
    assert identity["base_tangent_line_cosine"] == 1.0

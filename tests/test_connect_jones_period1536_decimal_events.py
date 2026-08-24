from decimal import Decimal

from scripts.connect_jones_period1536_decimal_events import SCHEMA, interpolate


def test_event_connection_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period1536-decimal-event-connection-manifest.v1"


def test_interpolate_hits_target_coordinate():
    left = {
        "a_decimal": "2",
        "period_time_decimal": "10",
        "nodes_decimal": [["0", "2", "4"]],
    }
    right = {
        "a_decimal": "0",
        "period_time_decimal": "14",
        "nodes_decimal": [["2", "4", "6"]],
    }
    nodes, period, fraction = interpolate(left, right, Decimal("1.5"))
    assert fraction == Decimal("0.25")
    assert period == Decimal("11")
    assert nodes == [[Decimal("0.5"), Decimal("2.5"), Decimal("4.5")]]

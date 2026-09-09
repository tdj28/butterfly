"""Exact arithmetic identities, root guards and partial archive preservation."""
from decimal import Decimal as D, localcontext
import pytest
from butterfly import decimal_taylor as taylor
from scripts.exp499_reference_controls import CONFIGS, SCALES, polynomial, rotation


def test_float_input_is_binary_value_not_decimal_spelling():
    assert taylor.exact(.1) == D.from_float(.1)
    assert taylor.exact(.1) != D("0.1")


def test_nonlinear_coefficients_match_exp_of_t_squared_over_two():
    with localcontext() as ctx:
        ctx.prec = 50
        q = taylor.coefficients([D(0),D(0),D(1)], polynomial(), 8)
        assert q[0] == [D(0),D(1),*[D(0)]*7]
        assert q[1][2] == D("0.5")
        assert q[2][0:5] == [D(1),D(0),D("0.5"),D(0),D("0.125")]
        assert q[2][6] == D(1)/48


def test_guarded_root_and_archive_roundtrip(tmp_path):
    raw = taylor.integrate([1,0,0], rotation(), 4, CONFIGS[0], SCALES)
    path = tmp_path/"raw.gz"
    writer = taylor.StreamArchive(path,dict(id="control"))
    for row in raw["steps"]:
        writer.step(row)
    writer.finish(raw)
    writer.close()
    header, loaded = taylor.load_stream(path)
    assert header == dict(id="control") and loaded == raw
    curve = taylor.Curve(raw)
    event = taylor.root(curve,["3.14","3.15"],0)
    assert abs(float(event["time"])-3.141592653589793) < 1e-14
    with pytest.raises(ValueError,match="derivative"):
        taylor.root(curve,["3.14","3.15"],0,direction=1)
    with pytest.raises(ValueError,match="bracket"):
        taylor.root(curve,["3.14","3.15"],10)
    with pytest.raises(ValueError,match="half-plane"):
        taylor.root(curve,["3.14","3.15"],0,gate_upper=-2)


def test_nonfinite_and_insufficient_order_rejected():
    with pytest.raises(ValueError,match="finite"):
        taylor.integrate([float("nan"),0,0],rotation(),1,CONFIGS[0],SCALES)
    with pytest.raises(ValueError,match="tail"):
        taylor.integrate([1,0,0],rotation(),1,dict(CONFIGS[0],order=3),SCALES)


def test_partial_stream_is_retained_but_not_accepted(tmp_path):
    path = tmp_path/"partial.gz"
    writer = taylor.StreamArchive(path,dict(id="control"))
    writer.step(dict(time="0"))
    writer.close()
    assert path.stat().st_size > 0
    with pytest.raises(ValueError,match="incomplete"):
        taylor.load_stream(path)
    with pytest.raises(FileExistsError):
        taylor.StreamArchive(path,dict(id="control"))


def test_nonterminating_decimal_horizon_does_not_loop():
    raw = taylor.integrate([1,0,0],rotation(),.1,CONFIGS[0],SCALES)
    assert raw["horizon"] == str(D.from_float(.1))
    assert len(raw["steps"]) == 6

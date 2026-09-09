"""Analytic controls for the decimal reference; no target trajectories."""
from decimal import Decimal as D, localcontext
import math
import time

from butterfly import decimal_taylor as taylor

CONFIGS = [dict(name="decimal-40",digits=40,order=24,step="0.02"),
           dict(name="decimal-50",digits=50,order=32,step="0.01")]
SCALES = [15.,15.,.01]
PI = D("3.141592653589793238462643383279502884197169399375105820974944592307816406286")


def rotation():
    return dict(constant=[0,0,0], linear=[[0,1,-1],[1,0,1]], quadratic=[[2,0,2,1]])


def polynomial():
    return dict(constant=[1,0,0], linear=[[1,0,1]], quadratic=[[2,0,2,1]])


def sine(value):
    # Separate scalar analytic control, not an ODE coefficient recurrence.
    with localcontext() as ctx:
        ctx.prec = 65
        term = total = value
        for n in range(1, 90):
            term *= -value*value / ((2*n)*(2*n+1))
            total += term
        return total


def controls(output):
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    start = time.monotonic()
    for config in CONFIGS:
        for kind in ("rotation", "near-tangent", "polynomial"):
            field = polynomial() if kind == "polynomial" else rotation()
            initial = [0,0,1] if kind == "polynomial" else [1,0,0]
            path = output/(config["name"]+"--"+kind+".json.gz")
            raw = taylor.run_profile(path, path.name, initial, field, 4, config, SCALES)
            _, saved = taylor.load_stream(path)
            if saved != raw:
                raise ValueError("analytic stored trajectory differs")
            curve = taylor.Curve(saved)
            if kind == "rotation":
                events = [taylor.root(curve, ["3.14","3.15"], 0)]
                with localcontext() as ctx:
                    ctx.prec = 60
                    error = max(abs(D(events[0]["time"])-PI), abs(D(events[0]["state"][0])+1))
            elif kind == "near-tangent":
                offset = D("0.99999999")
                center = math.asin(float(offset))
                boxes = [[center-1e-5,center+1e-5], [math.pi-center-1e-5,math.pi-center+1e-5]]
                events = [taylor.root(curve, box, offset, direction=direction) for box,direction in zip(boxes,[1,-1],strict=True)]
                error = max(abs(sine(D(e["time"]))-offset) for e in events)
            else:
                events = [taylor.root(curve, ["1.99","2.01"], 2, direction=1)]
                with localcontext() as ctx:
                    ctx.prec = 60
                    error = max(abs(D(events[0]["time"])-2), abs(D(events[0]["state"][2])-D(2).exp()))
            if error > D("1e-22"):
                raise ValueError("analytic decimal control failed")
            rows.append(dict(config=config["name"],kind=kind,events=events,error=str(error),
                steps=len(raw["steps"]),raw_path=path.name,passed=True))
    return dict(passed=True,profiles=rows,new_target_integrations=0,elapsed_seconds=time.monotonic()-start)

"""Analytic state, variation, shooting and complete-census controls for EXP-501."""
from decimal import Decimal as D, localcontext
from butterfly import decimal_grazing as numeric
from butterfly.decimal_taylor import load_stream
from butterfly._paired_startup import write_json
from scripts import exp500_census_analysis as census

PI = D("3.1415926535897932384626433832795028841971693993751058209749445923078164")


def case(kind):
    if kind == "rotation":
        field = dict(constant=[0,0,0],linear=[[0,1,-1],[1,0,1]],quadratic=[[2,0,2,1]])
        candidate = dict(initial_state=[1,0,1],initial_tangent=[1,0,0],seed_u="0.001",seed_time="1.56",
                         u_box=["-0.1","0.1"],time_box=["1.4","1.7"])
        offset = 1
    elif kind == "parabola":
        field = dict(constant=[1,0,0],linear=[[1,0,2]],quadratic=[[2,0,2,1]])
        candidate = dict(initial_state=[-1,1,1],initial_tangent=[0,1,0],seed_u="0.001",seed_time="0.99",
                         u_box=["-0.1","0.1"],time_box=["0.9","1.1"])
        offset = 0
    else:
        raise ValueError("unknown analytic control")
    return candidate,numeric.augment(field),offset


def identity(kind,shooting):
    with localcontext() as ctx:
        ctx.prec = 70
        if shooting["status"] != "qualified":
            raise ValueError("analytic grazing did not qualify")
        r = shooting["trace"][-1]
        expected_time = PI/2 if kind == "rotation" else D(1)
        q = [D(0),D(1),D(1).exp()] if kind == "rotation" else [D(0),D(0),D("-0.5").exp()]
        w = [D(0),D(1),D(1).exp()] if kind == "rotation" else [D(0),D(1),D(0)]
        error = max(abs(D(r["u"])),abs(D(r["time"])-expected_time),
                    *[abs(D(a)-b) for a,b in zip(r["state"]+r["tangent"],q+w,strict=True)])
        if error > D("1e-22"):
            raise ValueError("analytic state/tangent/root identity failed")
        return str(error)


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    rows = []
    for config in numeric.CONFIGS:
        for kind in ("rotation","parabola"):
            c,field,offset = case(kind)
            label = config["name"]+"--"+kind
            def step(iteration,initial,end,f,configuration):
                name = label+f"--iteration-{iteration}.json.gz"
                raw = numeric.run_profile(output/name,initial,f,end,configuration)
                if load_stream(output/name)[1] != raw:
                    raise ValueError("analytic archive round trip differs")
                return raw,name
            shooting,_ = numeric.shooting(c,field,offset,config,step,minimum="0.5")
            error = identity(kind,shooting)
            # Independent ordinary-crossing identity on a full analytic curve.
            initial = [str(v) for v in c["initial_state"]+c["initial_tangent"]]
            horizon = "4" if kind == "rotation" else "2"
            name = label+"--census.json.gz"
            raw = numeric.run_profile(output/name,initial,field,horizon,config)
            section = dict(offset=0 if kind == "rotation" else "0.25",gate_upper=10)
            projected = dict(raw,steps=[dict(r,coefficients=r["coefficients"][:3]) for r in raw["steps"]],
                field=dict(constant=field["constant"][:3],linear=[v for v in field["linear"] if v[0] < 3],
                           quadratic=[v for v in field["quadratic"] if v[0] < 3]),scales=numeric.SCALES)
            result,certificates = census.profile(projected,section)
            replay,_ = census.profile(projected,section,certificate=certificates)
            expected_times = [D(0),PI] if kind == "rotation" else [D("0.5"),D("1.5")]
            if (result != replay or not result["complete"] or len(result["events"]) != 2
                    or sum(e["accepted"] for e in result["events"]) != 1
                    or any(abs(D(e["time"])-t) > D("1e-22") for e,t in zip(result["events"],expected_times,strict=True))):
                raise ValueError("analytic complete census identity failed")
            write_json(output/(label+"-certificates.json"),certificates)
            rows.append(dict(kind=kind,configuration=config["name"],shooting=shooting,error=error,
                             census=result,census_raw=name,passed=True))
    return dict(passed=True,profiles=rows,new_target_integrations=0)

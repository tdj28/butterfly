"""Complete stored-polynomial census and section classification; no IVPs."""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F

from butterfly import polynomial_census as roots


def exact(value):
    if isinstance(value,float): return F.from_float(value)
    # Decimal.as_integer_ratio handles 0E-999999 without constructing 10**999999.
    if isinstance(value,str) and "/" not in value: return F(D(value))
    return F(value)


def decimal(value):
    with localcontext() as ctx:
        ctx.prec = 70
        return str(D(value.numerator)/D(value.denominator))


def add(a,b): return a[0]+b[0],a[1]+b[1]


def multiply(a,b): return roots.interval_product(a,b)


def square(a):
    values = a[0]*a[0],a[1]*a[1]
    return (F(0) if a[0] <= 0 <= a[1] else min(values)),max(values)


def sign(a):
    return 1 if a[0] > 0 else (-1 if a[1] < 0 else 0)


def field_interval(q,field):
    f = [(exact(v),exact(v)) for v in field["constant"]]
    for i,j,v in field["linear"]:
        f[i] = add(f[i],multiply(q[j],(exact(v),exact(v))))
    for i,j,k,v in field["quadratic"]:
        f[i] = add(f[i],multiply(multiply(q[j],q[k]),(exact(v),exact(v))))
    return f


def classify(poly,time,width,box,field,section):
    left,right = [F(v)*width for v in box]
    q = [roots.interval_value(p,left,right) for p in poly]
    mid = (left+right)/2
    state = [roots.evaluate(p,mid) for p in poly]
    dy = roots.interval_value([i*v for i,v in enumerate(poly[1])][1:],left,right)
    velocity = field_interval(q,field)
    direction = sign(dy)
    normal = square(velocity[1])
    norm = [square(v) for v in velocity]
    norm_upper = sum(v[1] for v in norm)
    angle_ok = norm_upper > 0 and normal[0] >= F("1e-14")*norm_upper
    gate = exact(section["gate_upper"])
    membership = "inside" if q[0][1] < gate else ("outside" if q[0][0] > gate else "unresolved")
    absolute = [time+left,time+right]
    cut = F("1e-8")
    after = "after" if absolute[0] > cut else ("initial" if absolute[1] <= cut else "unresolved")
    qualified = (direction != 0 and direction == sign(velocity[1]) and angle_ok
                 and membership != "unresolved" and after != "unresolved")
    accepted = qualified and direction == -1 and membership == "inside" and after == "after"
    return dict(time=decimal(time+mid),time_box=[str(v) for v in absolute],
        state=[decimal(v) for v in state],direction=direction,half_plane=membership,time_class=after,
        classification_qualified=qualified,accepted=accepted,
        angle_lower=float((normal[0]/norm_upper))**.5 if norm_upper > 0 else 0.,
        polynomial_direction=sign(dy),field_direction=sign(velocity[1]),
        polynomial_derivative_bounds=[decimal(v) for v in dy],
        state_interval_width=[decimal(hi-lo) for lo,hi in q])


def profile(raw,section,*,certificate=None,before_segment=None):
    """Producer or certificate replay through the same explicit classifier."""
    steps = raw["steps"]
    if not steps: raise ValueError("empty stored trajectory")
    times = [F(r["time"]) for r in steps]+[F(raw["horizon"])]
    if times[0] != 0 or any(a >= b for a,b in zip(times,times[1:])):
        raise ValueError("stored domain is not ordered from zero")
    if certificate is not None and len(certificate) != len(steps):
        raise ValueError("complete segment certificate required")
    events, unresolved, joins, proofs = [],[],[],[]
    previous, maximum_jump = None,F(0)
    tolerance = F(10)**(-raw["config"]["digits"]+8)
    for index,step in enumerate(steps):
        if before_segment is not None: before_segment()
        time,width = times[index],times[index+1]-times[index]
        if abs(width-F(step["step"])) > tolerance:
            raise ValueError("stored step/domain discrepancy")
        poly = [[exact(v) for v in p] for p in step["coefficients"]]
        if len(poly) != 3 or any(len(p) != raw["config"]["order"]+1 for p in poly):
            raise ValueError("complete coefficient matrix required")
        if previous is not None:
            jump = max(abs(a-p[0])/exact(s) for a,p,s in zip(previous,poly,raw["scales"],strict=True))
            maximum_jump = max(jump,maximum_jump)
            left = previous[1]-exact(section["offset"])
            right = poly[1][0]-exact(section["offset"])
            compatible = (left > 0 and right > 0) or (left < 0 and right < 0) or left == right == 0
            if not compatible or jump > F("1e-20"):
                joins.append(dict(index=index,time=str(time),scaled_jump=decimal(jump),plane_sign_compatible=compatible))
        previous = [roots.evaluate(p,width) for p in poly]
        power = roots.scaled_power(poly[1],width,exact(section["offset"]))
        if certificate is not None:
            # Independent scalar check of the positive scaling/plane transform.
            expected, factor = [],F(1)
            for coefficient in poly[1]:
                expected.append(coefficient*factor)
                factor *= width
            expected[0] -= exact(section["offset"])
            pivot = next((i for i,v in enumerate(expected) if v),None)
            if pivot is None:
                if any(power): raise ValueError("zero polynomial transform differs")
            else:
                ratio = F(power[pivot])/expected[pivot]
                if ratio <= 0 or any(F(a) != ratio*b for a,b in zip(power,expected,strict=True)):
                    raise ValueError("exact plane/power transform differs")
        proof = roots.isolate(power,width) if certificate is None else certificate[index]
        proofs.append(proof)
        if certificate is None:
            boxes = [leaf["root"] for leaf in proof["leaves"] if leaf["kind"] == "single"]
            boxes += [[v,v] for v in proof["points"]]
            missing = [list(map(str,roots.path_interval(leaf["path"]))) for leaf in proof["leaves"] if leaf["kind"] == "unresolved"]
        else:
            checked = roots.verify(power,width,proof)
            boxes,missing = checked["roots"],checked["unresolved"]
        unresolved.extend(dict(segment=index,box=[str(time+F(v)*width) for v in box]) for box in missing)
        for box in sorted(boxes,key=lambda r:F(r[0])):
            event = classify(poly,time,width,box,raw["field"],section)
            event["segments"] = [index]
            if events and event["time_box"][0] == event["time_box"][1] == events[-1]["time_box"][0] == events[-1]["time_box"][1]:
                old = events[-1]
                keys = ("direction","half_plane","time_class","classification_qualified","accepted")
                if any(old[k] != event[k] for k in keys):
                    joins.append(dict(index=index,time=event["time"],duplicate_classification_agrees=False))
                old["segments"].append(index)
                old.setdefault("join_witnesses",[]).append(event)
            else: events.append(event)
    complete = not unresolved and not joins and all(e["classification_qualified"] for e in events)
    return dict(events=events,unresolved=unresolved,join_failures=joins,maximum_scaled_join_jump=decimal(maximum_jump),
        complete=complete,segments=len(steps),polynomial_census_only=True),proofs


def compare_events(a,b,scales):
    rows = []
    equal_count = len(a) == len(b)
    if equal_count:
        for index,(x,y) in enumerate(zip(a,b,strict=True)):
            dt = abs(exact(x["time"])-exact(y["time"]))
            dq = max(abs(exact(u)-exact(v))/exact(s) for u,v,s in zip(x["state"],y["state"],scales,strict=True))
            rows.append(dict(index=index,time=float(dt),state=float(dq),passed=dt <= F("1e-12") and dq <= F("1e-9")))
    return dict(count_a=len(a),count_b=len(b),equal_count=equal_count,comparisons=rows,
        passed=equal_count and all(r["passed"] for r in rows))


def compare(profiles,parent,scales):
    if len(profiles) != 2 or [p["configuration"] for p in profiles] != ["decimal-40","decimal-50"]:
        raise ValueError("both ordered configurations required")
    a,b = [p["analysis"]["events"] for p in profiles]
    paired = compare_events(a,b,scales)
    keys = ("direction","half_plane","time_class","classification_qualified","accepted")
    categories = len(a) == len(b) and all(all(x[k] == y[k] for k in keys) for x,y in zip(a,b,strict=True))
    nominated = []
    for profile,old in zip(profiles,parent["profiles"],strict=True):
        if profile["configuration"] != old["configuration"]: raise ValueError("parent configuration identity")
        accepted = [e for e in profile["analysis"]["events"] if e["accepted"]]
        nominated.append(dict(configuration=profile["configuration"],**compare_events(accepted,old["events"],scales)))
    return dict(paired=paired,classifications_agree=categories,nominated=nominated,
        qualified=all(p["analysis"]["complete"] for p in profiles) and paired["passed"] and categories
                  and all(r["passed"] and r["count_a"] > 0 for r in nominated),
        repairs_exp498=False,symbolic_chains_verified=False,exact_flow_all_roots_proved=False)

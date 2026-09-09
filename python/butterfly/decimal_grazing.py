"""EXP-501 augmented Taylor/Newton pilot; numerical, not validated integration."""
from decimal import Decimal as D, localcontext

from .decimal_taylor import exact, horner, StreamArchive, field_value

CONFIGS = [dict(name="decimal-40", digits=40, order=24, step="0.02"),
           dict(name="decimal-50", digits=50, order=32, step="0.01")]
SCALES = [15., 15., .01]


def augment(field):
    """Differentiate a three-dimensional sparse quadratic field exactly."""
    if len(field["constant"]) != 3:
        raise ValueError("three-dimensional base field required")
    linear = [list(v) for v in field["linear"]]
    quadratic = [list(v) for v in field["quadratic"]]
    linear += [[i+3, j+3, v] for i, j, v in field["linear"]]
    for i, j, k, v in field["quadratic"]:
        quadratic += [[i+3, j+3, k, v], [i+3, j, k+3, v]]
    return dict(constant=field["constant"]+[0, 0, 0], linear=linear, quadratic=quadratic)


def coefficients(state, field, order):
    q = [[exact(v)] for v in state]
    for n in range(order):
        rhs = [exact(v) if n == 0 else D(0) for v in field["constant"]]
        for i, j, v in field["linear"]:
            rhs[i] += exact(v)*q[j][n]
        for i, j, k, v in field["quadratic"]:
            rhs[i] += exact(v)*sum(q[j][r]*q[k][n-r] for r in range(n+1))
        for i in range(len(q)):
            q[i].append(rhs[i]/(n+1))
    return q


def integrate(initial, field, horizon, config, *, retain_step=None, before_step=None):
    with localcontext() as ctx:
        ctx.prec = config["digits"]
        q = [exact(v) for v in initial]
        end, step, t = exact(horizon), D(config["step"]), D(0)
        if (len(q) != 6 or len(field["constant"]) != 6 or config not in CONFIGS
                or not end.is_finite() or end <= 0
                or not all(v.is_finite() for v in q)):
            raise ValueError("finite six-dimensional configured input required")
        rows, maxima = [], [D(0), D(0)]
        while t < end:
            if before_step is not None:
                before_step()
            next_time = min(t+step, end)
            h = next_time-t
            if h <= 0:
                raise ValueError("nonadvancing Taylor step")
            poly = coefficients(q, field, config["order"])
            tails = [max(sum(abs(poly[i][n]*h**n) for n in range(config["order"]-2, config["order"]+1))
                         /exact(SCALES[i % 3]) for i in range(start, start+3)) for start in (0, 3)]
            if any(not v.is_finite() or v > cap for v, cap in zip(tails, [D("1e-20"), D("1e-16")], strict=True)):
                raise ValueError("state/tangent tail diagnostic; no fallback")
            maxima = [max(a, b) for a, b in zip(maxima, tails, strict=True)]
            row = dict(time=str(t), step=str(h), coefficients=[[str(v) for v in p] for p in poly])
            rows.append(row)
            if retain_step is not None:
                retain_step(row)
            q = [horner(p, h) for p in poly]
            if any(not v.is_finite() or abs(v) > (D("1e4") if i < 3 else D("1e12")) for i, v in enumerate(q)):
                raise ValueError("state/tangent magnitude guard")
            t = next_time
        return dict(config=config, initial=[str(exact(v)) for v in initial], field=field,
                    horizon=str(end), steps=rows, final=[str(v) for v in q],
                    maximum_tails=[str(v) for v in maxima], rigorous_enclosure=False)


def run_profile(path, initial, field, horizon, config, before_step=None):
    metadata = dict(initial=initial, field=field, horizon=horizon, config=config)
    archive = StreamArchive(path, metadata)
    try:
        raw = integrate(initial, field, horizon, config, retain_step=archive.step, before_step=before_step)
        archive.finish(raw)
        return raw
    finally:
        archive.close()


def measure(final, field, offset):
    q = [exact(v) for v in final]
    f = field_value(q, field)
    jacrow = [D(0)]*3
    for i, j, v in field["linear"]:
        if i == 1:
            jacrow[j] += exact(v)
    for i, j, k, v in field["quadratic"]:
        if i == 1:
            jacrow[j] += exact(v)*q[k]
            jacrow[k] += exact(v)*q[j]
    matrix = [[q[4], f[1]], [f[4], sum(jacrow[i]*f[i] for i in range(3))]]
    return [q[1]-exact(offset), f[1]], matrix


def newton_delta(residual, matrix):
    (a, b), (c, d) = matrix
    determinant = a*d-b*c
    if not determinant.is_finite() or determinant == 0:
        raise ValueError("singular grazing system")
    r, s = residual
    return [(d*r-b*s)/determinant, (a*s-c*r)/determinant]


def initial_at(candidate, u):
    base = [exact(v) for v in candidate["initial_state"]]
    tangent = [exact(v) for v in candidate["initial_tangent"]]
    return [str(q+u*v) for q, v in zip(base, tangent, strict=True)]+[str(v) for v in tangent]


def shooting(candidate, field, offset, config, integrate_step, minimum="1"):
    """Retainer callback owns raw paths; all eight attempts remain visible."""
    with localcontext() as ctx:
        ctx.prec = config["digits"]
        u, end = exact(candidate["seed_u"]), exact(candidate["seed_time"])
        trace, raw = [], None
        for iteration in range(8):
            if not (exact(candidate["u_box"][0]) <= u <= exact(candidate["u_box"][1])
                    and exact(candidate["time_box"][0]) <= end <= exact(candidate["time_box"][1])):
                return dict(status="box-exit", trace=trace, proposed_u=str(u), proposed_time=str(end)), raw
            initial = initial_at(candidate, u)
            raw, path = integrate_step(iteration, initial, str(end), field, config)
            residual, matrix = measure(raw["final"], field, offset)
            converged = all(abs(v) <= D("1e-24") for v in residual)
            nondegenerate = abs(matrix[0][0]) >= D(minimum) and abs(matrix[1][1]) >= D(minimum)
            item = dict(iteration=iteration, u=str(u), time=str(end), initial=initial,
                        state=raw["final"][:3], tangent=raw["final"][3:], raw_path=path,
                        residual=[str(v) for v in residual], jacobian=[[str(v) for v in row] for row in matrix],
                        converged=converged, nondegenerate=nondegenerate)
            trace.append(item)
            if converged:
                return dict(status="qualified" if nondegenerate else "degenerate", trace=trace), raw
            try:
                delta = newton_delta(residual, matrix)
            except ValueError:
                return dict(status="singular", trace=trace), raw
            item["delta"] = [str(v) for v in delta]
            u, end = u-delta[0], end-delta[1]
        return dict(status="iteration-limit", trace=trace), raw


def prefix_state(raw, end):
    """Exact same stored state polynomials, truncated before deliberate grazing."""
    with localcontext() as ctx:
        ctx.prec = raw["config"]["digits"]
        end = exact(end)
        if not 0 < end < D(raw["horizon"]):
            raise ValueError("strict interior prefix required")
        rows = []
        for row in raw["steps"]:
            t = D(row["time"])
            if t >= end:
                break
            rows.append(dict(time=row["time"], step=str(min(D(row["step"]), end-t)),
                             coefficients=row["coefficients"][:3]))
        field = raw["field"]
        return dict(config=raw["config"], initial=raw["initial"][:3], horizon=str(end), steps=rows,
                    field=dict(constant=field["constant"][:3], linear=[v for v in field["linear"] if v[0] < 3],
                               quadratic=[v for v in field["quadratic"] if v[0] < 3]), scales=SCALES)

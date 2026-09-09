"""Decimal Taylor reference for sparse quadratic ODEs; no rigorous enclosure."""
from bisect import bisect_right
from decimal import Decimal, localcontext
import gzip
import json

D = Decimal


def exact(value):
    return D.from_float(value) if isinstance(value, float) else D(value)


def coefficients(state, field, order):
    q = [[v] for v in state]
    for n in range(order):
        rhs = [exact(v) if n == 0 else D(0) for v in field["constant"]]
        for i, j, value in field["linear"]:
            rhs[i] += exact(value) * q[j][n]
        for i, j, k, value in field["quadratic"]:
            rhs[i] += exact(value) * sum(q[j][r] * q[k][n-r] for r in range(n+1))
        for i in range(3):
            q[i].append(rhs[i] / (n+1))
    return q


def horner(poly, time):
    value = D(0)
    for coefficient in reversed(poly):
        value = value * time + coefficient
    return value


def integrate(initial, field, horizon, config, scales, before_step=None, retain_step=None):
    with localcontext() as ctx:
        ctx.prec = config["digits"]
        q = [exact(v) for v in initial]
        end, step, t = exact(horizon), D(config["step"]), D(0)
        if (len(q) != 3 or not all(v.is_finite() for v in q)
                or not end.is_finite() or end <= 0 or step <= 0 or config["order"] < 3):
            raise ValueError("finite bounded Taylor input required")
        rows = []
        maximum_tail = D(0)
        while t < end:
            if before_step is not None:
                before_step()
            next_time = min(t+step, end)
            h = next_time-t
            poly = coefficients(q, field, config["order"])
            tail = max(sum(abs(poly[i][n]*h**n) for n in range(config["order"]-2, config["order"]+1))
                       / exact(scales[i]) for i in range(3))
            maximum_tail = max(maximum_tail, tail)
            if not tail.is_finite() or tail > D("1e-20"):
                raise ValueError("Taylor tail diagnostic failed; no step fallback")
            rows.append(dict(time=str(t), step=str(h), coefficients=[[str(v) for v in p] for p in poly]))
            if retain_step is not None:
                retain_step(rows[-1])
            q = [horner(p, h) for p in poly]
            if not all(v.is_finite() and abs(v) <= D("1e4") for v in q):
                raise ValueError("Taylor state guard")
            t = next_time
        return dict(config=config, initial=[str(exact(v)) for v in initial],
            field=field, horizon=str(end), scales=scales, steps=rows,
            final=[str(v) for v in q], maximum_tail=str(maximum_tail), rigorous_enclosure=False)


def save(path, raw):
    with path.open("xb") as output:
        with gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=0) as stream:
            stream.write((json.dumps(raw, separators=(",", ":"), allow_nan=False)+"\n").encode())


def load(path):
    with gzip.open(path, "rt") as stream:
        return json.load(stream)


class StreamArchive:
    """Append full coefficient steps immediately; partial runs stay readable."""
    def __init__(self, path, metadata):
        self.file = path.open("xb")
        self.stream = gzip.GzipFile(filename="", fileobj=self.file, mode="wb", mtime=0)
        self.emit(dict(header=metadata))

    def emit(self, row):
        self.stream.write((json.dumps(row, separators=(",", ":"), allow_nan=False)+"\n").encode())

    def step(self, row):
        self.emit(dict(step_record=row))

    def finish(self, raw):
        self.emit(dict(footer={k:v for k,v in raw.items() if k != "steps"}))

    def close(self):
        self.stream.close()
        self.file.close()


def load_stream(path):
    with gzip.open(path, "rt") as stream:
        rows = [json.loads(line) for line in stream]
    if not rows or set(rows[0]) != {"header"} or set(rows[-1]) != {"footer"}:
        raise ValueError("incomplete coefficient archive")
    if any(set(row) != {"step_record"} for row in rows[1:-1]):
        raise ValueError("coefficient archive row schema")
    return rows[0]["header"], dict(rows[-1]["footer"], steps=[r["step_record"] for r in rows[1:-1]])


def run_profile(path, label, initial, field, horizon, config, scales, before_step=None):
    archive = StreamArchive(path, dict(label=label, initial=initial, field=field,
        horizon=horizon, config=config, scales=scales))
    try:
        raw = integrate(initial, field, horizon, config, scales,
                        before_step=before_step, retain_step=archive.step)
        archive.finish(raw)
        return raw
    finally:
        archive.close()


class Curve:
    def __init__(self, raw):
        self.raw = raw
        self.times = [D(r["time"]) for r in raw["steps"]]
        self.end = D(raw["horizon"])
        self.poly = [[[D(v) for v in p] for p in r["coefficients"]] for r in raw["steps"]]

    def index(self, time):
        if not D(0) <= time <= self.end:
            raise ValueError("query outside retained trajectory")
        return max(0, bisect_right(self.times, time)-1)

    def value(self, time):
        i = self.index(time)
        return [horner(p, time-self.times[i]) for p in self.poly[i]]

    def derivative_bounds(self, left, right, axis):
        # Numerical interval Horner on the retained polynomial, not the flow.
        low, high = [], []
        for i in range(self.index(left), self.index(right)+1):
            a, b = max(left, self.times[i])-self.times[i], min(right, self.times[i]+D(self.raw["steps"][i]["step"]))-self.times[i]
            lo = hi = D(0)
            derivative = [n*v for n, v in enumerate(self.poly[i][axis])][1:]
            for c in reversed(derivative):
                products = [lo*a, lo*b, hi*a, hi*b]
                lo, hi = min(products)+c, max(products)+c
            low.append(lo)
            high.append(hi)
        return min(low), max(high)


def root(curve, box, offset, direction=-1, gate_upper=None):
    with localcontext() as ctx:
        ctx.prec = curve.raw["config"]["digits"]
        left, right = map(exact, box)
        offset = exact(offset)
        if not left < right:
            raise ValueError("ordered root box required")
        bounds = curve.derivative_bounds(left, right, 1)
        if not ((direction == -1 and bounds[1] < 0) or (direction == 1 and bounds[0] > 0)):
            raise ValueError("root polynomial derivative sign not qualified")
        a, b = curve.value(left)[1]-offset, curve.value(right)[1]-offset
        if a*b > 0:
            raise ValueError("root not bracketed")
        if a == 0:
            right = left
        elif b == 0:
            left = right
        else:
            for _ in range(100):
                if right-left <= D("1e-25"):
                    break
                middle = (left+right)/2
                m = curve.value(middle)[1]-offset
                if m == 0:
                    left = right = middle
                    break
                if a*m < 0:
                    right = middle
                else:
                    left, a = middle, m
        if right-left > D("1e-25"):
            raise ValueError("root iteration limit")
        time = (left+right)/2
        q = curve.value(time)
        if gate_upper is not None and not q[0] < exact(gate_upper):
            raise ValueError("root half-plane gate")
        f = field_value(q, curve.raw["field"])
        if direction*f[1] <= 0:
            raise ValueError("root vector-field direction")
        angle = abs(f[1]) / sum(v*v for v in f).sqrt()
        if angle < D("1e-7"):
            raise ValueError("root crossing angle")
        return dict(time=str(time), state=[str(v) for v in q],
            residual=str(q[1]-offset), angle=str(angle),
            polynomial_derivative_bounds=[str(v) for v in bounds],
            final_box=[str(left), str(right)])


def field_value(q, field):
    value = [exact(v) for v in field["constant"]]
    for i, j, v in field["linear"]:
        value[i] += exact(v)*q[j]
    for i, j, k, v in field["quadratic"]:
        value[i] += exact(v)*q[j]*q[k]
    return value

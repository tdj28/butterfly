"""Exact rational polynomial root certificates, not enclosures of an ODE flow."""
from fractions import Fraction as F
from functools import reduce
from math import comb, gcd, lcm


def integers(values):
    values = [F(v) for v in values]
    denominator = lcm(*(v.denominator for v in values))
    raw = [v.numerator*(denominator//v.denominator) for v in values]
    divisor = reduce(gcd, raw, 0) or 1
    return [v//divisor for v in raw]


def scaled_power(coefficients, width, offset=0):
    h = F(width)
    if h <= 0 or not coefficients:
        raise ValueError("nonempty polynomial and positive width required")
    q = [F(v)*h**i for i,v in enumerate(coefficients)]
    q[0] -= F(offset)
    return integers(q)


def bernstein(power):
    n = len(power)-1
    denominator = lcm(*(comb(n,i) for i in range(n+1)))
    return [sum(power[i]*comb(k,i)*(denominator//comb(n,i)) for i in range(k+1)) for k in range(n+1)]


def split(coefficients):
    """Two exact half-interval Bernstein vectors, each scaled by positive 2**n."""
    n = len(coefficients)-1
    row, left, right = list(coefficients), [], []
    for depth in range(n+1):
        left.append(row[0] << (n-depth))
        right.append(row[-1] << (n-depth))
        row = [a+b for a,b in zip(row,row[1:])]
    return left, right[::-1]


def variations(values):
    signs = [(v > 0)-(v < 0) for v in values if v]
    return sum(a != b for a,b in zip(signs,signs[1:]))


def evaluate(power, point):
    value = F(0)
    for c in reversed(power): value = value*point+c
    return value


def interval_product(a,b):
    values = [x*y for x in a for y in b]
    return min(values),max(values)


def interval_value(power,left,right):
    value = (F(0),F(0))
    for c in reversed(power):
        lo,hi = interval_product(value,(left,right))
        value = lo+c,hi+c
    return value


def isolate(power,width,*,time_width=F("1e-25"),max_depth=160,max_nodes=2048,max_refinements=256):
    """Cover [0,1] with open-interval count certificates plus exact point roots."""
    width = F(width)
    if width <= 0 or time_width <= 0 or min(max_depth,max_nodes,max_refinements) < 1:
        raise ValueError("positive isolation bounds required")
    if not power or any(type(v) is not int for v in power):
        raise ValueError("integer power vector required")
    if abs(power[0]) > sum(abs(v) for v in power[1:]):
        return dict(leaves=[dict(path="",kind="dominance")],points=[],nodes=1)
    initial = bernstein(power)
    points = {F(v) for v,c in ((0,initial[0]),(1,initial[-1])) if c == 0}
    pending = [("",initial,F(0),F(1))]
    leaves, nodes = [],0
    while pending:
        path,b,left,right = pending.pop()
        nodes += 1
        v = variations(b)
        if not any(b):
            leaves.append(dict(path=path,kind="unresolved",reason="identically-zero"))
        elif v == 0:
            leaves.append(dict(path=path,kind="empty",variations=0))
        elif v == 1:
            lo,hi,q = left,right,b
            root = None
            for _ in range(max_refinements):
                if (hi-lo)*width <= time_width and q[0]*q[-1] < 0:
                    root = [str(lo),str(hi)]
                    break
                a,c = split(q)
                mid = (lo+hi)/2
                if a[-1] == 0:
                    root = [str(mid),str(mid)]
                    break
                va,vc = variations(a),variations(c)
                if va+vc != 1: raise ValueError("single-root subdivision conservation")
                if va == 1: hi,q = mid,a
                else: lo,q = mid,c
            if root is None:
                leaves.append(dict(path=path,kind="unresolved",reason="refinement-limit"))
            else:
                leaves.append(dict(path=path,kind="single",variations=1,root=root))
        elif len(path) >= max_depth or nodes+len(pending)+2 > max_nodes:
            leaves.append(dict(path=path,kind="unresolved",reason="search-limit",variations=v))
        else:
            a,c = split(b)
            middle = (left+right)/2
            if a[-1] == 0: points.add(middle)
            pending.extend([(path+"R",c,middle,right),(path+"L",a,left,middle)])
    # Identically zero intervals are represented as unresolved, not two roots.
    if not any(power): points.clear()
    return dict(leaves=leaves,points=[str(v) for v in sorted(points)],nodes=nodes)


def path_interval(path):
    left,right = F(0),F(1)
    for character in path:
        mid = (left+right)/2
        if character == "L": right = mid
        elif character == "R": left = mid
        else: raise ValueError("nonbinary certificate path")
    return left,right


def direct_bernstein(power,left,right):
    """Verifier route: direct affine power expansion, never de Casteljau."""
    n = len(power)-1
    h = right-left
    translated = [sum(F(power[j])*comb(j,i)*left**(j-i)*h**i for j in range(i,n+1)) for i in range(n+1)]
    return [sum(translated[i]*F(comb(k,i),comb(n,i)) for i in range(k+1)) for k in range(n+1)]


def verify(power,width,certificate,*,time_width=F("1e-25")):
    """Verify coverage/counts independently from the producer's search choices."""
    leaves = certificate["leaves"]
    intervals = sorted((path_interval(r["path"]),r) for r in leaves)
    if (not intervals or intervals[0][0][0] != 0 or intervals[-1][0][1] != 1
            or any(a[0][1] != b[0][0] for a,b in zip(intervals,intervals[1:]))):
        raise ValueError("certificate does not partition complete segment")
    roots,unresolved = [],[]
    boundaries = {x for (lo,hi),_ in intervals for x in (lo,hi)}
    points = {F(v) for v in certificate["points"]}
    expected_points = {x for x in boundaries if evaluate(power,x) == 0} if any(power) else set()
    if len(points) != len(certificate["points"]) or points != expected_points:
        raise ValueError("missing or invented exact boundary roots")
    for (left,right),leaf in intervals:
        kind = leaf["kind"]
        if kind == "dominance":
            if leaf["path"] or not abs(power[0]) > sum(abs(v) for v in power[1:]):
                raise ValueError("false root-free dominance certificate")
        elif kind == "unresolved":
            unresolved.append([str(left),str(right)])
        else:
            b = direct_bernstein(power,left,right)
            signs = [1 if x > 0 else -1 for x in b if x]
            count = sum(signs[i] != signs[i-1] for i in range(1,len(signs)))
            if not any(b) or count != leaf["variations"]:
                raise ValueError("direct Bernstein count differs")
            if kind == "empty":
                if count != 0: raise ValueError("false empty leaf")
            elif kind == "single":
                lo,hi = map(F,leaf["root"])
                if not (count == 1 and left <= lo <= hi <= right and (hi-lo)*F(width) <= time_width):
                    raise ValueError("single root not isolated strictly inside leaf")
                a,c = evaluate(power,lo),evaluate(power,hi)
                if not ((left < lo == hi < right and a == 0) or (lo < hi and a*c < 0)):
                    raise ValueError("root bracket not verified")
                roots.append([str(lo),str(hi)])
            else: raise ValueError("unknown certificate kind")
    roots += [[str(x),str(x)] for x in points]
    roots.sort(key=lambda row:F(row[0]))
    if any(F(a[1]) >= F(b[0]) for a,b in zip(roots,roots[1:])):
        raise ValueError("root intervals not disjoint")
    return dict(roots=roots,unresolved=unresolved,complete=not unresolved)

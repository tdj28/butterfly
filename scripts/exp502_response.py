"""Bounded two-residual response experiment; no integrations or fitting retries."""
import itertools
import math

import numpy as np


AXES = ("a", "c")
INCREMENTS = (.0001, .002)
SCALES = (1., .5)


def stencil(anchor):
    rows = []
    for axis, h in zip(AXES, INCREMENTS, strict=True):
        for scale in SCALES:
            for sign in (-1, 1):
                parameters = dict(anchor)
                parameters[axis] += sign*scale*h
                rows.append(dict(id=f"{axis}-{scale:g}-{sign:+d}", axis=axis,
                                 scale=scale, sign=sign, parameters=parameters))
    return rows


def correspondence(cycle, reference):
    rows = []
    if cycle["status"] == "qualified":
        for profile, old in zip(cycle["profiles"], reference["profiles"], strict=True):
            if profile["method"] != old["method"]:
                raise ValueError("cycle method order")
            for w, before in zip(profile["metric"]["windows"], old["metric"]["windows"], strict=True):
                if w["phase"] != before["phase"]:
                    raise ValueError("cycle window order")
                q = np.asarray(w["event_states"]["historical"])
                oldq = np.asarray(before["event_states"]["historical"])
                if q.shape != (6, 3) or oldq.shape != (6, 3):
                    raise ValueError("six three-dimensional events required")
                errors = [float(np.max(np.abs((np.roll(q, k, axis=0)-oldq)/[15., 15., .01]))) for k in range(6)]
                margin = min(errors[1:])-errors[0]
                rows.append(dict(method=profile["method"], phase=w["phase"], shift_errors=errors,
                    identity_margin=margin, passed=bool(errors[0] <= .1 and margin > 1e-4)))
    return dict(passed=len(rows) == 4 and all(r["passed"] for r in rows), rows=rows)


def vectors(contact, boundaries):
    """Shared cycle/phase cross-product, explicitly not independent samples."""
    result = []
    if contact is None:
        return result
    for fold, boundary in itertools.product(contact["rows"], boundaries):
        for configuration in ("decimal-40", "decimal-50"):
            for f in fold["variants"]:
                matches = [v for v in boundary["comparison"]["comparisons"]
                    if v["configuration"] == configuration and v["method"] == f["method"]
                    and v["phase"] == f["phase"] and v["index"] == 1]
                if len(matches) != 1:
                    continue
                result.append(dict(key=[fold["id"], boundary["id"], configuration, f["method"], f["phase"]],
                    value=[f["signed_residual"], -float(matches[0]["x_residual"])/15.]))
    return result


def response(points, base, anchor):
    specs = stencil(anchor)
    if len(points) != 8 or [r["spec"] for r in points] != specs:
        raise ValueError("complete fixed stencil required")
    keys = [r["key"] for r in base]
    if len(keys) != 256 or len({tuple(k) for k in keys}) != 256:
        raise ValueError("complete distinct anchor matrix required")
    if any(not r["qualified"] or [v["key"] for v in r["vectors"]] != keys for r in points):
        return dict(qualified=False, reason="missing or unqualified stencil matrix", matrices=[], proposal=None)
    lookup = {(r["spec"]["axis"], r["spec"]["scale"], r["spec"]["sign"]): r for r in points}
    rows, signs = [], set()
    for index, key in enumerate(keys):
        matrices, conditions, determinants = [], [], []
        for scale in SCALES:
            columns = []
            for axis, h in zip(AXES, INCREMENTS, strict=True):
                minus, plus = [lookup[axis, scale, sign] for sign in (-1, 1)]
                spacing = plus["spec"]["parameters"][axis]-minus["spec"]["parameters"][axis]
                columns.append((np.asarray(plus["vectors"][index]["value"])-minus["vectors"][index]["value"])*h/spacing)
            matrix = np.asarray(columns).T
            if not np.isfinite(matrix).all():
                return dict(qualified=False, reason="nonfinite response", matrices=rows, proposal=None)
            determinant = float(np.linalg.det(matrix))
            condition = float(np.linalg.cond(matrix))
            signs.add(int(np.sign(determinant)))
            matrices.append(matrix.tolist())
            determinants.append(determinant)
            conditions.append(condition if math.isfinite(condition) else None)
        coarse, fine = map(np.asarray, matrices)
        disagreement = float(np.linalg.norm(fine-coarse)/max(np.linalg.norm(fine), 1e-12))
        good = all(v is not None and v <= 1e4 for v in conditions) and all(v != 0 for v in determinants) and disagreement <= .05
        rows.append(dict(key=key, matrices=matrices, conditions=conditions, determinants=determinants,
                         relative_scale_disagreement=disagreement, qualified=bool(good)))
    if signs not in ({-1}, {1}) or not all(r["qualified"] for r in rows):
        return dict(qualified=False, reason="singularity, conditioning, orientation or scale disagreement", matrices=rows, proposal=None)
    mean = np.mean([r["matrices"][1] for r in rows], axis=0)
    f0 = np.mean([r["value"] for r in base], axis=0)
    if not np.isfinite(f0).all() or np.linalg.cond(mean) > 1e4:
        return dict(qualified=False, reason="mean system unqualified", matrices=rows, proposal=None)
    delta = np.linalg.solve(mean, -f0)
    if not np.isfinite(delta).all() or max(abs(delta)) == 0:
        return dict(qualified=False, reason="nonfinite or zero proposal", matrices=rows, proposal=None)
    factor = min(1., 10./max(abs(delta)))
    parameters = dict(anchor)
    for axis, h, value in zip(AXES, INCREMENTS, delta*factor, strict=True):
        parameters[axis] += h*float(value)
    return dict(qualified=True, reason=None, matrices=rows, mean_jacobian=mean.tolist(), base_mean=f0.tolist(),
        unclipped_step=delta.tolist(), clipping_factor=float(factor),
        proposal=dict(id="joint-proposal", parameters=parameters))


def scalar_proposal(result, base, anchor):
    """Separate scalar inverse and summation, not np.linalg.solve/mean."""
    if not result["qualified"]:
        return None
    n = len(result["matrices"])
    a, b, c, d = [math.fsum(r["matrices"][1][i][j] for r in result["matrices"])/n
                   for i, j in ((0, 0), (0, 1), (1, 0), (1, 1))]
    f, g = [math.fsum(r["value"][i] for r in base)/len(base) for i in (0, 1)]
    determinant = a*d-b*c
    step = [(b*g-d*f)/determinant, (c*f-a*g)/determinant]
    factor = min(1., 10./max(map(abs, step)))
    return dict(anchor, a=anchor["a"]+INCREMENTS[0]*step[0]*factor,
                c=anchor["c"]+INCREMENTS[1]*step[1]*factor)


def verdict(matrix, proposal, base):
    if not matrix["qualified"]:
        return dict(status="unresolved-response-matrix", joint_proximity=False, residual_reduction=None)
    if proposal is None or not proposal["qualified"]:
        return dict(status="failed-proposal-qualification", joint_proximity=False, residual_reduction=None)
    before = max(abs(np.mean([r["value"] for r in base], axis=0)))
    after = max(abs(np.mean([r["value"] for r in proposal["vectors"]], axis=0)))
    reduction = float(1-after/before) if before else None
    return dict(status="qualified-joint-proximity" if proposal["joint_proximity"] else "qualified-proposal-without-joint-proximity",
                joint_proximity=proposal["joint_proximity"], residual_reduction=reduction,
                reduction_at_least_twenty_percent=reduction is not None and reduction >= .2)

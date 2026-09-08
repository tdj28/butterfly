"""Finite-history dominant return directions, not an invariant-curve proof."""
from __future__ import annotations

import numpy as np


def line_angle(left, right):
    """Unsigned angle between unoriented 2D lines, stable near agreement."""
    left, right = np.asarray(left, float), np.asarray(right, float)
    if any(v.shape != (2,) or not np.isfinite(v).all() or np.linalg.norm(v) == 0 for v in (left, right)):
        raise ValueError("nonzero finite two-dimensional directions required")
    left, right = left/np.linalg.norm(left), right/np.linalg.norm(right)
    return float(np.arctan2(abs(left[0]*right[1]-left[1]*right[0]), abs(left @ right)))


def dominant_history(matrices, *, depths=(1, 2, 4, 8)):
    """Compose chronological derivatives; leading LEFT vector lives at endpoint.

    Normalize the product after every multiplication. This preserves singular
    directions, not absolute expansion. Ratios below floating precision are not
    evidence of an exactly singular flow map. Matrices use the declared metric.
    """
    matrices = np.asarray(matrices, float)
    if (matrices.ndim != 3 or matrices.shape[1:] != (2, 2)
            or not np.isfinite(matrices).all() or not depths
            or any(type(n) is not int or n < 1 or n > len(matrices) for n in depths)
            or list(depths) != sorted(set(depths))):
        raise ValueError("finite chronological 2D matrices and increasing valid depths required")
    rows = []
    for depth in depths:
        product = np.eye(2)
        for matrix in matrices[-depth:]:
            scale = np.max(np.abs(matrix))
            if scale == 0:
                raise ValueError("zero derivative has no dominant transported line")
            product = (matrix/scale) @ product
            scale = np.max(np.abs(product))
            if scale == 0 or not np.isfinite(scale):
                raise ValueError("degenerate transported product")
            product /= scale
        u, singular, vh = np.linalg.svd(product)
        direction = u[:, 0]
        if direction[np.argmax(np.abs(direction))] < 0:
            direction = -direction
        rows.append(dict(depth=depth, direction=direction.tolist(),
                         singular_ratio=float(singular[1]/singular[0])))
    return rows


def assess_direction(histories, current_jacobians, *, maximum_ratio=1e-4,
                     maximum_angle=1e-3, minimum_x_component=1e-3):
    """Finite-history/solver consistency gate; never certifies a scalar map.

    Require separation at the two longest declared histories in both solvers,
    their endpoint line agreement, and cross-solver agreement at every depth.
    Near-vertical directions have no reported x-graph derivative.
    """
    if len(histories) != 2 or set(histories) != set(current_jacobians):
        raise ValueError("exactly two solver histories and derivatives required")
    values = list(histories.values())
    depths = [[row["depth"] for row in h] for h in values]
    if len(depths[0]) < 2 or depths[0] != depths[1]:
        raise ValueError("matching histories with two or more depths required")
    history_angles = {name: line_angle(h[-2]["direction"], h[-1]["direction"])
                      for name, h in histories.items()}
    solver_angles = [line_angle(a["direction"], b["direction"])
                     for a, b in zip(*values, strict=True)]
    checks = dict(separation=all(0 <= r["singular_ratio"] <= maximum_ratio
                                for h in values for r in h[-2:]),
                  history_agreement=max(history_angles.values()) <= maximum_angle,
                  solver_agreement=max(solver_angles) <= maximum_angle)
    projected = {}
    for name, h in histories.items():
        v = np.asarray(h[-1]["direction"])
        matrix = np.asarray(current_jacobians[name], float)
        if matrix.shape != (2, 2) or not np.isfinite(matrix).all():
            raise ValueError("finite current derivative required")
        graph = abs(v[0]) >= minimum_x_component
        projected[name] = dict(direction=v.tolist(), graph_defined=bool(graph),
            x_graph_derivative=float((matrix @ v)[0]/v[0]) if graph else None,
            coordinate_partial=float(matrix[0, 0]))
    return dict(direction_consistent=all(checks.values()), checks=checks,
                history_angles=history_angles, solver_angles=solver_angles,
                projected=projected)

"""Closed-form and independently checkable Rössler equilibrium Hopf locus."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .models import (
    FloatVector,
    RosslerParameters,
    equilibrium_eigenvalues,
    rossler_equilibria,
)


@dataclass(frozen=True, slots=True)
class RosslerHopfPoint:
    """One regular equilibrium Hopf point at fixed ``(a,b)``.

    ``equilibrium_index`` refers to the ordering returned by
    :func:`rossler_equilibria`.  The point is algebraic; no trajectory
    integration or finite-difference continuation is used to construct it.
    """

    parameters: RosslerParameters
    equilibrium: FloatVector
    equilibrium_index: int
    angular_frequency: float
    real_eigenvalue: float


def rossler_equilibrium_characteristic_coefficients(
    parameters: RosslerParameters, equilibrium: FloatVector
) -> FloatVector:
    """Return ``(A,B,C)`` for ``lambda^3+A lambda^2+B lambda+C``.

    At an equilibrium ``(a*z,-z,z)``, writing ``r=b/z=c-a*z`` gives
    ``A=r-a``, ``B=1+z-a*r``, and ``C=r-a*z``.  The explicit coefficients
    provide a Routh--Hurwitz check independent of numerical eigensorting.
    """

    _x, _y, z = np.asarray(equilibrium, dtype=np.float64)
    if z == 0.0:
        raise ValueError("characteristic coefficient form requires z != 0")
    r = parameters.b / z
    return np.asarray(
        (r - parameters.a, 1.0 + z - parameters.a * r, r - parameters.a * z),
        dtype=np.float64,
    )


def rossler_hopf_points(a: float, b: float) -> tuple[RosslerHopfPoint, ...]:
    """Return every regular positive-``z`` equilibrium Hopf point at ``(a,b)``.

    For the declared Rössler equations, the Hopf condition ``A*B=C`` reduces
    exactly to

    ``a * (1 + r**2 - a*r) = b``, where ``r=b/z``.

    Positive roots yield ``z=b/r`` and ``c=a*z+r``.  Degenerate zero-Hopf
    points (``A=0``) and nonpositive roots are excluded.
    """

    values = np.asarray((a, b), dtype=np.float64)
    if not np.all(np.isfinite(values)) or a <= 0.0 or b <= 0.0:
        raise ValueError("regular Rössler Hopf points require finite a>0 and b>0")

    discriminant = a**4 - 4.0 * a * (a - b)
    scale = max(a**4, abs(4.0 * a * (a - b)), 1.0)
    tolerance = 32.0 * np.finfo(np.float64).eps * scale
    if discriminant < -tolerance:
        return ()
    discriminant = max(discriminant, 0.0)
    root = float(np.sqrt(discriminant))
    r_large = (a * a + root) / (2.0 * a)
    roots = [r_large]
    if r_large != 0.0:
        # Product-of-roots recovery avoids cancellation near a=b.
        roots.append((a - b) / (a * r_large))

    points: list[RosslerHopfPoint] = []
    for r in sorted(set(float(value) for value in roots), reverse=True):
        if r <= tolerance:
            continue
        z = b / r
        c = a * z + r
        parameters = RosslerParameters(a=a, b=b, c=c)
        equilibria = rossler_equilibria(parameters)
        equilibrium_index = int(np.argmin(np.abs(equilibria[:, 2] - z)))
        equilibrium = equilibria[equilibrium_index]
        coefficients = rossler_equilibrium_characteristic_coefficients(
            parameters, equilibrium
        )
        A, B, C = map(float, coefficients)
        if abs(A) <= tolerance or B <= tolerance or abs(A * B - C) > 1e-9:
            # Exclude zero-Hopf degeneracies and guard the algebraic map.
            continue
        eigenvalues = equilibrium_eigenvalues(parameters)[equilibrium_index]
        real_index = int(np.argmin(np.abs(eigenvalues.imag)))
        real_eigenvalue = float(eigenvalues[real_index].real)
        points.append(
            RosslerHopfPoint(
                parameters=parameters,
                equilibrium=equilibrium.copy(),
                equilibrium_index=equilibrium_index,
                angular_frequency=float(np.sqrt(B)),
                real_eigenvalue=real_eigenvalue,
            )
        )
    return tuple(sorted(points, key=lambda point: point.parameters.c))

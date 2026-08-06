"""Dynamical-system definitions shared by reference and accelerated paths."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatVector = NDArray[np.float64]
FloatMatrix = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class RosslerParameters:
    """Parameters for x'=-y-z, y'=x+a*y, z'=b+z*(x-c)."""

    a: float
    b: float
    c: float

    def __post_init__(self) -> None:
        values = np.asarray((self.a, self.b, self.c), dtype=np.float64)
        if not np.all(np.isfinite(values)):
            raise ValueError("Rössler parameters must be finite")


def rossler_rhs(
    _time: float, state: ArrayLike, parameters: RosslerParameters
) -> FloatVector:
    """Evaluate the Rössler vector field in Float64."""

    x, y, z = np.asarray(state, dtype=np.float64)
    return np.asarray(
        (-y - z, x + parameters.a * y, parameters.b + z * (x - parameters.c)),
        dtype=np.float64,
    )


def rossler_jacobian(
    state: ArrayLike, parameters: RosslerParameters
) -> FloatMatrix:
    """Return the analytic state Jacobian of the Rössler vector field."""

    x, _y, z = np.asarray(state, dtype=np.float64)
    return np.asarray(
        (
            (0.0, -1.0, -1.0),
            (1.0, parameters.a, 0.0),
            (z, 0.0, x - parameters.c),
        ),
        dtype=np.float64,
    )


def rossler_equilibria(parameters: RosslerParameters) -> FloatMatrix:
    """Return real equilibria ordered by increasing z coordinate.

    For nonzero ``a``, the z coordinates solve ``a*z**2-c*z+b=0``.
    The degenerate ``a=0`` case has one equilibrium when ``c`` is nonzero.
    """

    a, b, c = parameters.a, parameters.b, parameters.c
    if a == 0.0:
        if c == 0.0:
            if b == 0.0:
                raise ValueError("a=b=c=0 has a continuum of equilibria")
            return np.empty((0, 3), dtype=np.float64)
        z = b / c
        return np.asarray(((0.0, -z, z),), dtype=np.float64)

    discriminant = c * c - 4.0 * a * b
    scale = max(c * c, abs(4.0 * a * b), 1.0)
    if discriminant < -np.finfo(np.float64).eps * scale * 8.0:
        return np.empty((0, 3), dtype=np.float64)
    discriminant = max(discriminant, 0.0)
    root = np.sqrt(discriminant)

    # This form avoids losing the small root when c and sqrt(discriminant)
    # nearly cancel. The second root follows from the product b/a.
    q = 0.5 * (c + np.copysign(root, c if c != 0.0 else 1.0))
    if q == 0.0:
        z_values = (c / (2.0 * a),)
    else:
        z_values = (b / q, q / a)
    unique = sorted(set(float(z) for z in z_values))
    return np.asarray([(a * z, -z, z) for z in unique], dtype=np.float64)


def equilibrium_eigenvalues(
    parameters: RosslerParameters,
) -> NDArray[np.complex128]:
    """Return one row of Jacobian eigenvalues for each real equilibrium."""

    equilibria = rossler_equilibria(parameters)
    if len(equilibria) == 0:
        return np.empty((0, 3), dtype=np.complex128)
    return np.asarray(
        [np.linalg.eigvals(rossler_jacobian(point, parameters)) for point in equilibria],
        dtype=np.complex128,
    )

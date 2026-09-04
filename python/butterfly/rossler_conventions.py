"""Translate canonical Rössler equations to the origin-fixed convention.

Malykh et al. (2020), doi:10.1063/5.0026188, eqs. (1)-(2):
    X'=-Y-Z, Y'=X+alpha*Y, Z'=beta*X+Z*(X-gamma).
Equal parameter names in the two forms do NOT mean equal parameter slices.
There is no time rescaling. The shift can use any real equilibrium; the
default is the canonical equilibrium with smallest z, as in models.py.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .models import RosslerParameters, rossler_equilibria


@dataclass(frozen=True, slots=True)
class OriginFixedRosslerParameters:
    alpha: float
    beta: float
    gamma: float

    def __post_init__(self):
        if not np.all(np.isfinite((self.alpha, self.beta, self.gamma))):
            raise ValueError("translated Rössler parameters must be finite")

    @property
    def canonical(self) -> RosslerParameters:
        return RosslerParameters(self.alpha, self.beta * self.gamma, self.gamma + self.alpha * self.beta)

    @property
    def equilibrium_shift(self) -> np.ndarray:
        return np.asarray((self.alpha * self.beta, -self.beta, self.beta))


def canonical_to_origin_fixed(parameters: RosslerParameters, *, equilibrium_index: int = 0) -> OriginFixedRosslerParameters:
    equilibria = rossler_equilibria(parameters)
    if type(equilibrium_index) is not int or not 0 <= equilibrium_index < len(equilibria):
        raise ValueError("a valid real equilibrium index is required")
    beta = float(equilibria[equilibrium_index, 2])
    return OriginFixedRosslerParameters(parameters.a, beta, parameters.c - parameters.a * beta)


def origin_fixed_rossler_rhs(_time, state, parameters: OriginFixedRosslerParameters):
    x, y, z = np.asarray(state, dtype=float)
    return np.asarray((-y-z, x+parameters.alpha*y, parameters.beta*x + z*(x-parameters.gamma)))

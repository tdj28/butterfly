# FND-038 — One transverse saddle bracket passes; the second remains open

Status: mixed prospective result from failed EXP-132

## Finding

At a 256-return censor ceiling, EXP-132 prospectively qualifies the finite
two-to-three saddle bracket `a in [0.145,0.150]` at fixed `b=0.2,c=19.9`.
The lower endpoint is two-branch with negative signed edge slope under the
independently qualified coverage-only censor; the upper endpoint is
three-branch with positive slope in all 30 coordinate/variant decisions.

The `c=19.8` upper endpoint at `a=0.150` also passes as three/positive in all
30 decisions. Its proposed lower endpoint at `a=0.148` does not pass: 24/30
branch variants return two and all 30 slopes are negative, but the six
highest-bin decisions are bootstrap-unstable. Because bootstrap instability
was prospectively forbidden from masquerading as a coverage censor, that
endpoint and the full four-endpoint experiment remain failed.

All twelve PIM access lines resolved, every endpoint supplied 2097 return
pairs per coordinate, and none of 69,351 lifetime evaluations failed. The
mixed result is therefore a scientific classification limit rather than a
numerical integration failure.

## Implication for Jones

This is net good news for the local Jones/Barrio topology-change picture. It
provides the first prospectively qualified finite transverse bracket away
from `c=20` and independently confirms a three-branch saddle at the untouched
`c=19.8,a=0.150` endpoint. It also strengthens the correction that the local
boundary bends or shifts rather than continuing vertically from `c=20`.

It is not yet a curve: one finite bracket does not prove continuity, and the
`c=19.8` lower endpoint is still unresolved. Future continuation must use a
smooth dynamical residual or a genuinely converged classification, not relabel
the failed high-bin bootstrap cells.

Tracked receipt: `docs/experiments/receipts/EXP-132.json`.

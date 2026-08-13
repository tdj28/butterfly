# EXP-213 — Historical-section grazing on the period-6 flip curve

Status: prospectively frozen before refinement

## Question

Is EXP-212's lower termination a nondegenerate grazing of the historical
Poincare half-plane rather than an endpoint of the real-`-1` flow-orbit event?

## Frozen design

The deterministic EXP-212 bracket `c=6.9324593154--6.9412893753` is refined
while solving the exact period-6 flip event at every bisection point. The
continuous residual is the closest `y` extremum's signed clearance from the
small equilibrium's `y` coordinate. At zero clearance, `dy/dt=0` implies the
same point lies at the half-plane's `x=x_eq` gate boundary.

The final bracket must separate seven and six historical phases while both
ends retain eight Barrio phases and every invariant event gate except the
changing historical count. Clearance, gate margin, and tangency must converge;
the extremum must be nondegenerate. Radau must independently recover the event
and grazing at the final estimate.

Manifest:
[`../../experiments/manifests/EXP-213-period6-flip-section-grazing.json`](../../experiments/manifests/EXP-213-period6-flip-section-grazing.json).

## Claim boundary

A pass establishes a section-representation boundary on the sampled flip
curve. It is not a flow-orbit bifurcation, a physical curve endpoint, the TBA,
or a global explanation of shrimp organization.

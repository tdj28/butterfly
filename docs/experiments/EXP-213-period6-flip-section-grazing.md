# EXP-213 — Historical-section grazing on the period-6 flip curve

Status: complete — failed final integer-count gate

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

## Result

The continuous refinement converges, but the overall frozen gate fails. The
signed extremum clearance changes sign in a `6.58e-11`-wide bracket centered
at `c=6.93831802121`. The best DOP853 point has clearance `2.22e-11`, gate
margin `4.81e-12`, tangency residual `1.56e-14`, and nondegenerate second
derivative `-13.6961`. Radau independently gives clearance `-3.16e-11`, with
`6.78e-15` difference in `a` and `1.24e-12` relative period difference.

The failing gate is specifically the final raw crossing count: both bracket
ends report six historical phases rather than the required seven/six pair,
while Barrio remains eight/eight. Earlier lower-`c` evaluations do report
seven. The standard sign-change collector loses the close crossing pair as it
approaches tangency, the same numerical hazard previously exposed by EXP-055.
EXP-214 therefore freezes an extremum-partitioned count without changing the
continuous grazing equation.

Raw receipt: `artifacts/EXP-213/receipt.json`, 39,827 bytes, SHA-256
`7abc822a5683646e8dba007c2f34801762eb1f6ecdba8442e5217f9f41099b9f`.
Compact receipt:
[`receipts/EXP-213.json`](receipts/EXP-213.json).

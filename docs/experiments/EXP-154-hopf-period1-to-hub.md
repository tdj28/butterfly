# EXP-154 — Period-1 continuation from Hopf to the reported hub

Status: pilot-informed method and gates frozen before clean qualification

## Question

Does one one-winding period-1 flow-orbit family connect the qualified
small-equilibrium Hopf neighborhood to the reported hub coordinate along the
explicit fixed path `(a,b)=(0.1798,0.2)`?

## Frozen method

A stable period-1 attractor at `c=1` supplies a shooting seed. Phase-conditioned
shooting then follows the same one-winding orbit downward to
`c_H+0.001` and upward to `c=10.3084` at 118 exact points. Every row records
closure, phase residual, Floquet multipliers, winding number, period, and
minimum/RMS/maximum distance from the small equilibrium.

The near-Hopf RMS amplitude over offsets no larger than `0.02` must scale with
exponent in `[0.48,0.52]` and `R^2>=0.999`; its nearest period must approach
the linear Hopf period within `0.003`. At least one real `-1` multiplier
crossing must be bracketed. Six exact checkpoints are independently recorrected
with Radau, including the near-Hopf point and reported hub.

The schedule and thresholds were informed by an untracked feasibility pilot,
so this is a qualification replication rather than a blind discovery.

## Interpretation boundary

Passing would establish same-family period-1 connectivity and a supercritical
Hopf amplitude law along an explicit L2-like path. A finite period-1 orbit at
the hub would not be the proposed homoclinic orbit; the latter is a distinct
stable/unstable equilibrium-manifold intersection that must be solved
independently. The result cannot establish logistic ordering or a topology-
transition curve.

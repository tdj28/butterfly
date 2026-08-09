# EXP-155 — Corrected Hopf-to-hub period-1 qualification

Status: passed all unchanged scientific and administrative gates

EXP-154 passed every scientific tolerance but failed its exact row-count gate
because a near-Hopf independent-solver checkpoint was inserted into both
continuation directions and the seed was duplicated. EXP-155 fixes only that
direction-aware schedule partition. It retains the same 118 scientific points,
seed, DOP853 and Radau solvers, orbit samples, Hopf scaling interval, winding
identity, Floquet crossing requirement, and every numerical acceptance
threshold.

The raw EXP-154 receipt remains immutable. Passing EXP-155 may qualify the
scientific result; it cannot retroactively turn EXP-154 into a pass.

## Result

EXP-155 passes with exactly 118 points. Maximum closure is `3.60e-12`, maximum
neutral-multiplier error is `3.79e-12`, and maximum winding error is
`1.15e-13`. The near-Hopf amplitude exponent is `0.5017311` with
`R^2=0.9999983`; all six Radau checks pass. A real `-1` multiplier crossing is
bracketed over `c in [3.1556294737,3.2536126316]`.

At the hub, the one-winding orbit has period `5.9935437090`, primary
nontrivial multiplier `-3.2022459546`, and minimum equilibrium distance
`10.0310033361`. It is a finite unstable period-1 orbit, not the proposed
homoclinic connection. The tracked receipt is
`docs/experiments/receipts/EXP-155.json`.

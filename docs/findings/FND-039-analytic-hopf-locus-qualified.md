# FND-039 — The analytic Hopf locus is qualified

Status: passed EXP-153

## Finding

The regular small-equilibrium Andronov--Hopf locus at fixed `b=0.2` has been
constructed exactly and independently reproduced by eigensystem root solves at
192 points. Over `a in [0.1,0.195]`, it runs from `c=1.0702742041` to
`c=0.4218296645`. Every point has the required negative real eigenvalue, a
purely imaginary conjugate pair, and the frozen transverse sign change.

At the reported hub abscissa `a=0.1798`, the Hopf point is
`c=0.5192306256940273`. The fixed-`a` separation to the proposed homoclinic hub
coordinate `c=10.3084` is therefore `9.789169374305974`.

## Implication for Jones

This validates the local starting bifurcation used in the Figure 2
Hopf-to-homoclinic construction without depending on PyCONT/AUTO. It makes the
vertical `L2`-like path fully explicit at its Hopf end and converts part of
CLM-005 from an illustration into a reproducible equation and dataset.

It does not show that the period-1 orbit survives along that entire path, that
its endpoint is homoclinic, or that the homoclinic point is unique. It also does
not recover the exact historical `L1` and `L2` path definitions or qualify the
claimed logistic ordering. Those are now sharply separated follow-up tests.

Tracked receipt: `docs/experiments/receipts/EXP-153.json`.

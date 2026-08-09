# EXP-156 first period-1 flip frozen

Date: 2026-08-07

The first stability loss on the qualified Hopf-to-hub period-1 family now has
a coupled exact-Jacobian test. The Rössler augmented flip machinery has been
extended from `b` continuation to `c` continuation with finite-difference
verification of its state, parameter, and second-variational derivatives.

EXP-156 freezes the EXP-155 bracket, four-node anti-periodic shooting, cyclic
Floquet-product agreement, and an independent Radau check. Passing is only the
event gate; period-2 branch switching remains separate.

The clean solve subsequently passes at `c=3.1807265333384103`. All coupled
residuals are below `4.76e-15`; four cyclic products agree on `-1` within
`7e-15`; and independent Radau returns `-0.9999999999998008`. The event is
closed, while the period-2 child remains the next separate gate.

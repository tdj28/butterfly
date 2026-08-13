# EXP-208 freezes independent qualification of the period-12 nominations

EXP-207 failed its strict branch-arm gate but produced one accurate stable
12/16-phase nomination at each of three separated flip events. EXP-208 freezes
those exact coordinates before any independent correction result is examined.

The successor deliberately avoids inheriting EXP-207's continuation success
flag. It starts from the raw parent and child states, corrects each separately
with DOP853 and Radau, and requires solver identity, Floquet agreement,
parent/child stability exchange, period ratio two, both section identities,
and rejection of every proper subperiod. Only a three-of-three pass can upgrade
the nominations to qualified sampled period-12 children.

The clean execution passes three of three. Parent moduli are
`1.20713`--`1.29062`, child moduli are `0.02354`--`0.20615`, period ratios are
`1.999923`--`1.999932`, and every 6/8 parent and 12/16 child section count is
exact. DOP853/Radau orbit RMS is at most `6.29e-11`; no proper subperiod closes,
with a minimum return distance `0.09413` versus full closures below
`5.30e-11`.

This upgrades the three post-run leads to qualified sampled primitive stable
period-12 children, while preserving EXP-207's failed branch-arm claim. The
next prospective test is fixed-`c`, fixed-`a` child continuation back toward
each event, with frozen square-root opening, multiplier-scaling, and perturbed
attraction gates.

Receipt: [`../experiments/receipts/EXP-208.json`](../experiments/receipts/EXP-208.json).

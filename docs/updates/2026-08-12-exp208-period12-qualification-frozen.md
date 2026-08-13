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

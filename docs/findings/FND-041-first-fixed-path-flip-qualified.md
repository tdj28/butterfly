# FND-041 — The first fixed-path flip is qualified

Status: passed EXP-156

## Finding

The first stability loss of the one-winding period-1 family on the explicit
fixed path `(a,b)=(0.1798,0.2)` is a genuine period-doubling event at
`c=3.1807265333384103`.

Four-node orbit matching, phase, anti-periodic tangent transport, and tangent
normalization residuals are all below `4.76e-15`. The block-cyclic multiplier
is `-1.0000000000000047`; four direct cyclic products have median
`-1.0000000000000067` and spread `1.56e-15`. Independent Radau monodromy gives
`-0.9999999999998008`, closes within `3.50e-14`, and retains winding one.

## Implication for Jones

This upgrades the first qualitative stability loss on an L2-like path to a
coupled, identity-safe flow bifurcation. Together with EXP-153 and EXP-155, it
establishes the Hopf-born period-1 parent and its first flip along one explicit
slice—two prerequisites of the finite logistic-ordering argument.

EXP-157 and EXP-158 subsequently prove that a stable primitive period-2 child
opens on the post-flip side; see FND-042. This finding alone did not establish
that child, and neither result yet establishes later windows or symbolic
ordering.

Tracked receipt: `docs/experiments/receipts/EXP-156.json`.

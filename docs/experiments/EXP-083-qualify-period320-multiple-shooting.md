# EXP-083 — Independently qualify the period-320 candidate

Status: preregistered after EXP-082; pending clean execution

First validate a block-cyclic Floquet calculation against the ordinary
monodromy result for the independently established period-80 child at
`b=0.179735`. The block method propagates perturbations only over individual
shooting segments; its eigenvalue radii recover full-orbit multiplier moduli
without composing the ill-conditioned duration-2092 monodromy directly.

Then take both accepted EXP-082 switch signs at frozen step `0.005`, correct
them independently with 32-segment fixed-`b` shooting at `b=0.1797132`, and
test whether they are cyclic phase representations of one orbit. Pass only if
the lower-period Floquet modulus agrees within `1e-5`, both high-period
matching residuals are `<=1e-8`, opposite-sign cyclic node RMS is `<=1e-5`,
both half-period distinctness measures are `>=1e-5`, and both dominant
nontrivial block-Floquet moduli are `<=0.999`.

Passing would establish a stable, geometrically identified period-320 cycle
on the supercritical side of the EXP-077 flip. It would close the sixth local
cascade rung numerically; it would still not constitute a rigorous
universality proof.

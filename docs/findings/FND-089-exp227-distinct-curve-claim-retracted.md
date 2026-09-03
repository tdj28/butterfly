# FND-089 — The EXP-227 distinct-curve claim is retracted

Status: retracted by EXP-229

EXP-227's 21 event solutions and three solver controls are numerically sound,
but its comparator was not. It measured distance to a linear interpolation of
the sparse EXP-217 receipt. Curvature of that arm produces an interpolation
error of `5.60e-7--5.85e-7`, the full apparent separation.

EXP-229 freshly corrects the EXP-217 event at every EXP-227 `c`. All 21 pairs
coincide: maximum `a` difference `1.46e-14`, relative period difference
`2.23e-15`, state difference `4.77e-11`, tangent difference `4.04e-12`, and
multiplier-modulus difference `1.14e-10`. Three independent Radau controls
also pass. The distinct-curve and paired-boundary inferences are therefore
retracted.

Original evidence:
[`../experiments/EXP-227-second-period6-flip-local-curve.md`](../experiments/EXP-227-second-period6-flip-local-curve.md).
Corrective evidence:
[`../experiments/EXP-229-exp227-exact-source-identity.md`](../experiments/EXP-229-exp227-exact-source-identity.md).

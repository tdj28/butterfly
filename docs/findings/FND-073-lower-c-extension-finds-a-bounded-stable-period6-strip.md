# FND-073 — The lower-c extension finds a bounded stable period-6 strip

Status: qualified orbit geometry; frozen coverage gate failed

EXP-203 corrects all 6,283 preregistered points in a new rectangle extending
from `c=7.288` to `c=6.88`, without evaluating a return-map critical. The seed
passes, and 551 points pass every DOP853 closure, phase, family-identity,
section-count, Floquet, and stability gate. This is below the frozen minimum of
1,000, so the experiment fails as a coverage-qualified preparation.

The 551 qualified orbits occupy a bounded strip over
`a in [0.2155,0.2158]` and `c in [7.132,7.288]`, split into five
eight-connected components of sizes `331,156,62,1,1`. The 331-point seed
component spans `a in [0.2155,0.21577]`, `c in [7.22,7.268]`, and touches the
lower-`a` boundary. The 62-point upper component reaches the `c=7.288` overlap
boundary. The only qualified point below `c=7.184` is isolated at
`(a,c)=(0.21571,7.132)`.

Outside the strip, 4,921 points first fail orbit correction and 806 first fail
stability; only five first fail the correction-distance identity gate. Among
qualified points, the dominant nontrivial Floquet modulus reaches `0.99945`,
confirming that part of the strip approaches a stability boundary.

This result blocks a naive extrapolation of EXP-202's affine residual descent
toward higher `a` or much lower `c`: the stable family does not fill that
rectangle. It does not show that the period-6 family ends. The next admissible
tests are fold/stability-boundary continuation and a separately frozen
scale-ensemble residual replay on the 551 individually qualified orbits;
unstable continuation must remain available across the failed region.

Evidence: [`../experiments/EXP-203-lower-c-stable-period6-extension.md`](../experiments/EXP-203-lower-c-stable-period6-extension.md).

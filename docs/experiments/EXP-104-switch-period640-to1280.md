# EXP-104 — Switch the corrected period-640 flip to period 1280

Status: preregistered; not executed

Bind the passed full EXP-103 event receipt and double its 64 period-640 nodes
to a 128-segment, double-covered parent. Construct the secondary branch
direction directly from EXP-103's transported anti-periodic tangent nodes:
use `(v_0,...,v_63,-v_0,...,-v_63)` and add the unique repeated flow-tangent
component that satisfies the frozen phase row. Normalize the full direction
with zero initial period and parameter components.

Before switching, require the direction's residual under the doubled periodic-
orbit Jacobian to be `<=1e-7`. Try frozen predictor lengths `0.0005` and
`0.001` with both signs, using 128-segment analytic multiple shooting and the
EXP-103 tight integrator. Permit 100 corrector evaluations per attempt at
tolerance `2e-12`.

Accept a candidate only when matching and phase residuals are `<=1e-8`, both
half-period closure and half-node RMS are `>=1e-5`, the period ratio differs
from two by `<=0.001`, and it lies on the expected side of the event with
`0 < b_* - b <=1.5e-7`. At least one accepted candidate is required.

Passing establishes distinct period-1280 branch candidates but not stability,
common-parameter identity, or supercriticality. Those require a separate
fixed-parameter qualification. Failure retains the corrected eighth event and
triggers a switch-amplitude or conditioning audit without weakening identity
gates.

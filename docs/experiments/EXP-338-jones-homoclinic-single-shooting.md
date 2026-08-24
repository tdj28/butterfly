# EXP-338 — Fixed-c homoclinic single shooting

Status: preserved administrative receipt failure; EXP-339 frozen

EXP-337 passes its coverage recovery and sharpens the direct nonlinear
manifold mismatch to `0.000162262` at `a=0.18255`, but the best row is isolated
under the discontinuous first-return event selector and no degree cell exists.
EXP-338 therefore switches to the smooth boundary-value formulation.

At fixed `(b,c)=(0.2,10.3084)`, the unknowns are unstable departure angle,
`a`, and total flight time. The forward endpoint from the radius-`1e-7`
unstable seed is matched in all three state coordinates to the positive
nonlinear stable-manifold target on the radius-`0.03` sphere. The source row
supplies angle `2.4707317223544725`, `a=0.18255`, and total flight time
`234.2623011851337`. A bounded trust-region least-squares solve may move by one
fine angle spacing, `0.00025` in `a`, and five time units.

An interior residual at most `1e-8` only nominates a single-shooting root.
Qualification still requires multiple shooting, shrinking matching spheres,
and independent integration because a 234-time-unit chaotic trajectory is
too ill-conditioned for a final claim under one forward solve.

Manifest:
[`../../experiments/manifests/EXP-338-jones-homoclinic-single-shooting.json`](../../experiments/manifests/EXP-338-jones-homoclinic-single-shooting.json).

The numerical solve completed, but final receipt serialization stopped because
the initial-residual check remained a NumPy boolean. No receipt was written and
no optimizer result is recoverable from the traceback. EXP-339 converts only
that check to a JSON-native boolean; every scientific and optimization value
is unchanged.

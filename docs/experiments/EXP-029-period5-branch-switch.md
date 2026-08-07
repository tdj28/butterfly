# EXP-029 — Prospective period-5 branch switch at the +1 event

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-029-period5-branch-switch.json`
Claim target: generic structure of the EXP-028 period-5 branch point

## Hypothesis and method

The EXP-028 double-unit event has a second local periodic-orbit branch whose
tangent is linearly independent of the primary EXP-027 family.

Build the exact `4 x 5` phase-conditioned shooting Jacobian with state,
period, and `b` columns, including integrated `b` sensitivity. At a regular
one-parameter family its null space is one-dimensional. At the accepted event,
a second unit multiplier should reduce its rank and create a two-dimensional
null space. Project the observed EXP-027 tangent into that space, construct its
orthogonal complement, and use both signs of this secondary tangent as
pseudo-arclength predictors. Correct and continue twelve constant-length steps
in each direction without using the resulting orbit data to alter the frozen
step or gates.

## Acceptance and limits

The second-smallest singular value must be at most `1e-7`; the secondary and
primary tangents must have absolute dot product at most `0.25`. Each direction
must produce at least eight corrected points, all closures must be at most
`1e-8`, and its endpoint must differ from the interpolated primary branch by at
least `1e-5` in the five-dimensional shooting variables.

Passing demonstrates a numerically distinct crossing branch locally. It does
not by itself distinguish transcritical from pitchfork geometry: that requires
tracking branch identity on both sides, testing symmetries, and estimating the
local normal form with resolution/tolerance checks.

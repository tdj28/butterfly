# EXP-029 — Prospective period-5 branch switch at the +1 event

Status: executed; frozen gates passed; orbit identity qualification pending
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

## Result

The clean run at commit `51460c43ab0e1c49bb9e0a0532e51e243a8444db`
passed every frozen gate. The extended shooting singular values were
`(68.8239,1.00611,1,4.64e-11)`, and the derived primary/secondary tangent dot
product was `5.55e-17`. Both signs produced all twelve requested corrected
points; maximum closure was `2.42e-11`. Endpoint distances from the
interpolated primary branch were `0.0706` and `0.0812`, far above the `1e-5`
gate. The receipt SHA-256 is
`eb03f92d7577a866413d756e491f1a114b7e180643aba0bbd525700214298aee`.

Both switched arms move to `b` above the event and remain stable in the sampled
range, while the primary branch's significant real multiplier exceeds one.
This is consistent with a supercritical pitchfork-like stability exchange, but
that wording is not yet accepted.

## Post-result identity warning and next action

The frozen coordinate-distance gate is not phase invariant. A post-result
design diagnostic at `b=0.2735` found that the two switched arms align with one
another after a near-half-period shift (phase-aligned RMS `9.3e-8`), whereas
each remains far from the primary orbit (RMS `0.261`) and differs in flow
period. Thus the present evidence suggests one genuine secondary geometric
orbit represented twice by the phase condition, not two daughter orbits.

EXP-030 freezes the correct phase-invariant comparison at the previously
uninspected `b=0.2730`. Until it passes, EXP-029 establishes successful
coordinate branch switching but not the number of distinct invariant cycles.

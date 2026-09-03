# DEC-010 — Use the lower-support return-map slope as a signed companion observable

Date: 2026-08-07
Status: held-out local prediction passed; global continuation unqualified

## Context

The PIM branch oracle has localized a discrete two-to-three change to
`a in [0.148,0.14825]` at fixed `(b,c)=(0.2,20)`. More midpoint branch counts
would narrow that finite classifier bracket, but a branch count is integer
valued and cannot by itself define or continue a level set in `(a,c,b)`.

Existing PIM return relations suggest a more informative local coordinate. In
the two-branch cases the fitted relation descends from the lower occupied
support. In the three-branch cases it ascends there before forming the added
near-boundary extremum. The derivative at that occupied boundary is therefore
a candidate signed precursor to the discrete critical-point count.

## Decision

For every already declared bin/smoothing variant, affinely normalize the
source and target coordinates, construct the same median-binned cubic spline
used by the branch oracle, and evaluate its derivative at the first populated
binned-source median. Do not evaluate at normalized zero or extrapolate beyond
the occupied data.

A coordinate/horizon decision resolves only if all 15 variants have the same
strict sign and the smallest absolute normalized slope is at least `0.1`.
Negative maps to the calibrated two-branch class and positive maps to the
calibrated three-branch class. Both `y` and `z`, and both 128- and 256-return
PIM censor profiles, must agree. The slope-predicted class must also equal the
blind critical-point branch count.

The `0.1` magnitude gate and sign mapping were selected after exploratory
inspection of existing controls and bracket endpoints, but before generating
the EXP-129 midpoint data. The immutable reference archives are hash-bound in
the EXP-129 manifest. Their combined numerical-sensitivity ranges are:

| Frozen class | `y` slope range | `z` slope range |
|---|---:|---:|
| published two, `a=0.118` | `[-2.0744,-1.3869]` | `[-2.7153,-1.8357]` |
| published three, `a=0.149` | `[0.4629,0.8190]` | `[0.4983,1.0710]` |
| local two, `a=0.148` | `[-1.2459,-0.5227]` | `[-1.6051,-0.8700]` |
| local three, `a=0.14825` | `[0.3715,0.7472]` | `[0.6617,1.0273]` |

## Consequences

- EXP-129 passes its held-out test: all 60 target slopes are negative and
  predict the two-branch count independently returned by all 60 critical-point
  cells. The calibration rows themselves are not held-out evidence.
- The slope is a continuous-valued companion observable, but continuity in a
  parameter, existence or uniqueness of a zero, and smoothness of its zero set
  remain empirical questions.
- The statistic and branch oracle share PIM states and spline variants. Their
  agreement is predictive at the label level but not structurally independent
  reconstruction evidence.
- The value is bounded to the declared Barrio section and scalar coordinates;
  it is not a coordinate-free topological invariant.
- Only after held-out midpoint success should the statistic be sampled on a
  parameter mesh, root-bracketed, and continued with independent validation
  points to build a candidate TBA curve.

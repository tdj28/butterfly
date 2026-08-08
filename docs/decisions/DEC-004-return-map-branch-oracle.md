# DEC-004 — Define branch count as a gated scalar return-map observable

Date: 2026-08-07
Status: adopted; Jones-section and published-section controls qualified

## Context

Jones's two/three-branch claim cannot be tested by visually counting turns in
a projected trajectory or by counting crossings of an arbitrarily truncated
section. EXP-055 already proves that the historical crossing count can change
through section-boundary grazing while the flow orbit stays stable. The referee
also correctly objected to treating an abstract branched manifold as a physical
object deposited in phase space.

## Decision

For each frozen section and scalar coordinate `u`, define the observed return
relation from consecutive crossings as `(u_n,u_{n+1})`. A branch count is
reported only when all of the following pass:

1. the occupied bins cover a declared fraction of the invariant sample domain;
2. the conditional robust spread of `u_{n+1}` at fixed `u_n` is small enough
   that the scalar projection is graph-like;
3. a smoothed, normalized relation has interior derivative zeros whose
   prominence exceeds a frozen fraction of the return range; and
4. bootstrap resampling retains the same critical-point count with a frozen
   consensus.

The branch count is one plus the retained critical-point count. Failed
graph-likeness, coverage, prominence, or bootstrap gates produce `unresolved`,
not a forced one/two/three-branch label. Critical points are returned in the
original coordinate.

## Calibration and next gate

`butterfly.return_map.infer_return_map_branches` passes deterministic synthetic
controls for monotone (one branch), logistic (two branches), cubic (three
branches), and deliberately multivalued (unresolved) relations. These tests
validate implementation behavior, not a Rössler topology claim.

The first Rössler experiment must freeze the section, scalar coordinate,
transient, sample count, binning, smoothing, prominence, graph-likeness,
coverage, and bootstrap thresholds. It must include at least one section
perturbation and retain unresolved outcomes. Only after calibration may the
oracle be continued as a transition curve across parameter space.

EXP-106 performs that first application and falsifies its frozen two-branch
expectation: all three nearby section offsets robustly return three branches
with full coverage and 100/100 bootstrap agreement. This supports a sharp,
reproducible local three-branch result but does not yet validate coordinate,
orientation, threshold, or parameter robustness. Those sensitivities are
mandatory before transition continuation.

EXP-107 completes those sensitivities for the recovered Jones section. All
negative-oriented `x` and `z` cells retain three branches, while the opposite
half-plane is not a stable scalar graph. The qualified claim is therefore
representation-bounded. Direct source inspection also establishes that the
Barrio PRL uses a different section, `x=x_minus` with `dx/dt>0`. EXP-108 must
qualify the PRL's reported two- and three-branch controls on that declared
section before any TBA boundary continuation. The two section-specific curves
will be compared rather than assumed identical.

EXP-108 passes all 84 cells: the primary `y` and cross-check `z` maps both give
two branches at the published `a=0.11` control and three at `a=0.2`, across
three plane offsets and seven oracle settings. This authorizes a prospective
boundary search on the published section. It does not authorize interpolation
through periodic windows; those require the chaotic saddle used in the PRL.

After independent PIM continuation localizes a regular-window saddle change to
`a in [0.148,0.14825]`, DEC-010 adds a signed lower-support derivative as a
companion to this discrete count. It reuses the declared spline family but
does not replace any graph-likeness, coverage, prominence, bootstrap, censor-
horizon, or coordinate gate.

## Consequences

- RVR-003 is now mathematically operational but remains empirically open.
- A branch transition is distinct from the EXP-055 section-boundary grazing
  unless both observables coincide under section perturbation.
- Reinjection in RVR-005 will be defined relative to retained branches and
  critical values from this oracle, not an informal phase-space angle.

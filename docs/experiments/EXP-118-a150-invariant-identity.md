# EXP-118 — Adjacent `a=0.150` invariant-set identity audit

Status: preregistered; not executed

## Question

Is EXP-109's two-branch `a=0.150` aperiodic candidate a persistent chaotic
invariant set, or does burn-in, basin choice, or finite-time classification
explain its contrast with the qualified three-branch saddle at `a=0.149`?

## Frozen datasets

At `b=0.2,c=20`, use the published section and DOP853 throughout. From the
original `[0,4,0]` initial state, collect 1200 returns after burn-ins of
1000, 3000, 5000, and 10000 time units. At the 10000-unit burn-in, repeat with
four independently frozen scrambled-Sobol states on the section. No expected
branch label is present in the manifest.

Every dataset must remain nonperiodic under the period-through-64 recurrence
test, provide at least 1000 return pairs, and resolve to one common allowed
branch count in both `y` and `z`. Each scalar decision uses the full 15-variant,
50-bootstrap local-uncertainty oracle qualified for the saddle controls.
Within-dataset critical span must be at most `0.03`; across all eight datasets
it must be at most `0.04`.

## Independent chaos gate

For the original and first Sobol state, compute an eight-block, 1600-time-unit
Float64 variational/QR Lyapunov spectrum after a 10000-unit transient. Combine
it with recurrence using the uncertainty-aware dynamics classifier. Both must
classify chaotic, satisfy the divergence-trace identity to `1e-6`, and agree
with an independent two-trajectory largest exponent within `0.03`.

## Interpretation

A pass would qualify a persistent local chaotic topology at `a=0.150` across
the declared burn-in and basin perturbations. If the common count is two, the
`0.149/0.150` contrast is real at this resolution and a single monotone
continuation cannot be assumed. It would not by itself distinguish a second
TBA crossing, an invariant-set crisis/selection event, or a limitation of the
scalar projection; those require parameter refinement and two-dimensional-map
tests. Failure is retained by the first recurrence, topology, support,
critical-drift, or Lyapunov gate.

Immutable manifest:
`experiments/manifests/EXP-118-a150-invariant-identity.json`.

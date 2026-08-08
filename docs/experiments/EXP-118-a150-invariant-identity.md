# EXP-118 — Adjacent `a=0.150` invariant-set identity audit

Status: executed; failed full gate with persistent-chaos and resolution diagnosis

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

## Result

The clean run at `3f351d9` completed in `214.11 s` and failed. All eight
datasets integrate successfully, supply 1200 crossings, and remain
nonperiodic. Both Lyapunov cases classify chaotic; variational largest
exponents `0.06762,0.06204` agree with independent estimates
`0.05974,0.07068` within `0.00865`. They miss only the frozen `1e-6`
trace-identity sub-gate, with errors `2.80e-6,2.74e-6`.

The full topology gate fails because bin resolutions disagree. The pattern is
consistent across burn-in, seed, and coordinate: 46/48 20-bin cells return two,
while 189/192 30--80-bin cells return three; the other five cells are
unresolved, and no vote crosses those resolution groups in the opposite
direction. The old `a=0.150` two-branch label is therefore not robust under the
qualified local oracle. EXP-118 does not promote three branches either; a
prospective resolution-convergence successor is required. Raw receipt SHA-256:
`fec3f8d9c06b4cf670938f9d17ea97c18a2a4a0e23ec9af80fe43b597da2e9bc`.

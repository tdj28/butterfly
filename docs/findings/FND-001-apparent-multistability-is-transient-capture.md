# FND-001 — Apparent multistability resolves into long transient capture

Status: reproduced for two sampled Jones-hub parameter points; mechanism
supported but not yet directly reconstructed
Last updated: 2026-08-06
Primary evidence: EXP-010 through EXP-012
Related claims: CLM-013, CLM-015, and CLM-017

## Headline finding

At two parameter points near the Jones periodicity hub, short and intermediate
simulations appeared to show coexistence between periodic and chaotic
attractors. Longer integrations rejected that interpretation for the sampled
initial conditions. Both trajectories ultimately converged to the same stable
periodic orbit; one trajectory merely remained irregular for thousands of time
units before capture.

The defensible conclusion is:

> Persistent multistability is rejected at the two tested Jones-hub points. The
> evidence instead supports long chaotic-transient capture, consistent with a
> nonattracting chaotic-saddle mechanism.

“Consistent with” is essential. The project has not yet directly reconstructed
or certified the nonattracting chaotic saddle.

## What was observed

EXP-010 used two initial conditions and a finite observation horizon. It found
one trajectory classified as chaotic and the other periodic at each of two
points:

- `(a,b,c)=(0.17675,0.2,10.42)`, with an apparent period-8/chaotic split; and
- `(a,b,c)=(0.18475,0.2,10.35)`, with an apparent period-6/chaotic split.

EXP-011 confirmed that the period-6 orbit was a genuine stable periodic orbit,
including recurrence, flow closure, and Floquet evidence. It did not establish
that the apparently chaotic trajectory remained chaotic asymptotically.

EXP-012 then evaluated both initial conditions after progressively longer
transients:

| Parameter point | Initially slow-capturing trajectory | Other trajectory | Final result |
| --- | --- | --- | --- |
| period-8 point | unresolved through 3,200; period 8 by 6,400 | period 8 throughout | both period 8 at 12,800 |
| period-6 point | unresolved through 1,600; period 6 by 3,200 | period 6 throughout | both period 6 at 12,800 |

Thus the apparent basin split was a finite-time artifact: different initial
conditions produced dramatically different capture times, not different
demonstrated asymptotic attractors.

## Dynamical interpretation

A chaotic attractor retains nearby typical trajectories indefinitely. A
nonattracting chaotic saddle can instead organize irregular motion for a long
time while trajectories eventually escape toward another attractor. A finite
trajectory shadowing such a saddle can have positive finite-time Lyapunov
evidence and a chaotic-looking return map even though its asymptotic attractor
is periodic.

The observed combination—long irregular motion, positive finite-time
instability, and eventual convergence to a stable periodic orbit—is the pattern
expected from chaotic-saddle capture. Direct saddle reconstruction remains the
decisive missing test. Candidate methods include sprinkler sampling, edge
tracking, periodic-orbit extraction within the transient set, and computation
of stable and unstable manifolds.

## Consequences for the Jones paper

This finding does not undermine the existence of the periodicity hub, shrimp
windows, or the stable period-6 and period-8 orbits. Those parts are retained
and, for the sampled orbits, strengthened.

It does require a narrower interpretation of finite-time parameter maps:

- a pixel that appears chaotic after one declared transient is not necessarily
  an asymptotically chaotic attractor;
- dark or “chaotic/divergent” pixels near regular windows may include long
  transient capture and must not be merged into one class;
- return maps measured during the transient may describe a nonattracting
  invariant set rather than the asymptotic periodic attractor; and
- claims about structures continuing through regular windows require the
  nonattracting invariant set to be tracked explicitly.

Jones's stable-period ordering and reinjection hypotheses are not rejected by
this result. They now require validation using orbit continuation and
invariant-set diagnostics rather than finite-time raster colors alone.

## Relationship to Barrio, Blesa, and Serrano

Barrio, Blesa, and Serrano explicitly reported transient chaos inside regular
regions and attributed it to nonattracting chaotic saddles coexisting with
stable periodic orbits. They used that distinction to continue chaotic-set
topology through parameter regions where no chaotic attractor exists.

The present result independently reproduces the time-domain signature at
different parameters near the Jones hub. It therefore strengthens the view
that the two 2012 contributions are complementary:

- Jones mapped stable periodic organization, period ordering, mutant-shrimp
  connectivity, and a proposed reinjection mechanism; while
- Barrio, Blesa, and Serrano supplied the invariant-set distinction needed to
  follow chaotic topology through regular windows.

This corroborates their mechanism qualitatively. It does not yet reproduce
their saddle reconstruction, topology-bifurcation axis, superstability
tangency, or same-side topology claims.

## Implications for the expanded atlas

EXP-014 found four new finite-time outcome splits in the high-`a` region. They
were deliberately recorded as apparent or finite-time multistability, not as
persistent coexistence. EXP-015 subsequently resolved three of the four splits
into common periodic capture. A fifth boundary case also reached common period
2. The remaining point `(a,b,c)=(0.245,0.2,5.75)` retained distinct period-12
and period-3 cycles for both sampled basins at every checkpoint through
transient 19,200. EXP-016 now tests the closure and Floquet stability of both
cycles; this candidate must not be conflated with the rejected Jones-hub cases.

The atlas classification hierarchy is therefore:

1. periodic recurrence is a finite-time candidate;
2. an apparently chaotic trajectory is not an attractor claim;
3. differing initial-condition outcomes trigger a capture-time study;
4. common eventual periodic capture rejects persistent multistability for the
   sampled initial conditions;
5. surviving differences justify basin-boundary and exact-attractor analysis;
   and
6. a chaotic-saddle claim requires direct invariant-set reconstruction.

This hierarchy prevents the expanded `(a,c)` and future `(a,b,c)` atlas from
turning transient lifetime into a false attractor taxonomy.

## Evidence boundary

Established:

- the two tested Jones-hub trajectories with different finite-time labels
  eventually converge to the same stable periodic orbit;
- at least one initial condition at each point experiences a very long
  irregular transient; and
- the simple persistent-multistability interpretation is false for those
  initial-condition probes over the tested horizon.

Not yet established:

- existence and numerical reconstruction of the responsible chaotic saddle;
- a survival-time distribution or escape rate;
- the measure or geometry of the slow-capture initial-condition set;
- absence of every other attractor or persistent basin at those parameters;
- universality of the mechanism throughout the hub or high-`a` plane; or
- Barrio's stronger topological-continuation claims.

## Source records

- [`EXP-010`](../experiments/EXP-010-candidate-confirmation.md): original
  finite-time multistability candidates.
- [`EXP-011`](../experiments/EXP-011-focused-multistability.md): focused
  recurrence, Lyapunov, and Floquet qualification.
- [`EXP-012`](../experiments/EXP-012-transient-capture.md): decisive
  long-transient convergence test.
- [`EXP-014`](../experiments/EXP-014-wide-target-qualification.md): analogous
  apparent cases in the high-`a` atlas.
- [`EXP-015`](../experiments/EXP-015-high-a-transient-checkpoints.md): long-
  transient resolution of the high-`a` cases, retaining one distinct-period
  candidate.
- [`EXP-016`](../experiments/EXP-016-periodic-coexistence-floquet.md): closure
  and Floquet gate for the retained period-12/period-3 candidate.
- [`Claim ledger`](../claim-ledger.md): authoritative status of CLM-015 and
  related claims.

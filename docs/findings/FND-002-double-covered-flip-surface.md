# FND-002 — The apparent unit-multiplier surface is a fundamental flip surface

Status: reproduced at three separated points, including a parameter-space fold
Last updated: 2026-08-06
Primary evidence: EXP-028 through EXP-041
Related claims: CLM-012 and CLM-020

## Headline finding

The periodic-orbit surface first detected as a nontrivial `+1` Floquet event is
not evidence for an unknown pitchfork symmetry. The parent orbit had been shot
over twice its fundamental period. At half the stored period it closes and has
a transverse multiplier `-1`; over the doubled traversal that multiplier
squares to `+1`.

The defensible conclusion is:

> The continued event set is a fundamental period-doubling (flip) surface. Its
> apparent `+1`, square-root branch opening, ratio-two multiplier scaling, and
> two switched arms are the expected double-cover representation of a
> supercritical flip and its single period-doubled offspring.

This is good news for the Jones program. It replaces an unexplained numerical
symmetry with the standard local bifurcation at the heart of period-doubling
cascades and gives the first explicit orbit-defined bifurcation surface in the
expanded `(a,b,c)` investigation.

## Evidence chain

EXP-023 and EXP-024 first bracketed and refined several ordinary `-1`
period-doubling events. EXP-025 through EXP-028 then isolated a smooth
period-5-family event whose nontrivial multiplier appeared at `+1` when the
orbit was represented with stored period about `33.8`.

EXP-029 and EXP-030 switched branches and demonstrated that, above the event,
there are two distinct geometric cycles with a stability exchange. EXP-031,
EXP-039, and EXP-040 prospectively reproduced square-root branch separation,
multiplier-deviation ratio near two, and stability exchange at the source, a
separated `c=4.9` point, and the event curve's minimum-`b` fold. Those results
were initially described as “pitchfork-like” because the double cover had not
yet been recognized.

EXP-041 tested the multiple-cover explanation directly at those same three
events. At all three:

- the orbit closes at exactly half the stored shooting period;
- the half-period nontrivial multiplier is `-1` to within `3.87e-10`;
- the doubled-period multiplier is `+1` to within `2.57e-11`;
- the doubled monodromy agrees numerically with the square of the half-period
  monodromy; and
- no tested divisor from three through ten produces another closure.

This is an algebraic and dynamical identity, not merely a visual resemblance.

## Why the earlier measurements looked like a pitchfork

For a fundamental Poincare return map, a flip has the local form

`x_next = -(1 + alpha*mu)x + beta*x^3 + ...`.

Its second iterate removes the leading sign reversal. In the doubled-period
shooting representation, the parent therefore has an apparent `+1` critical
multiplier, the period-doubled child appears as two phase-shifted fixed points,
and its amplitude opens like `sqrt(mu)`. The familiar ratio-two stability
scaling also belongs to this second-iterate normal form.

The two branch-switch signs in EXP-029/030/031/039/040 are consequently not two
different child cycles and do not require a spatial reflection symmetry. They
are the same doubled cycle viewed from points separated by one parent period.

## Consequences for Jones

The result strengthens several parts of the Jones interpretation:

- it connects the numerically continued surface directly to period-doubling
  cascades rather than to a new, unexplained bifurcation class;
- it supplies a concrete way for one folded stability boundary to intersect a
  two-parameter slice several times, helping organize repeated window edges;
- it makes continuation of flip surfaces a principled route for tracking how
  shrimp and hubs move as `b` changes; and
- it turns the descriptive raster geometry into an orbit-defined object that
  can be compared quantitatively with window boundaries and return-map
  topology.

It does not yet prove that this one surface explains the entire Jones hub, all
shrimp beyond `a=0.22`, or the whole `(a,c)` superstructure. Multiple orbit
families and multiple flip surfaces are expected. The global claim requires
surface continuation, family identification, and comparison against the atlas.

## Relationship to the 2012 papers

Jones emphasized stable-period organization, period-doubling sequences, and
the geometry of shrimp/hubs. Barrio, Blesa, and Serrano emphasized topology
changes of the chaotic invariant set and the distinction between attractors
and nonattracting chaotic saddles. The present flip-surface result is most
directly an orbit-level strengthening of Jones's period-doubling organization;
the transient-capture result in FND-001 supplies the complementary connection
to Barrio, Blesa, and Serrano.

These are treated in this repository as independent co-discoveries with
complementary emphases. Jones's arXiv preprint predates the publication of the
Barrio–Blesa–Serrano paper; no priority claim beyond the documented record is
made here.

## Evidence boundary and next tests

Established numerically:

- the three tested `+1` events are double-covered fundamental flips;
- the local branch opening is supercritical at those three points;
- the event curve has projection folds; and
- a 45-point local event-surface patch has been corrected successfully.

Not yet established:

- direct half/full-period classification of the offspring on both sides at all
  three points;
- rigorous or interval validation of a flip point;
- uniform bifurcation type over the full surface;
- global continuation or the number/connectivity of flip surfaces;
- alignment with TBA, TTL, caustics, and window boundaries; or
- sufficiency of these surfaces to explain the entire `(a,c)` atlas.

The immediate independent check is a frozen offspring-period audit. The next
global step is fold-safe continuation of flip surfaces and their overlays on
the multi-`b` atlas.

## Source records

- [`EXP-028`](../experiments/EXP-028-period5-unit-multiplier.md): original
  doubled-period coupled event solve.
- [`EXP-030`](../experiments/EXP-030-period5-orbit-identity.md): distinct parent
  and offspring cycles modulo phase.
- [`EXP-031`](../experiments/EXP-031-period5-normal-form-scaling.md),
  [`EXP-039`](../experiments/EXP-039-separated-normal-form.md), and
  [`EXP-040`](../experiments/EXP-040-fold-normal-form.md): prospective local
  scaling and stability exchange at three points.
- [`EXP-035`](../experiments/EXP-035-event-pseudo-arclength.md) and
  [`EXP-038`](../experiments/EXP-038-resolved-period5-unit-event-surface-patch.md):
  folded curve and local surface geometry.
- [`EXP-041`](../experiments/EXP-041-double-cover-audit.md): decisive
  half-period closure, flip multiplier, and monodromy-square audit.

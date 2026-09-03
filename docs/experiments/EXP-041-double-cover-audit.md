# EXP-041 — Double-cover and fundamental flip audit

> **Identity refinement after EXP-047.** The fundamental parent/child periods
> are 3 and 6 under the legacy Poincare section.

Status: executed; passed
Manifest: `experiments/manifests/EXP-041-double-cover-audit.json`
Claim target: correct classification of the EXP-028/031/039/040 event

## Motivation, hypothesis, and method

A disclosed post-EXP-040 design diagnostic found closure at half the stored
shooting period near `1e-10` for all three qualified events. The prospective
hypothesis is therefore that the apparent nontrivial `+1` surface is the
double-covered representation of a fundamental period-doubling surface.

At the original, separated-`c`, and minimum-`b` fold events, reintegrate with a
tighter solver. Test closure at `T/2`; compute half- and full-period monodromy;
require a nontrivial half-period multiplier at `-1`, the corresponding
full-period multiplier at `+1`, and agreement of the full monodromy with the
square of the half-period monodromy. Evaluate closures at `T/d` for frozen
divisors `d=3..10` to exclude a still shorter integer-divisor traversal.

## Acceptance and implications

At all three events: half closure must be at most `1e-8`; distances to `-1` and
`+1` at most `1e-7`; the monodromy-square residual at most `1e-7`; and every
other tested divisor closure at least `1e-3`.

Passing reclassifies the mechanism as a supercritical period-doubling (flip) of
the fundamental cycle, represented as a pitchfork-like `+1` branch point only
because the parent was shot over twice its fundamental period. It would explain
the square-root opening, ratio two, half-period phase copies, and stability
exchange without invoking an unknown spatial symmetry. It still does not prove
surface-wide topology/TBA alignment or validate the bifurcation rigorously.

## Result

The clean execution at commit `447540551612e776bc0fbb06846b392da9f88a40`
passed every frozen gate at all three prospectively selected events. The stored
periods close at one half to between `1.96e-11` and `5.16e-10`. Their
nontrivial half-period multipliers differ from `-1` by between `1.82e-12` and
`3.86e-10`; the corresponding full-period multipliers differ from `+1` by at
most `2.57e-11`. Full monodromy agrees with the square of half-period
monodromy to between `1.28e-10` and `1.19e-9`.

Closures at every other frozen integer divisor `d=3..10` remain large: the
smallest is `2.9277`. Thus the half-period traversal is not itself an obvious
multiple cover under the tested divisors. The complete receipt SHA-256 is
`66cc557c0c554d2c47ea1fe42cf2ff274840f13ca2d9c230257c331bc84b5e88`.

| Event | `(a,b,c)` | Fundamental-period candidate | Half closure | `|-1-lambda_half|` | Monodromy-square residual |
| --- | --- | ---: | ---: | ---: | ---: |
| source | `(0.245,0.2722840598,5.1)` | `16.89503874` | `1.96e-11` | `1.02e-11` | `2.42e-10` |
| separated | `(0.245,0.2975539193,4.9)` | `16.95784609` | `1.96e-11` | `1.82e-12` | `1.28e-10` |
| minimum-`b` fold | `(0.2185131281,0.2031697977,5.1)` | `17.11534595` | `5.16e-10` | `3.86e-10` | `1.19e-9` |

## Decision

Reclassify the EXP-028/031/039/040 mechanism as a supercritical fundamental
period-doubling, or flip, represented in the original shooting calculations
over twice the parent orbit's fundamental period. In that doubled
representation, the flip multiplier is squared from `-1` to `+1`, and the two
apparently symmetric switched arms are half-period phase copies of the single
period-doubled child cycle.

This resolves the previously open symmetry question without requiring an
unknown spatial symmetry. It strengthens rather than weakens the connection to
Jones: the continued folded surface is now an orbit-defined period-doubling
surface, the precise local instability used to organize period-doubling
cascades and periodic-window boundaries. The remaining gaps are direct
fundamental-period checks of offspring cycles, validated numerics, global
surface continuation, and comparison with TBA and atlas geometry.

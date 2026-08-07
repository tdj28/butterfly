# EXP-041 — Double-cover and fundamental flip audit

Status: preregistered after design diagnostic; pending clean execution
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

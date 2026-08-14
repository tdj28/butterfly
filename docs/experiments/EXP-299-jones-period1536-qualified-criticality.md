# EXP-299 — Two-solver criticality audit of the seventh birth

Status: frozen before execution

EXP-298 supplies two passed period-1536 sign representations at one coordinate.
EXP-299 prospectively selects the positive sign only because it has the larger
half-period closure within the frozen pair. Its preliminary multiplier is not a
selection gate.

DOP853 and Radau independently correct the 1,024-segment parent and
2,048-segment child at fixed `a=0.24070100823781396`. Both solvers must pass
matching, phase, cyclic node identity, multiplier-spread, child half-period
nonclosure, and exact `1792/2048` section identity gates. Consistent
parent-unstable/child-stable or parent-stable/child-unstable classifications
pass; an unresolved or mixed result fails.

A pass qualifies the sampled local birth as supercritical or subcritical. It
does not yet establish tangent-sign equivalence, basin measure, continued
period-1536 attraction, or an eighth event.

Manifest:
[`../../experiments/manifests/EXP-299-jones-period1536-qualified-criticality.json`](../../experiments/manifests/EXP-299-jones-period1536-qualified-criticality.json).

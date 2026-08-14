# EXP-310 — Independent period-3072 stability exchange

Status: frozen before execution

EXP-309 nominates two primitive period-3072 candidates. EXP-310 selects the
negative sign solely by its larger direct half-period nonclosure and
independently corrects the period-1536 parent and period-3072 child at their
common coordinate under DOP853 and Radau.

Matching, phase, cross-solver node identity, multiplier spread, child
nonclosure, classification margin, and exact `3584/4096` section identities
are mandatory. Either consistent parent-unstable/child-stable or
parent-stable/child-unstable exchange passes; mixed or unresolved fails.

A pass qualifies the sampled eighth-birth direction only. It does not
establish sign equivalence, basin measure, a global stable child branch, or a
ninth event.

Manifest:
[`../../experiments/manifests/EXP-310-jones-period3072-qualified-criticality.json`](../../experiments/manifests/EXP-310-jones-period3072-qualified-criticality.json).

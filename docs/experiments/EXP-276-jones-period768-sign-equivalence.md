# EXP-276 — Period-768 tangent-sign equivalence

Status: frozen — not yet executed

EXP-274 produces period-768 candidates from both signs of the exact
anti-periodic period-384 tangent. EXP-276 corrects both signs at their frozen
mean coordinate `a=0.24070100827079027` under DOP853 and Radau, then compares
the complete 1,024-segment orbits with bounded continuous phase minimization
and 16,384 phase samples.

Matching, phase, endpoint, period, multiplier, stability, half-period
primitivity, within-solver sign identity, and cross-solver identity gates are
fixed before execution. A pass establishes that both switch signs represent
one stable primitive period-768 orbit up to phase. It does not establish basin
measure, deeper continuation, another event, a limiting scaling law, or any
global shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-276-jones-period768-sign-equivalence.json`](../../experiments/manifests/EXP-276-jones-period768-sign-equivalence.json).

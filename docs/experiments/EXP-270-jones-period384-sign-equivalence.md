# EXP-270 — Period-384 tangent-sign equivalence

Status: frozen — not yet executed

EXP-268 produces period-384 candidates from both signs of the exact
anti-periodic period-192 tangent. EXP-270 corrects both signs at their frozen
mean coordinate `a=0.24070100850360543` under DOP853 and Radau, then compares
the complete 512-segment orbits with bounded continuous phase minimization and
8,192 phase samples.

Matching, phase, endpoint, period, multiplier, stability, half-period
primitivity, within-solver sign identity, and cross-solver identity gates are
fixed before execution. A pass establishes that both switch signs represent
one stable primitive period-384 orbit up to phase. It does not establish basin
measure, deeper continuation, another event, a limiting scaling law, or any
global shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-270-jones-period384-sign-equivalence.json`](../../experiments/manifests/EXP-270-jones-period384-sign-equivalence.json).

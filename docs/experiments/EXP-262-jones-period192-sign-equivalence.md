# EXP-262 — Period-192 tangent-sign equivalence

Status: frozen — not yet executed

EXP-260 produces period-192 candidates from both signs of the exact
anti-periodic period-96 tangent. EXP-262 corrects both signs at their frozen
mean coordinate `a=0.24070100959763152` under DOP853 and Radau, then compares
the complete segmented orbits with bounded continuous phase minimization.

The phase method is declared prospectively because EXP-254/256 already showed
that a refined grid can resolve the correct half-period basin but stop above
the orbit-identity threshold. Matching, phase, endpoint, period, multiplier,
stability, half-period primitivity, within-solver sign identity, and
cross-solver identity gates are fixed before execution.

A pass will establish that both switch signs represent one stable primitive
period-192 orbit up to phase. It will not establish basin measure, deeper
continuation, another event, a limiting scaling law, or any global
shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-262-jones-period192-sign-equivalence.json`](../../experiments/manifests/EXP-262-jones-period192-sign-equivalence.json).

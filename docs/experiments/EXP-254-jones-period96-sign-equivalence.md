# EXP-254 — Period-96 tangent-sign equivalence

Status: frozen — not yet executed

EXP-252 produces period-96 candidates on both signs of the exact
anti-periodic tangent. EXP-254 corrects both signs to their frozen mean
coordinate `a=0.24070101600213994` under DOP853 and Radau, then compares the
full continuous segmented orbits after independently refined phase alignment.

Matching, phase, segment endpoint, period, multiplier, stability, and
half-period primitivity gates are explicit. A pass establishes that both signs
are one stable primitive period-96 orbit up to phase, not two nearby cycles.
It does not establish basin measure, the next flip, a limiting scaling law, or
any global shrimp/TBA claim.

Manifest:
[`../../experiments/manifests/EXP-254-jones-period96-sign-equivalence.json`](../../experiments/manifests/EXP-254-jones-period96-sign-equivalence.json).

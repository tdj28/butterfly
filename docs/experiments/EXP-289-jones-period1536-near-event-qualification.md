# EXP-289 — Near-event period-1536 qualification

Status: frozen — not yet executed

EXP-288 nominates six primitive period-1536 candidates but their preliminary
long-product multipliers are representation-conditioned. EXP-289
prospectively selects the largest-predictor positive candidate because it has
the largest half-period separation and best direct closure/neutral residual of
that bilateral pair; its preliminary stability label is explicitly not part
of the selection rule.

DOP853 and Radau independently correct the 1,024-segment parent and
2,048-segment child at the candidate's common `a`. Both must agree on a
resolved parent/child stability exchange, retain solver node identity, child
half-period nonclosure, and exact `1792/2048` section identity, and pass the
unchanged `0.02` multiplier-spread gate. Either a consistent supercritical or
consistent subcritical result passes; a mixed, neutral, or otherwise
unresolved classification fails. This avoids encoding the desired Jones
outcome in the acceptance criterion.

Manifest:
[`../../experiments/manifests/EXP-289-jones-period1536-near-event-qualification.json`](../../experiments/manifests/EXP-289-jones-period1536-near-event-qualification.json).

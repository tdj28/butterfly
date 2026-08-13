# EXP-288 — Segmented period-1536 switch

Status: frozen — not yet executed

EXP-287 independently qualifies the period-768 event represented by EXP-281.
EXP-288 doubles its 1,024 event nodes and switches along both signs of the exact
anti-periodic tangent using 2,048 shooting segments. The three predictor
lengths (`0.0000625`, `0.000125`, and `0.00025`) and every acceptance gate are
frozen before execution.

The correction uses the same analytic multiple-shooting Jacobian as earlier
rungs, stored as CSR rather than a dense 6,146-column matrix. This is a scaling
change, not a mathematical-method change. A dense-versus-sparse regression
test must pass before launch.

Matching, phase, full/half closure, neutral mode, half-node separation,
parameter displacement, period ratio, and exact `1792/2048` section identity
are mandatory. At least two bilateral candidates must pass. A pass only
nominates primitive period-1536 candidates; independent stability exchange and
criticality remain separate.

Manifest:
[`../../experiments/manifests/EXP-288-jones-period1536-segmented-switch.json`](../../experiments/manifests/EXP-288-jones-period1536-segmented-switch.json).

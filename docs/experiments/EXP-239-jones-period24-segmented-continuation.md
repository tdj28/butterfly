# EXP-239 — Segmented period-24 continuation

Status: frozen — not yet executed

EXP-238 nominates primitive period-24 candidates on both signs, but they lie
only `3.22e-10` in `a` from the singular event. EXP-239 selects the negative
mode at frozen predictor length `0.002` and continues it for up to 20
pseudo-arclength steps of nominal length `0.02`, with adaptive halving only on
corrector failure.

The run must retain multiple-shooting matching and half-node separation at
every point, span at least `2e-6` in `a`, and finish with low full-period and
neutral residuals, period-24 half-period nonclosure, and exact `28/32` section
identity. A pass provides a well-separated endpoint for independent
two-solver, sign-equivalence, stability-exchange, and attraction tests.

Manifest:
[`../../experiments/manifests/EXP-239-jones-period24-segmented-continuation.json`](../../experiments/manifests/EXP-239-jones-period24-segmented-continuation.json).

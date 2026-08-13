# EXP-268 — Segmented period-384 switch

Status: frozen — not yet executed

EXP-268 doubles EXP-267's exact 256-node period-192 event representation and
switches along both signs of its qualified anti-periodic tangent using 512
shooting segments. Three predictor lengths (`0.00025`, `0.0005`, `0.001`) are
frozen before execution.

Matching, phase, full/half closure, neutral, half-node separation, parameter
displacement, period ratio, and exact `448/512` section identity are mandatory.
At least two candidates must pass. A pass only nominates period-384 orbits for
independent stability and sign-equivalence tests.

Manifest:
[`../../experiments/manifests/EXP-268-jones-period384-segmented-switch.json`](../../experiments/manifests/EXP-268-jones-period384-segmented-switch.json).

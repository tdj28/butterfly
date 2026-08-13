# EXP-274 — Segmented period-768 switch

Status: frozen — not yet executed

EXP-274 doubles EXP-273's exact 512-node period-384 event representation and
switches along both signs of its qualified anti-periodic tangent using 1,024
shooting segments. Three predictor lengths (`0.000125`, `0.00025`, `0.0005`)
are frozen before execution.

Matching, phase, full/half closure, neutral, half-node separation, parameter
displacement, period ratio, and exact `896/1024` section identity are
mandatory. At least two candidates must pass. A pass only nominates
period-768 orbits for independent stability and sign-equivalence tests.

Manifest:
[`../../experiments/manifests/EXP-274-jones-period768-segmented-switch.json`](../../experiments/manifests/EXP-274-jones-period768-segmented-switch.json).

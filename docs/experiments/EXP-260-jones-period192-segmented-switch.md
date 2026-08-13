# EXP-260 — Segmented period-192 child switch

Status: frozen — not yet executed

EXP-259 supplies the exact 128-segment period-96 event and anti-periodic
tangent. EXP-260 doubles it to 256 nodes and opens the child at three frozen
predictor lengths on both tangent signs, with `a` free and
`(b,c)=(0.2,7.625815600403827)` fixed.

Candidates must pass matching, phase, direct closure, neutral, period-ratio,
parameter-displacement, half-period nonclosure, half-node separation, and
exact `224/256` section-identity gates. Survivors are nominations requiring a
separate DOP853/Radau stability-exchange audit; this experiment alone cannot
promote a fourth supercritical rung.

Manifest:
[`../../experiments/manifests/EXP-260-jones-period192-segmented-switch.json`](../../experiments/manifests/EXP-260-jones-period192-segmented-switch.json).

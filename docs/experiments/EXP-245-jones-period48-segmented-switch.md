# EXP-245 — Segmented period-48 child switch

Status: frozen — not yet executed

EXP-244 supplies the exact 32-segment period-24 event and anti-periodic tangent
mode. EXP-245 doubles it to 64 segments and attempts three frozen predictor
lengths on both signs at fixed `(b,c)`, with `a` free to open along the child.

Candidates must pass matching, phase, direct closure, neutral, period-ratio,
parameter-displacement, half-period nonclosure, half-node separation, and
exact `56/64` section-identity gates. Any survivor is a nomination requiring a
separately frozen independent-solver and stability-exchange qualification.

Manifest:
[`../../experiments/manifests/EXP-245-jones-period48-segmented-switch.json`](../../experiments/manifests/EXP-245-jones-period48-segmented-switch.json).

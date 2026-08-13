# EXP-267 — Tighter coupled period-192 flip refinement

Status: frozen — not yet executed

EXP-266 shows that tighter re-evaluation of the immutable EXP-265 variables
does not satisfy the unchanged `1e-7` flip gate. EXP-267 therefore performs a
new coupled orbit, free-`a`, normalized anti-periodic-tangent correction from
those variables, within the original unique bracket.

Both solvers use maximum step `0.01`; the DOP853 corrector tolerance is
`1e-12`. Reference and independent Radau direct-product multipliers must now
both lie within `1e-7` of `-1`, alongside the existing residual, cyclic,
primitivity, and exact `224/256` identity gates. No threshold is relaxed.

A pass qualifies the fifth event only; the period-384 switch remains a
separate prospective experiment.

Manifest:
[`../../experiments/manifests/EXP-267-jones-period192-augmented-flip-refinement.json`](../../experiments/manifests/EXP-267-jones-period192-augmented-flip-refinement.json).

# EXP-356 — Second crossing correction

Status: frozen; not yet run

EXP-355 lowers the fixed-`c` maximum defect to `8.30202e-6`, leaves nine
blocks above the `1e-8` gate, and moves to `a=0.1798386480583239`. Its
optimizer remains actively descending and the nodes are interior.

EXP-356 binds every exact node and repeats the same-`c` correction with the
same physics, tolerances, 128 arcs, node guardrail, 40-evaluation budget, and
scientific threshold. Passing qualifies the curve point; exact fixed `a` is
still a separate successor.

Manifest:
[`../../experiments/manifests/EXP-356-jones-homoclinic-crossing-correction-2.json`](../../experiments/manifests/EXP-356-jones-homoclinic-crossing-correction-2.json).

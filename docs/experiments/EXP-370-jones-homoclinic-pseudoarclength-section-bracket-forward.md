# EXP-370 — Forward-constrained 512-arc section bracket

Status: frozen; not yet run

EXP-369 finds a low-defect root but fails because it corrects backward in `c`.
EXP-370 repeats the same sources, 512-arc subdivision, `Delta c=0.00015`,
solver, manifold, gauge, sensitivity, budget, and acceptance settings. It adds
only an optimizer lower bound requiring `c` to remain at least `1e-6` above
the current EXP-368 coordinate, consistent with the already-frozen forward
direction check.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or
computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-370-jones-homoclinic-pseudoarclength-section-bracket-forward.json`](../../experiments/manifests/EXP-370-jones-homoclinic-pseudoarclength-section-bracket-forward.json).

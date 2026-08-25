# EXP-370 — Forward-constrained 512-arc section bracket

Status: failed; forward bound active

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

EXP-370 reaches the 40-evaluation cap on the new lower `c` bound and fails
three checks: `root_nominated`, `global_status_bound`, and
`optimizer_terminated_or_root_gate`. The final point is
`(a,c)=(0.1798323559761185,10.317082488758269)`, only
`1.63851e-11` inside the directional bound. Maximum matching defect is
`2.2817096038416275e-6`; arclength residual is `2.443558584641625e-10`.

The forced direction does not recover the branch. Together EXP-369/370 show
that the full-state pseudo-arclength hyperplane is contaminated by nuisance
angle/node displacement near the section: unconstrained correction selects a
backward root, while the constrained solve sticks to the forward wall. The
successor must define arclength only in the physical `(a,c)` projection rather
than add another bound or relax a gate.

Raw receipt: `artifacts/EXP-370/receipt.json`, 85,316 bytes, SHA-256
`ff9e29e15516d7481380e1b23348e7a6531f6b6d097a7459862a1445dd77fb7a`.

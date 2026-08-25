# EXP-374 — Reduced-step sparse homoclinic crossing

Status: frozen; not yet run

EXP-373 makes the physical projected arclength equation accurate but misses
the matching gate at its requested `Delta c=0.00015` step. EXP-374 retains its
qualified sources, 512-arc representation, full-state predictor, `(a,c)`
closing plane, common gauge, CSR/regularized-LSMR solve, unit closing-equation
weight, bounds, 40-evaluation budget, and all acceptance thresholds. Only the
desired `c` increment is halved to `7.5e-5`.

From EXP-368, the qualified local slope projects the exact `a=0.1798` crossing
after `Delta c=5.37476e-5`. The reduced step is therefore still a prospective
crossing attempt, not a retreat to another above-section point.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or computer-
assisted existence.

Manifest:
[`../../experiments/manifests/EXP-374-jones-homoclinic-sparse-reduced-step-crossing.json`](../../experiments/manifests/EXP-374-jones-homoclinic-sparse-reduced-step-crossing.json).

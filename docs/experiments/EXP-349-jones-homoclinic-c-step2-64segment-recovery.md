# EXP-349 — Second curve-step 64-arc recovery

Status: frozen; not yet run

EXP-348 remains interior and follows the first homoclinic-curve secant, but its
32-arc correction plateaus at maximum defect `2.51470e-8`. EXP-349 binds that
failure and splits every source arc at a Radau midpoint, producing 64 shorter
arcs at the unchanged `c=10.3144` target.

All physical geometry, Radau tolerances, global-variable bounds, the
40-evaluation budget, and the `1e-8` residual gate are retained. Passing
qualifies the second local curve point; failure remains a conditioning result
and cannot support the historical-path intersection.

Manifest:
[`../../experiments/manifests/EXP-349-jones-homoclinic-c-step2-64segment-recovery.json`](../../experiments/manifests/EXP-349-jones-homoclinic-c-step2-64segment-recovery.json).

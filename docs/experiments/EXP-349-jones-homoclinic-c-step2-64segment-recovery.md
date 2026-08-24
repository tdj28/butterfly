# EXP-349 — Second curve-step 64-arc recovery

Status: completed; preserved residual-floor failure; 128-arc successor required

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

## Result

Doubling segmentation lowers the maximum defect from `2.51470e-8` to
`1.18448e-8` while changing `a` by only `3.13e-14`. All variables remain
interior, but the unchanged `1e-8` gate is missed by `18.45%`; the experiment
therefore remains failed.

The monotone segmentation response motivates one final doubling to 128 arcs,
not a relaxed residual threshold. The hash-bound raw receipt retains the 63
nodes for that successor.

Tracked summary: [`receipts/EXP-349.json`](receipts/EXP-349.json). Raw receipt
SHA-256: `439d3739995a4d9e6d0ecf71cadf87a010877706117bd34569c963a754948329`.

# EXP-321 — Continue the immediate seventh daughter toward the stable target scale

Status: frozen; not yet run

EXP-318--320 distinguish two facts near the seventh event: the immediate
period-1536 daughter is stable and opens toward lower `a`, while EXP-299 also
contains a stable primitive period-1536 orbit slightly above the extrapolated
event. Their global relationship is unknown.

EXP-321 starts from EXP-319's negative-sign children at predictor lengths
`3.125e-5` and `6.25e-5`, forms a normalized secant in all 6,146 orbit,
period, and parameter variables, and takes six exact pseudo-arclength steps of
`3.125e-5`. The 50-digit 4,096-step RK4 3/8 map and five-variable cyclic
Newton elimination are unchanged. Each row records parameter, half-node
amplitude, Floquet stability, any parameter-direction reversal, and the best
cyclic node RMS to EXP-299's stable target.

All rows must close below `1e-20`, grow monotonically in primitive amplitude to
at least `5e-6`, and pass period, cyclic, and neutral gates. The experiment is
outcome-neutral: a fold, stability change, target match, or their absence can
all pass. Any nominated fold or stability bracket requires separate
refinement.

Manifest:
[`../../experiments/manifests/EXP-321-jones-period1536-decimal-sheet-continuation.json`](../../experiments/manifests/EXP-321-jones-period1536-decimal-sheet-continuation.json).

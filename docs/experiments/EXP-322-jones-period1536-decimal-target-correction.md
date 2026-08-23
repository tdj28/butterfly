# EXP-322 — Correct the EXP-299 target in the exact Decimal map

Status: frozen; not yet run

EXP-299 classified a stable period-1536 candidate at
`a=0.24070100823781396`, but its DOP853 solution retained `2.53e-11`
multiple-shooting mismatch and `2.86e-7` direct closure. Those tolerances were
adequate for the earlier Float64 stage but are not commensurate with the
`1e-20` exact-map evidence in EXP-319--321.

EXP-322 uses the exact stored EXP-299 nodes as a fixed-`a` seed in the same
50-digit, 4,096-step RK4 3/8 map as EXP-319 and EXP-321. A four-variable cyclic
Newton reduction solves all 6,144 node corrections and the period while
holding `a`, `b`, and `c` fixed.

The protocol is outcome-neutral. It passes if the orbit closes below `1e-20`
and unambiguously remains primitive period 1536 or collapses to the doubled
period-768 parent. An intermediate amplitude or failed correction is
unresolved. Floquet stability and phase-invariant distances to the original
seed and EXP-321 endpoint are recorded without selecting the outcome.

Manifest:
[`../../experiments/manifests/EXP-322-jones-period1536-decimal-target-correction.json`](../../experiments/manifests/EXP-322-jones-period1536-decimal-target-correction.json).

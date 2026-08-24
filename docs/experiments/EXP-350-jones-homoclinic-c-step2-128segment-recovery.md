# EXP-350 — Second curve-step 128-arc recovery

Status: frozen; not yet run

EXP-349's 64-arc recovery lowers the second curve point to maximum defect
`1.18448e-8`, just above the unchanged gate. EXP-350 binds its exact raw
receipt and splits every arc once more, yielding 128 Radau arcs at unchanged
`(b,c)=(0.2,10.3144)`.

No physical parameter, local bound, solver tolerance, optimization budget, or
acceptance threshold is relaxed. Passing qualifies the second continuation
point; failure blocks the historical-path intersection solve from using it as
a source.

Manifest:
[`../../experiments/manifests/EXP-350-jones-homoclinic-c-step2-128segment-recovery.json`](../../experiments/manifests/EXP-350-jones-homoclinic-c-step2-128segment-recovery.json).

# EXP-350 — Second curve-step 128-arc recovery

Status: passed; second continuation point qualified

EXP-349's 64-arc recovery lowers the second curve point to maximum defect
`1.18448e-8`, just above the unchanged gate. EXP-350 binds its exact raw
receipt and splits every arc once more, yielding 128 Radau arcs at unchanged
`(b,c)=(0.2,10.3144)`.

No physical parameter, local bound, solver tolerance, optimization budget, or
acceptance threshold is relaxed. Passing qualifies the second continuation
point; failure blocks the historical-path intersection solve from using it as
a source.

The local 128-arc Radau run passes at maximum block defect
`6.125992914961101e-9`, down from `1.1844777856244658e-8`, with
`a=0.18069045562126884`. The root remains interior and differs from the
failure-bound 64-arc source by only `1.12496e-12` in `a`. The optimizer reaches
the prospective root gate even though it uses all 40 evaluations; the frozen
acceptance rule explicitly permits this case.

Together with EXP-347, the new qualified secant is
`da/dc=-0.3255310084`, versus `-0.3255142594` for the preceding secant. Its
linear intersection with `a=0.1798` is `c=10.3171353942`. This is a prospective
target for a direct boundary-value solve, not yet evidence that the historical
fixed-`a` path intersects the root curve there.

Raw receipt: `artifacts/EXP-350/receipt.json`, 31,733 bytes, SHA-256
`f9e93a9e593f8c722c97c7fc2fd16a48f8bcc882ae3f18911bf0850e49909b04`.
The raw ignored artifact retains all 127 internal matched nodes for the next
hash-bound continuation run.

Manifest:
[`../../experiments/manifests/EXP-350-jones-homoclinic-c-step2-128segment-recovery.json`](../../experiments/manifests/EXP-350-jones-homoclinic-c-step2-128segment-recovery.json).

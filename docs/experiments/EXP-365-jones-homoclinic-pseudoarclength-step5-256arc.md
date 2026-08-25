# EXP-365 — 256-arc recovery of the fifth pseudo-arclength step

Status: passed

EXP-364 misses the unchanged root gate by `9.33%`, with its error localized in
the first shooting block. EXP-365 repeats the same qualified EXP-362/EXP-363
half-step after deterministically subdividing both exact 128-arc sources to
256 arcs.

Only segmentation changes. The common gauge, desired `Delta c=0.00025`, both
free parameters, Radau/manifold settings, sensitivities, bounds,
40-evaluation budget, and both `1e-8` gates remain fixed. Passing demonstrates
segmentation recovery and qualifies the next curve point; it does not alone
qualify the historical section or establish uniqueness or computer-assisted
existence.

Manifest:
[`../../experiments/manifests/EXP-365-jones-homoclinic-pseudoarclength-step5-256arc.json`](../../experiments/manifests/EXP-365-jones-homoclinic-pseudoarclength-step5-256arc.json).

EXP-365 passes all ten checks with normal `gtol` termination in 11 function
evaluations. The 256-arc point is
`(a,c)=(0.18001520454594663,10.316474198445746)`, with maximum matching defect
`5.165717131432943e-9`, matching-residual norm `1.3844764152467626e-8`, and
arclength residual `-3.795193326272539e-12`. Node margin is `0.89873`.

Segmentation cuts the corresponding EXP-364 controlling defect by `52.75%`
and restores almost a factor-of-two margin below the unchanged gate. The new
slope `-0.3255531864` projects exact `a=0.1798` at `c=10.3171352411`.

Raw receipt: `artifacts/EXP-365/receipt.json`, 42,291 bytes, SHA-256
`315fcd9c4f99101aa10b567e8ff675dbd174ff10bbda499b0a8d2f7b0bef0192`.

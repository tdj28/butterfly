# EXP-365 — 256-arc recovery of the fifth pseudo-arclength step

Status: frozen; not yet run

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

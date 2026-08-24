# EXP-331 — Printed-hub unstable-angle refinement replay

Status: frozen; not yet run

EXP-330 stopped before manifest loading because its tested package import was
not resolvable under direct file execution. EXP-331 changes only the import
fallback needed by `python scripts/refine_jones_homoclinic_unstable_angles.py`.
It retains the same hash-bound EXP-329 source, selected center, 257 angles,
integration settings, candidate thresholds, execution gates, and claim limits.

The run remains a finite discovery/refinement scan. A candidate requires both
a return distance at most `0.01` and stable transverse ratio at most `0.1`, and
would still require an independent boundary-value solve. A null result on the
frozen interval does not reject a homoclinic orbit elsewhere.

Manifest:
[`../../experiments/manifests/EXP-331-jones-homoclinic-unstable-angle-refinement-replay.json`](../../experiments/manifests/EXP-331-jones-homoclinic-unstable-angle-refinement-replay.json).

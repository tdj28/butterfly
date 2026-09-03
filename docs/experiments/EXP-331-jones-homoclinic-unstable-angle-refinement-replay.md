# EXP-331 — Printed-hub unstable-angle refinement replay

Status: passed

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

All 257 departures and return integrations completed in `31.1586` seconds.
No row passed the joint candidate gate. The closest return moved to angle
`4.304350090807109` and distance `0.010451007332282615`, an improvement of
only `2.3624e-5` over the coarse minimum, while remaining
`0.9992956826043482` transverse to the stable direction. The best-aligned row
in the interval was still `0.9970597073293357` transverse. Thus the coarse
near miss does not hide a sampled stable-direction return in the frozen local
window. The rounded source coordinate and unsearched parameter direction keep
CLM-003 open.

Tracked summary: [`receipts/EXP-331.json`](receipts/EXP-331.json). Raw receipt
SHA-256: `8f2b2d23b1bf18b1f974a1148cd7dfda61c7f6e81b7004d6222d7b2ade436f95`.

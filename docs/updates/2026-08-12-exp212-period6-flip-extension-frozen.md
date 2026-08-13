# EXP-212 freezes broad continuation beyond the qualified child sheet

EXP-211 closes the dense sampled child-sheet task on `c=7.18--7.30`, but that
rectangle says nothing about how far its parent flip curve extends. EXP-212
now freezes 100 dual-parameter pseudo-arclength steps from each EXP-206
boundary. Exact second-variational derivatives supply both parameter columns,
and Radau must independently recover both remote terminal events.

The experiment is deliberately a broad-extension test, not an endpoint claim.
If it passes, the next child calculation can sample remote slices before an
endpoint search. If it turns or fails, the retained path supplies a local
seed for fold-safe endpoint refinement.

## Result

The full symmetric gate fails, but the upper result is strong: all 100 points
pass through `c=8.40309`. The lower arm accepts 23 points before the historical
phase count changes from six to seven near `c=6.93246`; the Barrio count stays
eight and the real-`-1` event remains accurate. This nominates a section
grazing, not a flow-orbit endpoint. EXP-213 freezes the continuous tangency
test before refining it.

Receipt: [`../experiments/receipts/EXP-212.json`](../experiments/receipts/EXP-212.json).

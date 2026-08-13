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

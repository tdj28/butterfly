# EXP-227 — Local continuation of the second period-6 flip

Status: frozen — awaiting execution

EXP-226 proves that the stable child strip meets a second period-6 flip on one
fixed offset path. EXP-227 tests whether that crossing belongs to a distinct
local plane curve rather than being an isolated or path-dependent coincidence.

Starting only from the DOP853 endpoint receipt, the exact augmented
orbit--real-`-1` system is solved at 21 fixed `c` values over
`c_root±2e-4`. Every point must pass orbit, phase, event-eigenvector,
normalization, real-multiplier, neutral-multiplier, and `7/8` two-section
identity gates. The candidate must remain at least `5e-8` lower in `a` than
the interpolated EXP-217 returning arm throughout the local grid. Both
endpoints and the center receive independent Radau event correction.

A pass establishes a distinct local second flip curve. It does not establish
broad continuation, close the child sheet globally, connect the curve to
either broad arm, prove paired shrimp boundaries, identify the TBA, or locate
a double-critical center.

Manifest:
[`../../experiments/manifests/EXP-227-second-period6-flip-local-curve.json`](../../experiments/manifests/EXP-227-second-period6-flip-local-curve.json).

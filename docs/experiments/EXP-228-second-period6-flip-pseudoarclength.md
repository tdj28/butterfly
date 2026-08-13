# EXP-228 — Broad second-flip pseudo-arclength continuation

Status: frozen — awaiting execution

EXP-227 qualifies a distinct local second period-6 flip curve. EXP-228 uses
both ends of that receipt to continue 80 exact pseudo-arclength events in each
direction, targeting `c<=7.46` and `c>=7.78`.

Every event must retain strict augmented-system residuals, real-`-1` and
neutral multipliers, historical/Barrio identity `7/8`, bounded parameter
jumps, and at least `5e-8` lower-`a` separation from the interpolated EXP-217
returning arm. Both terminal events receive independent Radau correction.

A pass establishes a broad distinct second flip curve over the sampled range.
It does not establish global closure, connection to either broad arm, a
complete child-sheet boundary, paired shrimp boundaries, TBA membership, or
double-criticality.

Manifest:
[`../../experiments/manifests/EXP-228-second-period6-flip-pseudoarclength.json`](../../experiments/manifests/EXP-228-second-period6-flip-pseudoarclength.json).

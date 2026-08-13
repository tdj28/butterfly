# EXP-228 — Broad candidate-flip pseudo-arclength continuation

Status: complete — failed the frozen distinctness gate

EXP-227 initially appeared to qualify a distinct local period-6 flip curve.
EXP-228 uses both ends of that receipt to continue 80 exact pseudo-arclength
events in each direction, targeting `c<=7.46` and `c>=7.78`. EXP-229 later
retracts the premise after exact same-coordinate comparison.

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

## Result

The broad claim fails after 53 accepted exact events: 30 in the decreasing-`c`
direction and 23 in the increasing-`c` direction. They cover
`c=[7.56579873,7.67193358]` and `a=[0.23835647,0.24256313]`. Every accepted
event passes its orbit, tangent, real-`-1`, neutral, `7/8` section, and jump
gates. The two accepted terminals also pass independent Radau recorrection;
their `a` differences are `8.29e-13` and `8.16e-13`.

Both next exact corrector steps remain numerically regular but fail only the
interpolated-source separation requirement. The rejected down/up separations
are `-4.63e-8` and `-2.29e-8`, below the frozen `5e-8` magnitude. Exact
same-`c` diagnostic correction at three EXP-227 coordinates then finds
candidate/source agreement near machine precision, indicating that the
apparent local separation is interpolation error rather than a distinct event
curve. EXP-229 freezes the full confirmation before the earlier interpretation
is formally retracted.

Raw receipt: `artifacts/EXP-228/receipt.json`, 79,695 bytes, SHA-256
`d06a616888a6980d365ed64106db78f403435a56e791f7663346a03b672ef215`.
Compact receipt:
[`receipts/EXP-228.json`](receipts/EXP-228.json).

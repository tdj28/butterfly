# FND-028 — Transverse PIM rejects a nearly vertical boundary

Status: qualified prospective falsification from failed EXP-131

## Finding

The first adaptive-PIM test away from `c=20` rejects the simple expectation
that the local two-to-three saddle transition remains near `a=0.148` as `c`
decreases to `19.8`.

EXP-131 was preregistered with four endpoint predictions selected by the failed
finite-sprinkler discovery pilot. All twelve PIM access lines resolved, every
case retained 2097 return pairs per coordinate, and none of 72,717 lifetime
integrations failed. The experiment nevertheless fails its strict all-endpoint
gate, and that failure is retained.

The decisive falsification is `(c,a)=(19.8,0.148)`. In both `y` and `z`, 12 of
15 branch variants return two branches and the remaining three are bootstrap-
unstable rather than three-branch. Independently, every signed lower-support
fit is negative: the `y` slope interval is `[-1.4647,-0.8185]` and the `z`
interval is `[-1.7981,-1.0380]`. Thus the preregistered three/positive
prediction is not merely unresolved; its signed companion observable points
unanimously in the opposite direction.

At `(19.9,0.150)`, all 30 branch variants resolve three and all 30 slope fits
are positive, so that upper endpoint passes cleanly. The two `a=0.145` lower
endpoints each return 12/15 two-branch variants and uniformly negative slopes;
their last variants fail only finite coverage at `0.675`. They remain failures
under EXP-131's deliberately stricter all-variant rule, although that exact
censor form was independently qualified in EXP-121.

## Implication for Jones

This is good methodological news and a correction to an overly simple geometric
picture. It supports a real two/three saddle-topology distinction while showing
that its parameter-space locus bends or shifts, and may be interrupted by the
nearby loss of the stable period-4 window. Jones's qualitative mechanism is not
falsified. What is falsified is treating one accurate `c=20` bracket as a
nearly vertical transition curve.

No continuous TBA curve is established. The next prospective test raises the
censor ceiling to 256 returns and tests the newly implied `c=19.8` bracket
`[0.148,0.150]` and the provisional `c=19.9` bracket `[0.145,0.150]` under the
already-qualified coverage-censor semantics.

Tracked receipt: `docs/experiments/receipts/EXP-131.json`.

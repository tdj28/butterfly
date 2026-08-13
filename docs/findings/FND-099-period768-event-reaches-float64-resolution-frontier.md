# FND-099 — The seventh-event candidate reaches a Float64 resolution frontier

Status: qualified numerical-method finding; seventh dynamical event not qualified

EXP-280 brackets a seventh real-`-1` crossing on the exact primitive
period-768 branch. EXP-281 corrects the 1,024-node orbit and anti-periodic
tangent to residual norm below `9e-11`, but fails only its independent Radau
flip gate. EXP-282 repeats the immutable event at tighter step and tolerance:
DOP853 gives `-0.99999999629`, while Radau gives `-1.00000036358`.

EXP-283 binds those results to the original bracket. One representable
Float64 increment at the candidate `a` is `2.7756e-17`. The bracket secant
corresponds to an estimated `1.024e-6` multiplier change per increment, while
the tight solver disagreement is `3.673e-7`; even half that gap is
`1.836e-7`, above the unchanged `1e-7` event gate.

This qualifies a numerical frontier: repeating the identical Float64 coupled
formulation is poorly resolved at the precommitted tolerance. It does not
prove that no Float64 algorithm can qualify the event, and it does not promote
a seventh event, period-1536 child, limiting scaling law, or universality.
The next evidence path is a prospectively gated higher-precision segmented
integration and, only if that converges, a higher-precision event correction.

Evidence:
[`../experiments/EXP-280-jones-period768-segmented-flip-scan.md`](../experiments/EXP-280-jones-period768-segmented-flip-scan.md),
[`../experiments/EXP-281-jones-period768-augmented-flip.md`](../experiments/EXP-281-jones-period768-augmented-flip.md),
[`../experiments/EXP-282-period768-flip-precision-audit.md`](../experiments/EXP-282-period768-flip-precision-audit.md), and
[`../experiments/EXP-283-period768-float64-resolution.md`](../experiments/EXP-283-period768-float64-resolution.md).

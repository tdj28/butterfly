# EXP-023 — Natural continuation of periodic orbits in b

Status: executed; both natural-continuation gates passed
Manifest: `experiments/manifests/EXP-023-periodic-b-continuation.json`
Claim target: CLM-012 and P1-005

## Purpose

Continue the corrected period-3 and period-5 cycles away from their `b=0.20`
seeds while holding `(a,c)` fixed. Unlike EXP-022's moving representative
paths, this follows each flow solution itself and retains it after loss of
attractor stability.

## Frozen method

The period-3 seed fixes `(a,c)=(0.3225,3.0)`; the period-5 seed fixes
`(a,c)=(0.245,5.1)`. Each starting attractor is corrected by phase-conditioned
shooting. In both `b` directions the previous corrected state and flow period
predict the next solution. Nominal `b` step is 0.005 over `[0.05,0.35]`; a
failed correction halves the step down to 0.0003125 before stopping.

Every accepted point records closure, phase residual, period, nontrivial
Floquet multipliers, stability, and distances to `+1` and `-1`. Unit-modulus
sign changes are bracketed as candidate stability boundaries. The execution
gate requires at least 20 corrected points per family and maximum closure
`<=1e-8`.

## Limits

Natural-parameter continuation is not fold-safe and can stop at a fold even
when a pseudo-arclength branch continues. Linear interpolation of a multiplier
crossing is only a candidate boundary. Any detected crossing must be refined
as a coupled boundary solve and checked with pseudo-arclength continuation
before being identified as saddle-node, period-doubling, or Neimark-Sacker.

## Result

The clean run at commit `5b334269fb5e769d72e2dc98b6341b7c21fcc678`
passed in 31.38 seconds.

The fixed-`(a,c)=(0.3225,3.0)` period-3 branch reached both frozen limits,
producing 61 corrected points over `b in [0.05,0.35]`. Maximum closure was
`7.27e-12`; 35 points were stable. A real nontrivial multiplier crosses `-1`
between `b=0.175` and `0.180`, with a preliminary linear estimate `0.17683`.
This is a period-doubling boundary candidate.

The fixed-`(a,c)=(0.245,5.1)` period-5 branch produced 46 corrected points over
`b in [0.1275,0.35]`; maximum closure was `6.01e-12` and 23 points were stable.
It reached the upper limit but adaptive natural continuation stopped below
`b=0.1275` after exhausting the `0.0003125` minimum step. Three real-multiplier
unit-circle crossings are bracketed:

- a `-1` candidate in `[0.140,0.145]`;
- a `-1` candidate in `[0.180,0.185]`; and
- a `+1` candidate in `[0.275,0.280]`.

The last is a saddle-node candidate; the first two are period-doubling
candidates. The lower continuation stop has no nearby `+1` multiplier in the
last accepted sample, so it is recorded as a conditioning/fold/branch-tracking
problem rather than labeled a bifurcation.

The receipt SHA-256 is
`e3dab3bd688d20d37d13ac51a4bfb0e860f9ea99eb53385adf2f2728cbbe80eb`.

## Decision

The period-3 flow orbit persists throughout the declared `b` interval even
when unstable. The period-5 orbit persists over most of it and exposes multiple
stability changes. This is substantially stronger than atlas drift alone and
provides concrete boundary brackets for refined solves. EXP-024 will refine
the four signed multiplier crossings; pseudo-arclength is required to recover
or diagnose the lower period-5 stop.

# EXP-023 — Natural continuation of periodic orbits in b

Status: preregistered; pending clean local execution
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

# EXP-031 — Local normal-form scaling of the period-5 branch point

Status: executed; passed
Manifest: `experiments/manifests/EXP-031-period5-normal-form-scaling.json`
Claim target: local square-root classification of EXP-028; reclassified by EXP-041

> **Reclassification after EXP-041.** The measurements below remain valid, but
> their mechanism is now known: the parent was represented over twice its
> fundamental period. The apparent `+1` pitchfork-like branch point is the
> second-iterate representation of a fundamental supercritical flip at `-1`.

## Hypothesis and method

Above `b*=0.2722840597934716`, phase-invariant separation between the primary
and secondary cycles scales as `(b-b*)^1/2`. The primary multiplier excess
`lambda_p-1` and secondary deficit `1-lambda_s` are both positive, with their
ratio approaching the cubic pitchfork normal-form value two.

At six prospectively frozen offsets from `5e-5` through `1.4e-3`, independently
interpolate and correct the primary and one identity-qualified secondary
representation. Compute whole-trajectory phase-aligned RMS separation and
transverse Floquet multipliers. Fit log separation against log offset over all
six declared points, retaining every result.

## Acceptance and limits

All closures must be at most `1e-8`; primary must be unstable and secondary
stable at every point. The separation exponent must lie in `[0.4,0.6]` with
`R^2 >= 0.98`. The median ratio
`(1-lambda_s)/(lambda_p-1)` must lie in `[1.5,2.5]`.

Passing supports a supercritical pitchfork normal form in the quotient by flow
phase. It is still “pitchfork-like,” not a theorem: no exact system symmetry
has been identified, the scaling is finite precision and finite range, and a
validated local reduction remains future work.

## Result

The clean run at commit `2e97de92a21b6c567089bcae4b9c543ab13859ff`
passed every frozen gate. Across all six offsets, closures stayed below
`1.21e-13`, the primary cycle was unstable, and the secondary cycle was stable.

The phase-aligned separation fit is
`separation = exp(2.00494) * (b-b*)^0.4989577`, with
`R^2=0.99999916`. The exponent is within `0.00105` of the pitchfork value
one-half. The median multiplier-deviation ratio is `1.98050`, with range
`[1.91079,1.99673]`, approaching the cubic normal-form value two toward the
event.

The complete receipt SHA-256 is
`dd7fd933f00d1487d02636541cc5adb0c0a5f68b59e9a4716019026684d9c873`.
The provenance-bound figure is
`artifacts/EXP-031/EXP-031-period5-normal-form.png` (SHA-256
`d3c05ef050a7ee0c8c801164682521b76b1735ecc4db46234fbad06983425264`).

## Decision

Accept strong finite-range numerical support for a square-root second-iterate
normal form at fixed `(a,c)=(0.245,5.1)`, with `b*=0.272284059793`. EXP-041
subsequently identifies it as a double-covered fundamental supercritical flip,
so current scientific prose should use “period-doubling” or “flip,” not infer
an unknown spatial pitchfork symmetry. This result does not establish a global
organizing surface or classify other shrimp.

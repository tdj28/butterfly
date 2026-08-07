# EXP-031 — Local normal-form scaling of the period-5 branch point

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-031-period5-normal-form-scaling.json`
Claim target: supercritical pitchfork-like classification of EXP-028

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

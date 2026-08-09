# EXP-194 — Local corrected cycles from the second period-6 component

Status: executed; failed only because the frozen Barrio-section phase count was
six rather than the observed eight

## Question

Can a geometry-only sample of the isolated second-landmark component be
converted locally into corrected, stable period-6 flow orbits with six phases
on the independently published Barrio section?

## Frozen computation

EXP-194 binds the EXP-192 frame and component by SHA-256. It begins at the
exact second Jones landmark and selects 65 component pixels by deterministic
farthest-point coverage in component-range-normalized `(a,c)` distance. No
symbol, critical point, multiplier target, or presumed center enters this
selection.

Eight local workers independently integrate each parameter with DOP853 from
`(0,4,0)` after a 2,400-unit transient, reproduce fundamental period 6, shoot
the flow orbit to closure, integrate its exact variational equations, and
extract exactly six crossings on Barrio's declared small-equilibrium
`x`-plane with positive `dx/dt`. Each accepted candidate must have flow closure
at most `1e-9`, phase residual at most `1e-10`, neutral-multiplier error at most
`1e-6`, a real stable dominant transverse multiplier, and six Barrio-section
phases. At least 60 of 65 must pass.

Manifest:
[`../../experiments/manifests/EXP-194-local-corrected-second-component-cycles.json`](../../experiments/manifests/EXP-194-local-corrected-second-component-cycles.json).

## Claim boundary

Passing would establish corrected stable orbits at representative pixels, not
continuous family identity. The output is a hash-freezable input for a separate
two-step GPU survivor reconstruction using Barrio-section `z` as the scalar
return coordinate. Center status still requires two distinct critical
memberships and independent solver/step confirmation.

## Result

The local eight-worker run from clean commit `158c2ea` completed in 36.55
seconds. Fifty-eight of 65 geometry-selected pixels reproduce fundamental
period 6 on the historical section, correct to stable flow orbits, and pass
every closure, phase, monodromy, neutral-multiplier, and stability gate. Six
boundary-adjacent pixels remain unresolved under DOP853 and one resolves as
period 5.

All 58 corrected period-6 flow orbits intersect Barrio's positive-x section
exactly eight times per flow period, so every otherwise passing row fails the
preregistered `barrio_crossing_count == 6` check. Flow closure spans
`[7.76e-15,8.15e-13]`, neutral-multiplier error
`[9.09e-11,1.24e-9]`, and dominant transverse modulus
`[0.02770,0.99977]`. This is a systematic section-representation mismatch,
not an orbit-correction failure.

EXP-195 freezes a one-check requalification requiring eight finite Barrio
phases while preserving every orbit and all other checks byte for byte.

Compact receipt: [`receipts/EXP-194.json`](receipts/EXP-194.json).

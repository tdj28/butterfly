# EXP-194 — Local corrected cycles from the second period-6 component

Status: preregistered; not yet executed

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

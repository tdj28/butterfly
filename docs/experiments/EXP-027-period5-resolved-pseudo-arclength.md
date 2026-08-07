# EXP-027 — Final resolved period-5 pseudo-arclength crossing test

Status: preregistered; pending clean local execution
Manifest: `experiments/manifests/EXP-027-period5-resolved-pseudo-arclength.json`
Claim target: period-5 `+1` crossing near `b=0.2723`

## Purpose and frozen method

Make the local pseudo-arclength resolution gate compatible with the declared
window without changing a completed experiment. EXP-027 uses the same source
branch, exact Jacobian, solver, corrector, and two seeds as EXP-026. It freezes
a constant step one eighth of the seed secant norm, 100 attempted steps, and a
local `b` guard `[0.24,0.30]`.

The execution gate requires at least 40 points and maximum closure `<=1e-9`.
The scientific test is whether this independently denser trace again crosses
`+1` near `b=0.2723` without reversing in `b`.

## Limits

Passing rejects a saddle-node interpretation for the traced branch and supplies
a high-resolution branch-interaction seed. It still does not identify or
continue the second branch, impose a coupled eigencondition, or establish a
generic transcritical/pitchfork classification.

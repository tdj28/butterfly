# FND-040 — The Hopf-born period-1 family reaches the hub

Status: passed EXP-155 after preserved administrative failure EXP-154

## Finding

A single one-winding period-1 flow-orbit family has been phase-corrected from
`c=c_H+0.001=0.5202306256940273` to the exact reported hub coordinate
`c=10.3084`, holding `(a,b)=(0.1798,0.2)` fixed. All 118 points pass closure,
phase, neutral-multiplier, trajectory, and winding gates. Six exact points also
pass independent Radau correction.

Near Hopf, RMS orbit amplitude scales as `(c-c_H)^0.5017311` with
`R^2=0.9999983`, and the nearest computed period differs from the linear Hopf
period by `0.001417`. This qualifies the branch as the expected supercritical
Hopf-born family. A real `-1` multiplier crossing is bracketed in
`c in [3.1556294737,3.2536126316]`, supplying the next dedicated
period-doubling refinement target.

## Implication for Jones

This materially strengthens the local logic of the Figure 2 construction: a
single period-1 family really does originate at the qualified Hopf boundary,
persist along the explicit fixed-`a` path, and undergo the first stability loss
needed for a period-doubling cascade.

At the hub, however, the continued period-1 orbit has finite period
`5.9935437090` and never comes closer than `10.0310033361` to the small
equilibrium. It is therefore not itself the proposed homoclinic orbit. This is
not evidence against a distinct homoclinic connection of the equilibrium; it
prevents the period-1 continuation from being mistaken for that still-open
global manifold claim.

Tracked receipt: `docs/experiments/receipts/EXP-155.json`.

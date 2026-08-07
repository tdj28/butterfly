# EXP-027 — Final resolved period-5 pseudo-arclength crossing test

Status: executed; closure passed; frozen point-count gate failed
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

## Result

The clean run at commit `2dc19eb142fb14ab649cb23fb029a8c30d321666`
produced 37 corrected points before leaving the frozen `b <= 0.30` guard. This
is three points short of the preregistered minimum 40, so the overall
experiment gate is failed. Maximum flow-closure error was `6.35e-11`; the
traced range was `b in [0.2650000,0.3003367]`; and there were zero reversals in
the `b` component.

The significant real multiplier brackets `+1` between
`b=0.2720462159` (`0.9796096`) and `b=0.2727496629` (`1.0402575`). Linear
interpolation gives the descriptive estimate `b=0.2722827212`. The complete
receipt SHA-256 is
`eef4f1b88665c821c9b6a6dc55406b45836e57bc4a7ce07358f122a254fca6a3`.

Across EXP-025, EXP-026, and EXP-027, successively finer frozen steps give
descriptive crossing estimates `0.27219295`, `0.27227869`, and `0.27228272`.
All three traces contain zero `b`-direction reversals and overlap on the same
smooth period and multiplier curves. The resolution figure is
`artifacts/EXP-027/EXP-025-027-pseudo-arclength-resolution.png` (SHA-256
`ff1fd6730ed426cccd40ac5d9303d8cb4fce4804d4bc189489b3f17cf0f8d1f9`).

## Decision

Preserve the failed 40-point gate; do not redefine it after observing the
result. The independent resolution sequence nevertheless rejects a
saddle-node interpretation for the period-5 branch traced at fixed
`(a,c)=(0.245,5.1)`: its multiplier passes smoothly through `+1` while `b`
remains monotone. The event is retained as an unresolved `+1` branch
interaction near `b=0.272283`.

No further runs will chase an arbitrary point count. The next decisive test is
to solve the orbit equations together with a `+1` eigenvector condition and to
identify and continue the second local orbit branch. Only that analysis can
distinguish a transcritical-like, pitchfork-like, symmetry-related, or
nongeneric interaction.

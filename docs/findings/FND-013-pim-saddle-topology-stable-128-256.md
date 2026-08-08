# FND-013 — Independent PIM saddle topology is stable from 128 to 256 returns

Status: qualified two-control finite-horizon result

## Result

EXP-116 passes every prospectively frozen gate after `5136.14 s`. It compares
new 256-return censor-aware PIM straddles against the exact 128-return critical
intervals and hashes retained from EXP-115. All six declared 256-return lines
resolve, each stable-cycle control is independently period 4, and no adaptive
integration fails.

At `a=0.118`, 2097 retained pairs per coordinate recover two branches in all
15 oracle variants. Maximum normalized spans are `0.01601` within the new PIM
profile, `0.01595` against the EXP-112 CPU sprinkler, and `0.01601` across the
frozen 128/new 256 horizons.

At `a=0.149`, 2097 pairs recover three branches in both coordinates with
variant consensus `1.0`. The largest within-PIM, CPU/PIM, and 128/256 spans are
`0.01282`, `0.01282`, and `0.01282`. Every value is far below its frozen
`0.03`, `0.05`, or `0.04` gate.

The longer horizon sharply reduces reliance on censor bounds. The 128-return
profiles used 1108 and 385 censored lifetime evaluations at the unimodal and
bimodal controls; the new 256-return profiles use only 34 and 1. All surviving
censor decisions remain explicitly certified by captured neighbors.

## Interpretation

The independent adaptive-DOP853 PIM construction now reproduces the complete
two/three saddle distinction at two successive adequate lifetime horizons and
agrees with the independent RK4/Sobol sprinkler's critical locations. This
closes the repository's planned finite-horizon independent-method gate at the
two published controls.

The failed 64-return profiles in EXP-115 remain an important negative control:
short horizons can restrain trajectories to an under-covering invariant subset.
EXP-116 does not prove infinite-time convergence or hyperbolicity, but it shows
that the accepted geometry is stable after doubling an already adequate
observation ceiling.

## Consequence for Jones and the next experiment

This is strong positive evidence for the local nonattracting two/three-branch
substrate needed by Jones's branch-based explanation and by the shared 2012
topology-transition picture. It still does not prove reinjection rotation,
window connectivity, or a plane-wide TBA.

The binding next step is no longer another control reproduction. Freeze a
saddle-defined continuation path through the intervening regular gap, use the
256-return PIM method where the attractor is periodic, preserve full support
and branch-oracle uncertainty, and bracket the first nonattracting two-to-three
transition without interpolating across unresolved cells.

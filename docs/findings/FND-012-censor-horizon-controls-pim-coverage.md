# FND-012 — Censor horizon controls which part of the PIM saddle is covered

Status: qualified fixed-horizon result from a prospectively failed experiment

## Result

EXP-115 fails its complete nested-horizon gate after `5574.91 s`, with no
adaptive integration failures. The failure is retained. It does not erase a
stronger fixed-horizon result: the independently reconstructed 128-return
profiles pass at both published controls.

At `a=0.118`, all three 128-return PIM straddles retain 2097 pooled pairs per
coordinate. Both `y` and `z` recover two branches in all 15 oracle variants.
Maximum within-PIM critical spans are `0.01501` and `0.01250`; combined
EXP-112/PIM spans are `0.01511` and `0.01260`.

At `a=0.149`, all three 128-return PIM straddles also retain 2097 pairs. Both
coordinates recover three branches with variant consensus `1.0`. Maximum
within-PIM spans are `0.01224` and `0.01214`; combined CPU/PIM spans are
`0.01245` and `0.01213`.

The 64-return profiles fail for two different support reasons. All three
unimodal lines form complete straddles, but their pooled projections cover too
little of the invariant domain for any oracle variant to resolve. Only one of
three bimodal lines forms a complete straddle, yielding 699 pairs rather than
the required 1000. The two rejected bimodal lines have no exact or certified
censored interior maximum on their initial grids. No branch label is forced in
either failure.

## Interpretation

This is the first structurally independent PIM/DOP853 reconstruction of both
published saddle topologies in the repository. It directly strengthens the
local premise shared by the 2012 work: at the declared 128-return observation
scale, the regular-window nonattracting sets carry the expected two- and
three-branch return geometry, and their critical locations agree with the
independent RK4/Sobol sprinkler.

It does not qualify censor-horizon invariance. At 64 returns the PIM restraint
selects an under-covering invariant subset even when complete straddles exist.
At the bimodal `z=0.0090` line, the 64-return ordering is rejected at its first
refinement while the 128-return ordering completes 800 returns. Censor horizon
therefore changes stable-set access, not merely runtime.

## Consequence for Jones and the TBA program

The result is good news for the local substrate behind Jones's branch-based
mechanism: the two/three distinction is now recovered by an independent orbit-
restraint method at both controls, not only by survival ensembles or GPU
parity. It still does not prove Jones's third-branch reinjection explanation,
continue a TBA curve, or explain the full parameter plane.

Before using PIM as the production continuation method, a prospectively frozen
128-versus-256 return comparison must reproduce both branch counts and critical
locations. The shorter 64-return profile is now a documented negative control,
not a candidate for post hoc relabeling.

EXP-116 subsequently passes that 128/256 comparison with all six new lines
resolved and maximum cross-horizon span `0.01601`; see FND-013. The failed
EXP-115 nested gate and its 64-return support diagnosis remain unchanged.

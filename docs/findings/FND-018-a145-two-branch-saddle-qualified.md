# FND-018 — `a=0.145` two-branch saddle is prospectively qualified

Status: qualified local invariant-set result

## Result

EXP-121 passes its immutable new-data gate from clean commit `8d96f1c` in
`686.79 s`. The ordered saddle labels at fixed `(b,c)=(0.2,20)` are exactly
`2,2,3` at `a=0.118,0.145,0.149`, with one transition bracketed by the sampled
points `[0.145,0.149]`.

Both published controls pass without invoking censoring: all 420 control
case--run--coordinate--variant cells resolve normally, recovering two branches
at `a=0.118` and three at `a=0.149`.

At `a=0.145`, all 105 `y` variants resolve normally as two. In `z`, 84 resolve
normally as two and 21 meet the frozen coverage-only censor rule. Those 21 are
again exactly the three 80-bin variants in every run; all retain coverage
`0.6875`, remain graph-like, contain one nominal critical point, and agree with
the resolved critical interval. No target variant is rejected or returns
three.

## Numerical gates

The weakest target run retains 327 survivors and 2768 return pairs. Maximum
target survivor-fraction drift is `0.001526`; maximum target across-run critical
span is `0.01495`, below `0.04`. Across all three cases there are no integration
failures, and the largest DOP853/Hermite scaled-state and event-time errors are
`2.67e-6` and `1.72e-6`.

## Implication and boundary

The remaining `a=0.145` ambiguity is closed prospectively, not relabeled after
inspection. This is strong local evidence that the nonattracting chaotic saddle
inside the period-4 window remains on the two-branch side until at least
`a=0.145`, while the qualified `a=0.149` saddle is three-branch.

This strengthens the saddle-defined TBA mechanism relevant to both 2012
co-discoveries. It does not prove a continuous codimension-one curve between
the samples, determine the crossing location inside the interval, establish
template equivalence, or explain the entire parameter plane.

Raw receipt SHA-256:
`f396d3e034a2ee4f3f8a2785316b7ec099021c512d22274f93efb548ef985b9b`.

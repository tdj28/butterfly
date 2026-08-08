# FND-022 — Blind PIM qualifies the `a=0.148` saddle as two-branch

Status: prospectively qualified finite-horizon invariant-set result

## Finding

EXP-125 independently qualifies the nonattracting saddle at
`(a,b,c)=(0.148,0.2,20)` as two-branch. The target manifest encodes neither an
expected count nor a sprinkler critical-point reference. The finite sampled
two/three classifier bracket narrows to `[0.148,0.149]`.

## Evidence

- All three fixed PIM access lines complete at both 128- and 256-return
  right-censor ceilings.
- Each horizon provides 2097 post-burn-in return pairs per coordinate.
- All 15 oracle variants resolve as two in both `y` and `z` at both horizons:
  60/60 two-branch cells, with no three-branch or unresolved result.
- The 128/256 normalized critical spans are `0.008504` in `y` and `0.004735`
  in `z`, below the frozen `0.04` gate.
- The period-4 reference passes, the preregistered rule certifies the two
  right-censored evaluations at horizon 128, and no lifetime integration
  fails.

## Implication for EXP-123/124

The three-branch map exposed by 300-unit sprinkler survivors is not recovered
when the chaotic saddle is directly targeted. Both the longer-conditioned
sprinkler core and the independent PIM saddle are two-branch. The combined
evidence therefore supports escape-lifetime selection: an additional branch
is present in the finite transient population but is not part of the
PIM-resolved long-lived saddle core at this parameter. EXP-127 later rejects
the provisional faster-mean-escape explanation. The branch instead has delayed
but bounded capture: it outlives the core on average while lacking the core's
rare long tail.

This strengthens the Jones/Barrio-Blesa-Serrano topology-change program by
showing that the two/three distinction can be recovered inside the regular
window with a method designed for nonattracting invariant sets. It also
sharpens the definition: near the boundary, branch topology must be attached
to a specified invariant-set construction, not to an arbitrary finite-time
transient cloud.

## Limit

The result qualifies agreement at two finite censor ceilings. It does not prove
the infinite-lifetime saddle, a continuous codimension-one TBA curve, or the
Jones third-branch reinjection mechanism. Those remain continuation and
branch-conditioned escape problems. EXP-127 now closes the latter only for the
frozen landmark and scalar branch definition; the reinjection mechanism remains
open.

Raw receipt SHA-256:
`d76f6b84943ba527a83850d396144525c3c9c9726e92065c441870085cffc623`.

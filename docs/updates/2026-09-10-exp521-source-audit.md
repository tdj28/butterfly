# EXP-521 source-only adversarial pass

A separate local AI reviewer examined the frozen controller, runner, raw auditor,
tests, and protocol while the target ran. It did not inspect EXP-521 target
outcomes, run integrations, edit files, use the network, or call a paid API.
This is a source-only adversarial pass, not independent-team replication or a
paid Pro review. The reviewed source matches execution commit
`7260931511c2fc4583dbb89e7716b2d54c082005` and plan SHA-256
`29178f095da8a15602e8290d0d2339437f57148efad3fdc9aac0ad1471f9303b`.

No scientific acceptance blocker was found in that bounded review. The reviewer
checked all-16-root cyclic identity, both derivative centers and displacement
bounds, all 16 six-component contact/prediction checks, all eight gap checks,
retention of the second maximum, and failure/point/raw accounting.

## Accepted resource-reporting clarification

The frozen protocol calls the 600,000-segment limit a limit on "stored segments."
The implementation actually counts **periodic dense segments processed by the
stationarity census**, after the numerical producer has retained its output.
It does not count all midpoint, fold, guard, or shooting mesh segments and is
not a pre-storage total-mesh cap. Separate IVP, wall-time, byte quota and free-
space limits remain in force. Result prose must use the narrower, accurate
description. The frozen protocol and executed source are preserved unchanged;
this note corrects the reporting scope without changing a gate.

## Accepted interpretation limits

Strict gap improvement has no minimum effect-size gate. Report actual reductions
and cross-method/window spread, not certified exact-flow progress. A positive
result permits "one numerically validated local step satisfying the frozen
contact-proximity and prediction gates while reducing the first maximum's
absolute section gap in all four contexts." It does not establish an exact
critical locus, a grazing endpoint, local C/D identification, a homoclinic orbit,
or a Jones symbolic arrow. A negative result rejects this predictor or its
local validity, not Jones globally.

These findings do not predict the target result. Full raw-result audit remains
required after collection.

## Figure-helper review, still without target outcomes

The same reviewer checked the separate, post-freeze figure helper using only
source and synthetic tests. Two accepted findings were repaired: available
geometry at unqualified points now has open/gray markers and an explicit failure
list; the proposed correction now shows all four-context ranges, not just means.
The two correction maxima also use different shapes (star/plus), not color alone.
Missing geometry stays missing rather than becoming zero, and connecting lines
break at unqualified points. None of these presentation changes touches the
frozen numerical source or its acceptance gates.

# EXP-230 — Exact-arm continuation through the false child endpoint

Status: complete — middle-slice claim failed at a child flip candidate

EXP-229 proves that EXP-223's apparent endpoint was caused by subtracting a
fixed offset from a linear interpolation of the curved returning flip arm.
Near `c=7.62538`, the interpolation error cancels the intended offset and
moves the path back onto the event curve.

EXP-230 resumes from EXP-223's last qualified exact-event child at source index
44. For every direct or bisected step, it first solves the augmented period-6
real-`-1` event at exactly that `c`, then applies the unchanged
`-5.730236757e-7` offset and corrects the parent and primitive period-12 child.
It targets all seven remaining intervals through source index 51 at
`c=7.70247507`, with bisection to depth eight and DOP853/Radau controls at
indices 44, 47, and 51.

A pass establishes that the sampled stable child strip crosses the former
interpolation-induced false endpoint and reaches the middle slice at this
exact-arm offset. It does not establish a global child sheet, its true
endpoints, paired shrimp boundaries, TBA membership, double-criticality, or a
full-plane explanation.

Manifest:
[`../../experiments/manifests/EXP-230-returning-period12-child-exact-arm.json`](../../experiments/manifests/EXP-230-returning-period12-child-exact-arm.json).

## Result

The complete middle-slice claim fails, but exact-arm correction moves the
obstruction past the former interpolation-induced recrossing. Five points are
accepted from `c=7.62060178` through `c=7.62564488`; all retain unstable
period-6 parents, stable primitive period-12 children, period ratio two, and
`7/8` versus `14/16` section identity. Maximum closure is `2.36e-10`, minimum
proper-subperiod closure is `0.04370`, and maximum child-state step is
`0.000755` against the frozen `0.003` gate.

The child multiplier moves monotonically from `-0.95602` to `-0.99855` over
the accepted points. Subsequent exact-arm trials fail only the frozen child
stability margin: at `c=7.62570219` the modulus is `0.999034`, at
`c=7.62575950` it is `0.999522`, and at `c=7.62587412` it is `1.000499`.
This brackets a genuine period-12 real-`-1` event rather than another source-
arm interpolation artifact. EXP-231 freezes two-solver localization and
bilateral stability qualification of that event.

Raw receipt: `artifacts/EXP-230/receipt.json`, 18,518 bytes, SHA-256
`772ee87a47acae5d6c182944cb7c883905621c6aa1ddaca89ab1d6ae0fee4e4a`.
Compact receipt:
[`receipts/EXP-230.json`](receipts/EXP-230.json).

# EXP-230 — Exact-arm continuation through the false child endpoint

Status: frozen — not yet executed

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

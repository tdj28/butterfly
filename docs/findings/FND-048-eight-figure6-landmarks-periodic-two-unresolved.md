# FND-048 — Eight printed Figure 6 landmarks are periodic; two remain unresolved

Status: mixed result from failed strict EXP-174 gate

## Finding

A blind exact-coordinate audit of all ten approximate Jones Figure 6 landmarks
finds eight periodic attractors at the qualified horizon. DOP853 and Radau agree
for both initial conditions in all ten cases. The observed periods in source
transcription order are `5, 6, 8, 14, 6, 5, unresolved, 14, 14, unresolved`.

The full experiment correctly remains failed. One initial condition at
`(a,b,c)=(0.19368,0.2,8.456)` is unresolved after an 800-unit transient and
period 14 after 1600 units. This is a delayed-capture sensitivity, not
multistability or solver disagreement. The two unresolved exact coordinates
remain unresolved under every frozen long-profile comparison.

## Implication for Jones

This is good evidence that most printed gray-box locations genuinely sit on
low-period or doubled low-period windows despite their explicitly approximate
precision. It also validates the decision not to treat the gray boxes as a
ready-made exact symbolic database: one coordinate is transient-sensitive and
two exact printed points do not resolve periodically.

The periods alone do not identify Jones words or verify any `p -> p+1` arrow.
The figure's box-to-node geometry has not yet been machine-digitized, and
DEC-014 still requires an independently inferred return partition before a
cycle receives `C`, `D`, `0`, `1`, or `2`.

Tracked receipt: [`../experiments/receipts/EXP-174.json`](../experiments/receipts/EXP-174.json).

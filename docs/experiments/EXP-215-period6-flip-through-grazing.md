# EXP-215 — Invariant flip continuation through the section grazing

Status: complete — failed fixed-step completion gate after six accepted points

EXP-214 establishes that EXP-212's lower stop is a section-representation
boundary, not a loss of the exact real-`-1` flow event. EXP-215 therefore
continues from the same last two accepted parent events but no longer treats
the raw historical count as invariant identity.

One hundred exact dual-parameter pseudo-arclength points are requested. Every
point must retain the invariant flip gates, eight Barrio phases, and seven
historical phases under extremum-partitioned root bracketing. The terminal
point must reach `c<=6.05` and independently recorrect under Radau with the
same two section identities.

Manifest:
[`../../experiments/manifests/EXP-215-period6-flip-through-grazing.json`](../../experiments/manifests/EXP-215-period6-flip-through-grazing.json).

A pass establishes a broad sampled lower parent arm through one qualified
representation boundary. It does not locate a physical endpoint, extend the
child sheet, identify the TBA, prove global connectivity, or establish
double-critical membership.

## Result

The frozen 100-point claim fails after six accepted points. Those points do,
however, continue the exact period-6 real-`-1` event below the EXP-214 grazing,
from `c=6.91937431` to `c=6.83093274`. Every accepted event retains raw and
extremum-partitioned historical counts `7/7`, Barrio count `8`, maximum orbit
residual `4.61e-13`, maximum event-eigenvector residual `9.93e-13`, and maximum
extremum-partitioned section residual `2.66e-13`.

The terminal event independently recorrects under Radau: the parameter
difference is `2.69e-10`, relative period difference `6.79e-10`, state
difference `5.22e-10`, and multiplier-modulus difference `2.15e-9`. The next
fixed-step corrector terminates with orbit residual `9.25e-4`, event-vector
residual `9.94e-3`, and arclength residual `2.99e-3`. It is therefore not an
accepted dynamical event and cannot establish a physical endpoint. The
rapidly changing parameter projection motivates prospectively frozen adaptive
step-halving in EXP-216.

Raw receipt: `artifacts/EXP-215/receipt.json`, 20,148 bytes, SHA-256
`43488e68c43e6873ce1240f44d609c7a259fa1502d09ed6fb72946fdea346c3c`.
Compact receipt:
[`receipts/EXP-215.json`](receipts/EXP-215.json).

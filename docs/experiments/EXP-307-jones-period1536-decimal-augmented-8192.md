# EXP-307 — 8,192-step representation of event eight

Status: completed — passed all ten gates

EXP-306 qualifies the primitive period-1536 real-`-1` event from independent
three-resolution augmented sequences. Before attempting a 4,096-segment
period-3072 switch, EXP-307 applies the same representation safeguard required
at the preceding rung: refine the passed RK4 3/8 event from 4,096 to 8,192
steps on every one of 2,048 segments.

The 2,048/4,096/8,192 parameter and period increments must converge with
ratios in `[12,20]`. Successive Richardson estimates, source displacement,
augmented residual, target-blind continuation-envelope, and primitive
half-orbit gates are frozen. The doubled representation must then pass direct
DOP853 event matching below `1e-8` and secondary-null residual below `1e-6`.

A pass qualifies only this representation as the source of a prospective
period-3072 switch. It does not establish a child or birth direction.

Manifest:
[`../../experiments/manifests/EXP-307-jones-period1536-decimal-augmented-8192.json`](../../experiments/manifests/EXP-307-jones-period1536-decimal-augmented-8192.json).

## Result

The 8,192-step augmented system converges in two Newton updates to
`1.25e-31/1.37e-29` orbit/tangent residuals. The 2,048/4,096/8,192 parameter
and period increments give fourth-order ratios `15.8601/15.8529`. The new
Richardson coordinate is `0.24070100822425268955`, changing by only
`1.41e-13` from EXP-306; the Richardson period changes by `5.93e-10`.

Source node, tangent, period, continuation-envelope, and primitive-separation
gates all pass. The doubled representation's DOP853 event-matching residual is
`1.36e-9`, below the unchanged `1e-8` gate. Its secondary-null residual is
`3.60e-12`.

EXP-307 therefore qualifies this 8,192-step event representation as the source
of a period-3072 switch. It does not establish a child or birth direction.

Raw receipt: `artifacts/EXP-307/receipt.json`, 696,171 bytes, SHA-256
`59be65492475319a704f19fdc88ec985571a9cc117c837530804b43a2a34098c`.
Compact receipt:
[`receipts/EXP-307.json`](receipts/EXP-307.json).

# EXP-238 — Segmented period-24 child switch

Status: completed — passed candidate nomination

EXP-237 supplies an exact 16-segment representation of the primitive
period-12 real-`-1` event and its anti-periodic tangent mode. EXP-238 doubles
that event to 32 segments and switches directly along the phase-fixed child
mode at three frozen predictor lengths and both signs. It holds `b` and `c`
fixed and allows `a` to open with the child branch.

Candidates must have small multiple-shooting, phase, single-orbit closure, and
neutral residuals; a period ratio near two; nonzero parameter displacement;
half-period nonclosure in both node and integrated-orbit representations; and
exact `28/32` historical/Barrio section identity. A pass is a nomination only:
independent two-solver identity, stability exchange, attraction, and
sign-equivalence remain a separate successor.

Manifest:
[`../../experiments/manifests/EXP-238-jones-period24-segmented-switch.json`](../../experiments/manifests/EXP-238-jones-period24-segmented-switch.json).

## Result

All six corrected attempts retain low multiple-shooting residuals. Both signs
at predictor length `0.002` pass every candidate gate. Their half-period
closures are `0.000501835` and `0.000502113`, their half-node RMS values are
about `0.000361`, and both retain `28/32` section identity. The two candidate
`a` values lie about `3.22e-10` below the event and their preliminary dominant
moduli are `0.995499` and `0.995492`.

The smaller four attempts fail only the frozen minimum parameter-displacement
gate; they are retained in the receipt. EXP-239 continues one passing
candidate away from the singular event before independent qualification.

Raw receipt: `artifacts/EXP-238/receipt.json`, 24,793 bytes, SHA-256
`2e47b554a2591f58fe29d2df65a9a0a8ea08e71300ecf06a01a88a5f09d3ec82`.
Compact receipt:
[`receipts/EXP-238.json`](receipts/EXP-238.json).

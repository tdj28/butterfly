# EXP-238 — Segmented period-24 child switch

Status: frozen — not yet executed

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

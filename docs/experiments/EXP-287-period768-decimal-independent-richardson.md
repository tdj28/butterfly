# EXP-287 — Independent decimal Richardson audit for period 768

Status: frozen — not yet executed

EXP-286 qualifies a converged 50-digit classical-RK4 Richardson multiplier at
the immutable EXP-281 coordinate. EXP-287 independently integrates all 1,024
segments with the distinct fourth-order RK4 3/8 tableau at 4,096, 8,192, and
16,384 steps per segment.

The independent sequence must show fourth-order raw convergence, successive
Richardson convergence, a flip residual within `1e-7`, and agreement with the
classical extrapolation within `1e-7`. Analogous neutral gates and cyclic,
characteristic, orbit, tangent, primitive, and exact-section gates remain
mandatory.

A pass qualifies the seventh exact numerical real-`-1` event and tangent
representation by two independently tableaued high-precision sequences. A
period-1536 switch, stability exchange, scaling law, and universality remain
separate prospective claims.

Manifest:
[`../../experiments/manifests/EXP-287-period768-decimal-independent-richardson.json`](../../experiments/manifests/EXP-287-period768-decimal-independent-richardson.json).

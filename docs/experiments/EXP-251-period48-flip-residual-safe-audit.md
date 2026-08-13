# EXP-251 — Residual-safe segmented audit of the period-48 flip

Status: frozen — not yet executed

EXP-250 reaches all frozen DOP853 event residuals but exhausts its optimizer
ceiling, while a full-period Radau replay accumulates enough drift to miss the
multiplier gate. EXP-251 accepts the source status only if those already
frozen residuals pass, then evaluates the identical 64-segment orbit and
anti-periodic tangent equations under Radau and computes independent
block-Floquet products at four cyclic shifts.

The independent orbit, phase, tangent, normalization, real-`-1`, cyclic, exact
`56/64` identity, and proper-subperiod gates remain explicit. A pass qualifies
the event representation; a failure triggers a new collocation solve.

Manifest:
[`../../experiments/manifests/EXP-251-period48-flip-residual-safe-audit.json`](../../experiments/manifests/EXP-251-period48-flip-residual-safe-audit.json).

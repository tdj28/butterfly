# EXP-235 — One-sided-tangent multiscale period-24 switch

Status: frozen — not yet executed

EXP-234 shows that the symmetric primary-family stencil fails only at its
positive `a` offset, with raw closure `0.00801`; the center and negative offset
pass near `1e-11`. EXP-235 changes only the primary tangent stencil to
`[-2e-5,-1e-5,0]`.

The exact EXP-232 event, six switch scales, both nullspace signs, solver,
residual-safe handling, and all primitive period-24 nomination gates are
unchanged. A pass remains only a candidate nomination pending independent
DOP853/Radau qualification.

Manifest:
[`../../experiments/manifests/EXP-235-returning-period24-one-sided-switch.json`](../../experiments/manifests/EXP-235-returning-period24-one-sided-switch.json).

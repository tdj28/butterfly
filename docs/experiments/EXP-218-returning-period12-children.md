# EXP-218 — Held-out period-12 children on the returning flip arm

Status: complete — administrative failure before candidate evaluation

## Question

Does the broad EXP-217 returning arm carry the stability exchange expected of
the opposing boundary of the same local periodic domain?

## Frozen prediction and design

Three untouched EXP-217 events near `c=7.16`, `7.70`, and `8.20` are selected
by exact receipt coordinates. At each, a doubled-period shooting nullspace is
separated from the observed parent tangent and probed in both signed
directions. Every resulting candidate is independently recorrected with
DOP853 and Radau; doubled-parent roots are rejected by all proper historical
subperiod closures.

The directional prediction is fixed in advance. The original arm's qualified
stable period-12 children open toward higher `a`. If the returning arm is the
opposing boundary of the same local stability domain, its primitive stable
period-12 child must open toward lower `a`. A pass requires at least one such
child per slice, paired with an unstable period-6 parent, period ratio two,
historical/Barrio identities `7/8` for the parent and `14/16` for the child,
whole-orbit cross-solver agreement, and Floquet stability exchange.

Manifest:
[`../../experiments/manifests/EXP-218-returning-period12-children.json`](../../experiments/manifests/EXP-218-returning-period12-children.json).

## Claim boundary

A pass establishes local stability exchange on the returning arm compatible
with an opposing shrimp boundary. It does not prove that both arms bound one
globally connected window, qualify a returning child sheet, identify the TBA,
establish double-criticality, or explain the full parameter plane.

## Result

The runner aborts before evaluating the directional child prediction. The
inherited switcher estimates the fixed-`c` parent tangent from symmetric
natural corrections at `a_event+-1e-5`. The higher-`a` auxiliary parent fails
generic periodic-orbit correction at the `c=7.70247507` slice, raising
`RuntimeError: primary period-6 correction failed`; no candidate receipt is
written.

A post-failure administrative audit changes no child or stability gate. It
shows that the declared one-sided offsets `[-2e-5,-1e-5,0]` correct at all
three frozen events, whereas the positive offset also fails at the
`c=8.20198618` event. EXP-219 prospectively freezes this one-sided tangent
estimate and adds failure serialization. The lower-`a` child prediction remains
untested.

Compact failure record:
[`receipts/EXP-218.json`](receipts/EXP-218.json).

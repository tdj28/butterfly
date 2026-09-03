# EXP-078 — Switch the period-160 flip to period 320

Status: executed; failed conditioning gate

Apply the resolved-event nullspace switch to the independently qualified
period-160 parent. Use step `2e-5`, 10 requested points per sign, and require
one distinct arm with at least three points. Retain the `1e-7` singular-value,
`0.25` tangent, `1e-5` parent-distance, `5e-5` half-period, and `1e-8` closure
gates.

Passing supplies a period-320 candidate only. At a child duration near `2092`,
an independent attraction test may require a multiple-shooting/collocation or
remote-CPU design before the sixth rung is called supercritical.

The clean run at `b60a959` failed. The doubled period-160 shooting Jacobian's
smallest singular value is `7.75e-7`, above the frozen `1e-7` gate. Neither
sign produces a qualifying half-period-distinct arm: one has zero corrected
points and the other returns to the parent with half-period closure `1.81e-9`.
Receipt SHA-256:
`76de4b16a60d8388bcc1f21dba35144a636dde279eb63e06cd6ee524fa014d2f`.

Do not retry predictor size. At doubled duration near `2092`, the full-period
single-shooting Jacobian is no longer a reliable branch-direction oracle.
EXP-079 audits an equivalent segmented multiple-shooting Jacobian before any
new period-320 switch is attempted.

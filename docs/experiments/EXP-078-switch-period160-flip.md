# EXP-078 — Switch the period-160 flip to period 320

Status: preregistered after EXP-077; pending clean execution

Apply the resolved-event nullspace switch to the independently qualified
period-160 parent. Use step `2e-5`, 10 requested points per sign, and require
one distinct arm with at least three points. Retain the `1e-7` singular-value,
`0.25` tangent, `1e-5` parent-distance, `5e-5` half-period, and `1e-8` closure
gates.

Passing supplies a period-320 candidate only. At a child duration near `2092`,
an independent attraction test may require a multiple-shooting/collocation or
remote-CPU design before the sixth rung is called supercritical.

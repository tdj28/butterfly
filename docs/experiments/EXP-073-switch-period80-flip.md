# EXP-073 — Switch the period-80 flip to period 160

Status: preregistered after EXP-072; pending clean execution

Apply the resolved-event nullspace switch to the verified period-80 parent,
using step `8e-5`, 12 requested points per sign, and one required distinct arm
with at least four points. Retain the `1e-7` singular-value, `0.25` tangent,
`1e-5` parent-distance, `2e-4` half-period, and `1e-8` closure gates.

Passing supplies a period-160 candidate only. A fixed-parameter attraction and
stability-exchange qualification remains mandatory before the fifth cascade
rung is called supercritical.

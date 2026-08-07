# EXP-073 — Switch the period-80 flip to period 160

Status: executed; passed

Apply the resolved-event nullspace switch to the verified period-80 parent,
using step `8e-5`, 12 requested points per sign, and one required distinct arm
with at least four points. Retain the `1e-7` singular-value, `0.25` tangent,
`1e-5` parent-distance, `2e-4` half-period, and `1e-8` closure gates.

Passing supplies a period-160 candidate only. A fixed-parameter attraction and
stability-exchange qualification remains mandatory before the fifth cascade
rung is called supercritical.

The clean run at `84833c5` passed. The smallest singular value is `2.36e-8`,
tangent dot `5.55e-17`, and the distinct arm contains five points with endpoint
distance `0.001032` and half-period closure `0.004951`. The other sign returns
to the parent and is retained. Receipt SHA-256:
`f5d5b8de46ea9c4a123f26c96f119d80d86d498d1d3d2c0af7d8592882611dc9`.

Accept a one-arm period-160 candidate. Its first point is stable and later
points are unstable, already bracketing a possible next cascade event. EXP-074
independently qualifies the stable child at `b=0.17971425`.

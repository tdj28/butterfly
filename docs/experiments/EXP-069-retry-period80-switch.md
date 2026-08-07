# EXP-069 — Retry the period-80 switch from the resolved event

Status: preregistered after EXP-068; pending clean execution

Repeat the one-distinct-arm period-80 switch from the much more accurate
EXP-068 event, using step `0.00025`, 16 requested steps, and five required
distinct points. Retain the unchanged smallest-singular-value gate `1e-7`,
tangent gate `0.25`, endpoint distance `1e-5`, half-period closure `0.001`,
and full closure `1e-8`.

Passing supplies a period-80 candidate for an independent fixed-parameter
attraction/stability qualification. It does not validate the EXP-066 predicted
80→160 event; that prediction is tested only after period 80 itself passes.

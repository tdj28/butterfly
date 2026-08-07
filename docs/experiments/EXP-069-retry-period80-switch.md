# EXP-069 — Retry the period-80 switch from the resolved event

Status: executed; passed

Repeat the one-distinct-arm period-80 switch from the much more accurate
EXP-068 event, using step `0.00025`, 16 requested steps, and five required
distinct points. Retain the unchanged smallest-singular-value gate `1e-7`,
tangent gate `0.25`, endpoint distance `1e-5`, half-period closure `0.001`,
and full closure `1e-8`.

Passing supplies a period-80 candidate for an independent fixed-parameter
attraction/stability qualification. It does not validate the EXP-066 predicted
80→160 event; that prediction is tested only after period 80 itself passes.

The clean run at `e2b72ed` passed after the receipt-serialization fix at
`cc1a5b7`. The smallest singular value is `2.08e-8`, tangent dot is
`1.67e-16`, and one arm supplies eight distinct candidate points with endpoint
distance `0.00285` and half-period closure `0.01444`. The opposite sign returns
to the doubled parent and is retained. Receipt SHA-256:
`1c715df95ecfc96f043b369aa95c8c8e4271bdc7213deced2cc7d7ee638c813c`.

Accept a one-arm period-80 candidate. Its first two points are stable; the next
is unstable. Independently qualify a stable point at `b=0.179735` before
refining the prospective 80→160 bracket.

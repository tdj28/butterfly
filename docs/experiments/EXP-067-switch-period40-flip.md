# EXP-067 — Switch the period-40 flip to period 80

Status: executed; failed

Apply the extended-shooting nullspace switch at the EXP-065 period-40 event
with step `0.0004` and 14 requested points per sign. Based on the audited
EXP-063 phase-sheet asymmetry, require at least one—not retroactively both—
distinct child arm with six points, endpoint distance `>=1e-5`, half-period
closure `>=0.001`, and full closures `<=1e-8`. Retain both attempted signs.

Passing supplies a period-80 candidate only. A fixed-parameter perturbation,
period ratio, half-period identity, and parent/child stability exchange remain
mandatory. The eventual period-80 flip search must test the independently
frozen EXP-066 prediction rather than fit it after inspection.

The receipt-producing clean run at `cc1a5b7` failed. One direction gives five
distinct candidate points (endpoint half-period closure `0.01446`); the other
returns to the doubled parent. The smallest extended-shooting singular value
is `1.454e-7`, above the frozen `1e-7` gate, and the distinct arm also misses
the six-point gate by one. Receipt SHA-256:
`9cd30342c7f93535a22b3b65a69c3b82e077ca096f70f986bf25c76cc086f4f9`.

Retain the run as failed. The first execution completed but wrote no receipt
because the false NumPy predicate was not JSON serializable; commit `cc1a5b7`
made a native-boolean conversion and reran the unchanged manifest. EXP-068
re-refines the parent event at tighter tolerances instead of relaxing the
singular-value gate.

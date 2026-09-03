# FND-106 — The EXP-299 higher-a child seed collapses to the parent

Status: qualified by the combined EXP-324/325 evidence

EXP-299's Float64 DOP853 candidate at `a=0.24070100823781396` appeared to be a
stable primitive period-1536 orbit, but retained `2.53e-11` multiple-shooting
mismatch and `2.86e-7` direct closure. EXP-322 preserves undamped Newton
failure, and EXP-323 preserves a factor-independent backtracking failure.

EXP-324 changes no orbit gate. A step-scaled Armijo rule globalizes the same
50-digit fixed-`a`, 4,096-step RK4 3/8 correction. After thirteen accepted
updates, matching is `1.196e-23` and half-node RMS is `7.382e-20`. The exact
solution is therefore the doubled period-768 parent, not a primitive
period-1536 orbit. Cyclic spread is zero and the neutral residual is
`1.22e-20`.

This removes the apparent stable/stable child pair and the interim need for a
higher-`a` child fold, restabilization, or separate sheet. It does not weaken
the seventh event or the qualified immediate daughter: EXP-319/320 already
place that stable primitive daughter on the lower-`a` side with independently
repeated quadratic opening. The new result instead strengthens the local
supercritical interpretation and demonstrates why Float64 orbit labels cannot
be trusted at the accumulation scale without exact closure.

EXP-325 independently repeats the complete correction from the unchanged
original seed at 8,192 steps per segment. Nineteen accepted updates reduce
matching from `4.675e-11` to `7.219e-30` and half-node RMS from `6.307e-6` to
`6.026e-25`. The result is again the doubled period-768 parent; cyclic spread
is zero and the neutral residual is `7.11e-27`. This resolution-doubled
agreement promotes the finding from nominated to qualified.

The scope is deliberately seed-specific. It qualifies the collapse of the
stored EXP-299 candidate and invalidates conclusions downstream that require
that candidate to be a primitive exact orbit. It does not prove global
nonexistence of remote period-1536 sheets, establish basin measure, resolve
the eighth-event global sheet, validate a homoclinic connection, or explain
full-plane topology.

Tracked receipts: [`../experiments/receipts/EXP-322.json`](../experiments/receipts/EXP-322.json),
[`../experiments/receipts/EXP-323.json`](../experiments/receipts/EXP-323.json),
[`../experiments/receipts/EXP-324.json`](../experiments/receipts/EXP-324.json),
and [`../experiments/receipts/EXP-325.json`](../experiments/receipts/EXP-325.json).

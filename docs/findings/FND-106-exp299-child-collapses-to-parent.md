# FND-106 — The EXP-299 higher-a child seed collapses to the parent

Status: nominated by EXP-324; resolution-doubled replication frozen as EXP-325

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

The finding remains nominated until EXP-325 repeats the complete correction
from the original seed at 8,192 steps per segment. It does not establish basin
measure, the eighth-event global sheet, a homoclinic connection, or full-plane
topology.

Tracked receipts: [`../experiments/receipts/EXP-322.json`](../experiments/receipts/EXP-322.json),
[`../experiments/receipts/EXP-323.json`](../experiments/receipts/EXP-323.json),
and [`../experiments/receipts/EXP-324.json`](../experiments/receipts/EXP-324.json).

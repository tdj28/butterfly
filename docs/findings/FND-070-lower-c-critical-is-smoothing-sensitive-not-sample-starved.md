# FND-070 — The lower-c critical is smoothing-sensitive, not sample-starved

Status: qualified oracle-sensitivity diagnosis; topology remains unresolved

EXP-200 quadruples EXP-199's initial-condition ensemble from 2,048 to 8,192 on
168 previously qualified lower-`c` stable orbits. Support is ample: typical
profiles contain roughly 49,000 return pairs, and the two RK4 steps agree in
survivor fraction within `0.00281`.

Only 10 and 9 candidates pass the strict five-variant three-branch oracle, with
8 agreeing across steps, below the frozen minimum of 40. This is not a clean
two-branch field. At both steps, 125 candidates are called three-branch by all
four bin-count/baseline-smoothing/prominence variants. For 104 of those, the
single `smoothing=1e-4` variant returns two branches at both steps. Thus adding
four times as many trajectories does not remove the disagreement; it reveals
that the shallow additional critical is filtered at one declared smoothing
scale.

The eight strict survivors still do not nominate a double-critical center.
Their second signed residual remains positive, with a minimum near `0.0341`,
and none passes any direct-center gate. The evidence rejects sample scarcity
as the main explanation for the lower-`c` oracle failure, but it does not
qualify a topological destruction of the third branch. A scale-aware smoothing
ladder and critical-prominence continuation are required before the residual
can be followed farther.

Evidence: [`../experiments/EXP-200-lower-c-high-support-signed-residual-scan.md`](../experiments/EXP-200-lower-c-high-support-signed-residual-scan.md).

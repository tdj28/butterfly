# EXP-155 — Corrected Hopf-to-hub period-1 qualification

Status: schedule correction and unchanged gates frozen before execution

EXP-154 passed every scientific tolerance but failed its exact row-count gate
because a near-Hopf independent-solver checkpoint was inserted into both
continuation directions and the seed was duplicated. EXP-155 fixes only that
direction-aware schedule partition. It retains the same 118 scientific points,
seed, DOP853 and Radau solvers, orbit samples, Hopf scaling interval, winding
identity, Floquet crossing requirement, and every numerical acceptance
threshold.

The raw EXP-154 receipt remains immutable. Passing EXP-155 may qualify the
scientific result; it cannot retroactively turn EXP-154 into a pass.

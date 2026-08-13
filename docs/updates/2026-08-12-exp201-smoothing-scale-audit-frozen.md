# EXP-201 freezes a nested smoothing-scale audit

EXP-200's failure is concentrated in a single high-smoothing variant, not in
return-pair support or step parity. EXP-201 selects the complete 104-point
cross-step disagreement set and replaces the binary comparison with a seven-
level logarithmic smoothing ladder.

The audit reuses one 8,192-trajectory integration per RK4 step and extracts a
nested 2,048-trajectory rectangular grid from the same run. A point qualifies
only when the shallow critical's location and its monotone three-to-two
smoothing transition remain stable across both supports and both steps. The
164,041-byte candidate artifact is prepared and hash-bound before execution.

The first secure RTX A4500 worker was stopped before any transfer or integration:
the controller requires payload-specific authorization for the derived candidate
artifact even though its `<$30` compute cost is already authorized. The worker
was terminated, the RunPod account was verified empty, and the cost is bounded
below `$0.02`.

After the exact artifact was authorized, the unchanged experiment ran on a
secure RTX A5000. It passes with 94/104 qualified candidates against the frozen
70/104 minimum. Eighty-six have identical transition indices across all four
step/support reconstructions, and eight differ by one ladder level. The
qualified second-critical spans have median `0.01031` and maximum `0.01679`
against the `0.03` gate. The receipt was retrieved by matching hash; the worker
was terminated; no account pods remain; and its cost is bounded below `$0.12`.

This qualifies a reproducible finite-data transition scale, not invariant
topology. The next experiment may now reconstruct the signed critical-membership
residual with a scale ensemble instead of treating `smoothing=1e-4` as a veto.

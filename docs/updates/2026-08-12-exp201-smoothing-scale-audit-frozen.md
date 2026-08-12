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

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

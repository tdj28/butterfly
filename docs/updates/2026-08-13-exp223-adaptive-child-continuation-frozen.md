# EXP-223 adaptive returning-child continuation is frozen

EXP-222's successful fine bridge turns EXP-221's failure into a branch-tracking
problem rather than evidence that the stable child ends. EXP-223 now attempts
all 52 exact event endpoints to the middle returning-arm slice and bisects only
rejected or incoherent steps, to depth six.

The closure, stability, period-ratio, primitive-period, and two-section identity
gates are unchanged. A new prospective `0.003` child-state bound prevents a
converged nonlinear solve on a different primitive root from being accepted.

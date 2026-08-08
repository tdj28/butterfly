# Update — EXP-130 transverse GPU pilot preregistered

The next calculation is now concrete: it tests whether the locally qualified
signed branch-opening observable produces ordered finite brackets at `c=19.8`
and `c=19.9`, rather than spending another hour bisecting only `c=20`.

The GPU remains a discovery accelerator. Stable-cycle construction and
classification use adaptive DOP853; the ensemble uses the already qualified
Float64 RK4/Hermite kernel; any newly discovered bracket must later pass an
independent adaptive-DOP853 PIM experiment. Unresolved points are preserved.

The live Runpod account was empty before preregistration. EXP-130 has a
run-specific `$0.40/hour`, one-hour, `$0.40` hard gate and an explicit
retrieve/hash/terminate/verify-empty teardown contract.

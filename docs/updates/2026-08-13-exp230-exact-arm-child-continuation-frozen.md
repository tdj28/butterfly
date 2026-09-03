# EXP-230 freezes exact-arm child continuation

The EXP-229 correction immediately changes the next computation. EXP-230
retains the qualified EXP-223 child, offset, and scientific gates but replaces
every interpolated source event by a fresh exact fixed-`c` augmented event
solve. It resumes at exact event 44 and targets the middle slice at event 51.

This is a serial orbit/variational workload, so local CPU is the appropriate
executor. A GPU worker would add transfer and provisioning overhead without
accelerating the nonlinear dependency chain.

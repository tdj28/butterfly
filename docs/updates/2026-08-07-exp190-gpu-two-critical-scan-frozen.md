# EXP-190 freezes the GPU two-critical scan

All 65 EXP-189 candidates will be integrated together under two Float64 RK4
steps on a cost-capped NVIDIA worker. Unlike the rejected Floquet-only locator,
the ranking keeps two explicit survivor-derived critical-to-orbit residuals
and forces distinct orbit phases.

The scan is x-only because z is already demonstrated non-injective here. It is
still target-word blind, requires step-size topology and survivor parity, and
can only nominate a candidate for independent CPU/adaptive confirmation.

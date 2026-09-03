# EXP-182 gap statistical parity frozen

Date: 2026-08-07

EXP-182 preserves EXP-181 and replaces only its inappropriate long-time
trajectory-label audit. The same 8,192 Jones-section seeds, attractor
reference, capture rule, local oracle, and physical predictions are evaluated
at RK4 steps `0.01` and `0.005`. Every profile must pass locally, survivor
fractions may differ by at most `0.02`, and physical critical locations may
differ by at most `0.8` in x and `0.00012` in z.

As a new false-negative control, 128 validation-attractor states must all be
captured by time 100 at both steps. Five fixed seeds must agree with DOP853
over their first five returns within scaled state error `0.001` and event-time
error `2e-5`. No long-time chaotic trajectory identity is required.

Global branch-count disagreement remains descriptive. Passing can qualify the
finite survivor-cloud local critical at the one support gap, not a global TBA
curve or historical symbol mapping by itself.

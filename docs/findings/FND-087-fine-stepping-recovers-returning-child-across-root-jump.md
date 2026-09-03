# FND-087 — Fine stepping recovers the returning child across a root jump

Status: numerically qualified across 17 points and three solver controls

EXP-222 follows the closest qualified returning-arm child across the first
event interval using 16 substeps. Every point retains unstable period-6 parent,
stable primitive period-12 child, period ratio two, and exact `7/8` versus
`14/16` section identity. DOP853 and Radau agree at both endpoints and the
midpoint.

This establishes that EXP-221's coarse correction jumped between primitive
roots; it was not a loss of the child sheet. The conclusion is currently local
to one interval. Adaptive identity-safe continuation is required before the
returning child can be associated with a broad shrimp boundary.

Evidence:
[`../experiments/EXP-222-returning-period12-child-first-bridge.md`](../experiments/EXP-222-returning-period12-child-first-bridge.md).

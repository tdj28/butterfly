# EXP-196 freezes GPU parity for the eight-phase Barrio section

EXP-195 produces 58 corrected stable candidates with eight phases on Barrio's
positive-x section. Before those candidates are scanned, EXP-196 isolates the
new CUDA code path at the exact second landmark and compares it to the existing
CPU sprinkler reference.

The test is source-only: the orbit is regenerated from the public parameter
coordinate on the worker, so no derived atlas or candidate artifact leaves the
local workspace. Both RK4 steps must independently produce robust three-branch
z maps and pass survivor, return-pair, critical-location, and numerical-failure
parity. Passing opens only the GPU implementation gate.

# FND-062 — The first period-6 Floquet-zero neighborhood is unimodal

Status: qualified negative result; double superstability remains open

EXP-190 reconstructs survivor return maps for every one of EXP-189's 65
stable period-6 zero-edge candidates at RK4 steps `0.01` and `0.005`. All 130
candidate/profile maps resolve as two-branch in the recovered historical x
coordinate under every frozen oracle variant. No trajectory fails, every
candidate clears the survivor and return-pair floors, and critical intervals
are narrow. The absence of the second critical is therefore the scientific
result rather than a numerical-resolution failure.

This closes the local search around Jones's approximate landmark
`(a,c)=(0.21564,6.124)`: neither an exact printed point, a Floquet stationary
zero, nor any of its 65 qualified zero edges is a two-critical center on this
representation. It does not reject the Jones/Barrio double-superstability
mechanism. The printed landmarks are unordered and approximate, and Jones did
not publish the section equation. A post-result diagnostic at the other exact
period-6 landmark `(0.215,7.6)` finds a robust three-branch z return map on the
independently published Barrio section; that observation is a search lead and
must be confirmed prospectively before becoming evidence.

Evidence: [`../experiments/EXP-190-gpu-two-critical-residual-scan.md`](../experiments/EXP-190-gpu-two-critical-residual-scan.md).

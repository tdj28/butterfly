# EXP-199 rejects both center nominations in the incomplete dense field

EXP-198 provides 685 individually qualified corrected orbits but fails its
coverage gate. EXP-199 binds that complete immutable artifact, limits its claim
to an incomplete diagnostic, and retains signed residuals for both critical-
to-orbit assignments at both RK4 steps.

A direct grid point must improve sharply on EXP-197's distances and slope.
Alternatively, a bracket cell requires four eligible corners, one common
phase assignment, and sign changes of both residuals independently at both
steps. Neither route passes. There are 126 cross-step-qualified candidates,
but no point passes any direct gate and no complete cell brackets both signed
residuals. The first residual crosses zero; the second remains strictly
positive at both steps, with lower bounds `0.031491` and `0.031529`.

The selected point moves to `(a,c)=(0.21559,7.32)` and improves EXP-197's
midpoint and interval distances, but still misses the frozen limits by wide
margins. Because the prerequisite mesh is fragmented, coverage-failed, and
boundary-touching, the result rejects only the sampled stable field. It points
next to continuation beyond that field, not another blind local densification.

The authorized 3,950,130-byte input and clean source were hash-verified on a
secure RTX A5000 worker. The 3,785,688-byte receipt was retrieved with matching
remote/local SHA-256, the worker was terminated, and the elapsed-time cost
bound is below `$0.20`.

The result is now Figure 10 in the rebuilt 29-page manuscript. Its
provenance-bearing three-panel field shows the residual sign split and direct-
gate margins; the complete rendered PDF passes visual QA.

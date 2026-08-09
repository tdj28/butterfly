# EXP-197 freezes the direct Barrio-z two-critical scan

EXP-195 supplies 58 corrected stable eight-phase candidates across the
isolated second period-6 component. EXP-196 qualifies the generalized CUDA
section path with exact CPU/GPU survivor and return-pair agreement at both RK4
steps. EXP-197 now binds those two prerequisites and scans every candidate.

The discovery rule is target-word blind. Each candidate must reconstruct a
robust three-branch Barrio z map at both steps, assign its two ordered criticals
to distinct members of the complete eight-phase orbit, and pass survivor,
critical-location, and slope-residual parity. A selected point remains only a
nomination for a coupled local solve and independent adaptive-solver audit.

Execution requires transferring the 106,345-byte hash-bound
`artifacts/EXP-195/candidates.json` to the task-owned RunPod worker. The
platform requires authorization naming this derived artifact even though
tracked-source upload is already authorized.

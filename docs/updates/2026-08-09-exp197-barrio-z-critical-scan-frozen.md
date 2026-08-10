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

An initial secure-worker attempt transferred only the frozen `fa8f332` source
archive. The platform rejected the derived candidate transfer, so no scan ran.
Worker `ek8r3t88x0i71i` was terminated immediately, and the account pod list
was then empty. Execution remains frozen without scientific peeking.

## Authorized execution result

After artifact-specific authorization, the unchanged scan completed on a
fresh secure RTX A5000. Both steps are numerically clean and identify 31 and
32 three-branch candidates; 31 retain identical phase assignments across
steps. The experiment nevertheless fails its final direct-membership rule.
No candidate places both orbit phases inside the two critical intervals, and
no candidate passes the frozen assigned zero-slope ceiling. The nearest
sample, `(a,c)=(0.21555,7.372)`, passes only the midpoint-distance gate. It is
now a localized target for a denser coupled solve, not evidence of a center.

The receipt was retrieved with matching SHA-256 and task worker
`35fgcklf1dto3y` was terminated. One unrelated account worker remained and was
not modified.

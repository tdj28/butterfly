# EXP-197 — Barrio-z two-critical scan of the second component

Status: preregistered; execution awaits explicit transfer authorization for
the 106,345-byte derived candidate artifact

## Question

Among all 58 corrected stable representatives of the isolated second-landmark
component, does any orbit contain both independently reconstructed critical
points of the three-branch Barrio z return map?

## Frozen computation

EXP-197 binds the complete EXP-195 candidate artifact and the passed EXP-196
CPU/GPU parity receipt by SHA-256. Every candidate has a corrected stable flow
orbit and exactly eight finite phases on Barrio's `x=x_-`, positive-`dx/dt`
section. No symbolic word, alphabet label, Floquet-zero target, or expected
center enters the scan.

For each candidate, the qualified CUDA survivor kernel runs the same 2,048
historical-half-plane seeds at RK4 steps `0.01` and `0.005`. It independently
reconstructs the scalar `z_n -> z_(n+1)` map under five oracle variants,
requires a robust three-branch partition, and assigns the two ordered critical
intervals to two distinct phases among all eight corrected section points.
Candidates must pass survivor, return-pair, critical-span, step-parity, and
zero-slope residual gates. Ranking uses only the two critical-to-orbit
distances and local slope residuals.

Manifest:
[`../../experiments/manifests/EXP-197-barrio-z-two-critical-scan.json`](../../experiments/manifests/EXP-197-barrio-z-two-critical-scan.json).

## Claim boundary

A pass nominates a direct double-critical center candidate. It does not prove
double superstability: the selected point must be locally refined as a coupled
two-residual solve, independently corrected with DOP853 and Radau, reproduced
under step and survivor controls, and only then encoded symbolically.

## Administrative execution attempt

On 2026-08-09, secure task-owned RTX A5000 worker `ek8r3t88x0i71i` was
provisioned at a hard `$0.30/hour` ceiling and an actual `$0.27/hour` rate. The
frozen `fa8f332` source archive (SHA-256
`e719b90006b74fb2692a683e02e61af5d238e2fee62c327ad839f34f85a2155b`)
was transferred. The platform rejected transfer of the derived EXP-195
candidate payload because the user message did not name that exact artifact
and destination. No candidate data were transferred and no scientific
computation ran. The worker was immediately terminated; the subsequent
account-wide pod list was empty.

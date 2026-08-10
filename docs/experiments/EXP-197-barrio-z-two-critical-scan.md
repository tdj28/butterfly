# EXP-197 — Barrio-z two-critical scan of the second component

Status: executed; failed the frozen direct-membership acceptance gates

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

## Executed result

The authorized secure RTX A5000 execution from declared clean source commit
`9b8b557` completed both profiles without a numerical failure. The `dt=0.01`
profile resolves 31 three-branch candidates; `dt=0.005` resolves 32. Thirty-one
candidates retain the same phase assignment and pass all frozen cross-step
parity gates. The maximum critical-location and survivor-fraction differences
over that cross-step set are `0.00666` and `0.00782`, respectively, below the
frozen `0.03` ceilings.

No cross-step candidate passes either final direct-membership gate. The best
midpoint and interval candidate is `component-sample-059` at
`(a,b,c)=(0.21555,0.2,7.372)`. Its maximum normalized midpoint distance is
`0.04963`, just inside the `0.05` gate, but its interval distance is `0.03603`
against a `0.02` ceiling and its assigned zero-slope residual is `1.894`
against `0.2`. One assigned phase matches the first critical with a slope
residual of about `0.044`; the phase assigned to the second critical lies
outside its interval and has the large slope residual. Even the independently
best slope candidate has `0.24556`, so zero of 31 candidates passes the frozen
slope ceiling.

EXP-197 therefore rejects direct double-critical membership at the 58 sampled
representatives. It does not reject a center between them. The best candidate
is a prospectively identified localization target for a denser two-dimensional
residual solve, not a discovered center.

Raw receipt: `artifacts/EXP-197/receipt.json`, SHA-256
`6a823588e5cf581b831ff70d2cdc276b172399638f8267648b923b95c15f4c71`.
Compact receipt: [`receipts/EXP-197.json`](receipts/EXP-197.json).

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

After the exact derived-artifact authorization was supplied, a fresh secure
worker (`35fgcklf1dto3y`) received hash-matching source and candidate payloads.
Its first invocation stopped before integration because the source archive's
repository root was absent from `PYTHONPATH`. Adding that import root and
rerunning the scientifically unchanged command produced the result above. The
hash-matching receipt was retrieved and the task worker was terminated. The
account then contained one unrelated `ndl-tent-map-20260809` worker, which was
left untouched; no EXP-197 worker remained active.

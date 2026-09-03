# EXP-199 — Incomplete local Barrio signed-residual scan

Status: executed; both frozen nomination routes failed on the explicitly
coverage-incomplete input

## Question

Do the 685 individually qualified EXP-198 orbits contain a substantially
closer double-critical candidate or a complete local grid cell in which both
signed critical-to-orbit residuals change sign consistently at two RK4 steps?

## Frozen computation

EXP-199 retains EXP-197's section, survivor ensemble, capture geometry, five
oracle variants, and two RK4 steps. It changes only the prospectively selected
candidate set and makes the signed residuals explicit. Each candidate must
resolve the robust three-branch Barrio z map at both steps, retain the same
distinct phase assignment, and pass survivor and critical-location parity.

The direct-candidate gates are deliberately tighter than EXP-197:
maximum normalized midpoint distance `0.02`, interval distance `0.005`, and
assigned zero-slope residual `0.1`. Independently, the scan records a bracket
only when all four corners of one complete lattice cell are eligible, have the
same phase assignment, and bracket zero for both signed residuals at both RK4
steps. Either condition is only a nomination for an adaptive solve.

Manifest:
[`../../experiments/manifests/EXP-199-incomplete-local-barrio-signed-residual-scan.json`](../../experiments/manifests/EXP-199-incomplete-local-barrio-signed-residual-scan.json).

## Claim boundary

EXP-198 failed its coverage gate, its passing mask is fragmented, and the
center component touches the lower-a boundary. Consequently, even a clean
negative EXP-199 result cannot exclude a nearby center. A bracket is not a
root and must be solved and independently qualified with adaptive integrators.

## Result

Both RK4 profiles complete on the authorized RTX A5000 worker. They retain 137
and 131 individually eligible candidates at `dt=0.01` and `dt=0.005`, with 126
candidates agreeing across both steps. All 126 preserve their distinct phase
assignment. Maximum critical-location drift is `0.002102` and maximum survivor-
fraction drift is `0.01172`, below their frozen `0.03` limits.

Neither nomination route passes. No cross-step candidate meets the midpoint
distance, interval-membership, or assigned zero-slope gates, even separately.
The selected point is `local-a019-c030` at
`(a,b,c)=(0.21559,0.2,7.32)`, with phase assignment `[7,5]`, maximum normalized
midpoint distance `0.031529`, interval distance `0.030404`, and zero-slope
residual `1.86985`, versus frozen limits `0.02`, `0.005`, and `0.1`.

The signed field explains the failure. The first residual crosses zero at both
steps, ranging from `-0.005262` to `+0.001668` at `dt=0.01` and from
`-0.005199` to `+0.001335` at `dt=0.005`. The second is positive at every one
of the 126 points: its ranges are `[0.031491,0.090708]` and
`[0.031529,0.090767]`. Consequently there is no complete same-assignment cell
that brackets both residuals. The best zero-slope residual anywhere in the
eligible field is `0.820887`, still 8.2 times the frozen limit.

This is a strong finite-sample rejection of a double-critical center inside
the recovered stable field. It is not a rejection of the Jones/Barrio
double-superstability mechanism globally: EXP-198 failed coverage, the passing
mask is fragmented, the center component reaches the lower-`a` boundary, and
EXP-199's cross-step eligible field begins only at `c=7.32`. The one-sided
second residual instead selects continuation beyond this incomplete field as
the next test.

Compact receipt: [`receipts/EXP-199.json`](receipts/EXP-199.json). The raw
receipt is `artifacts/EXP-199/receipt.json`, 3,785,688 bytes, SHA-256
`384016b40113cfbcfbd415c514dfd52543e35c36c37132eb128f8fcd4624a4b2`.

## Remote execution

The source archive and the user-authorized EXP-198 candidate artifact were
uploaded only to task worker `5nmz0fjzukf5nx`. Remote hashes matched the local
source archive (`84725fd...cdb2`) and candidate artifact (`db4c3a...efa6a`),
and the retrieved receipt hash matched locally. The secure worker ran at
`$0.27/hour`, was terminated immediately after retrieval, left no task pod
running, and incurred less than `$0.20` by elapsed-time bound.

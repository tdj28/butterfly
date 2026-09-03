# EXP-325 — Resolution-doubled replay of the EXP-299 target collapse

Status: passed — resolution-doubled collapse independently reproduced

EXP-324 closes the original EXP-299 seed below `1e-20` in the 4,096-step
50-digit RK4 3/8 map and collapses its primitive amplitude to `7.38e-20`.
EXP-325 binds that passed raw receipt and replays the correction from the
unchanged original seed using the passed EXP-320 event period and 8,192 steps
per segment.

The complete Armijo factor ladder, coefficient, twenty-update cap, precision,
fixed parameters, and every science gate are unchanged. The run does not start
from EXP-324's collapsed endpoint; it must independently globalize the old
Float64 seed in the finer discrete map.

Either primitive survival or doubled-parent collapse may pass. Agreement with
EXP-324 promotes FND-106 across two resolutions, while disagreement preserves
both receipts and leaves the seed fate representation-dependent.

Manifest:
[`../../experiments/manifests/EXP-325-jones-period1536-decimal-target-armijo-8192.json`](../../experiments/manifests/EXP-325-jones-period1536-decimal-target-armijo-8192.json).

## Result

EXP-325 passes every frozen gate after 9,452.80 seconds and nineteen accepted
updates. Matching falls from `4.675e-11` to `7.219e-30`; half-node RMS falls
from `6.30690e-6` to `6.02635e-25`. The corrected orbit is again classified
as the doubled period-768 parent. Its cyclic Floquet spread is zero, maximum
neutral residual is `7.11e-27`, and dominant transverse modulus is `0.927453`.

The fine-map path is more strongly damped than EXP-324's path and includes an
amplitude rebound during globalization, but then enters full-step quadratic
convergence. It starts from the unchanged original EXP-299 seed, so agreement
is not inherited from the 4,096-step endpoint.

Together EXP-324/325 qualify the fate of this stored seed across two discrete
representations: its apparent primitive period-1536 identity was a
near-neutral Float64 artifact. This retracts the project's interim extra-sheet
interpretation and strengthens Jones's local cascade. It does not prove that
no remote period-1536 sheet exists anywhere else in parameter space.

Raw receipt: `artifacts/EXP-325/receipt.json`, 380,615 bytes, SHA-256
`352b2254cca632f644b8c55b236d6f4487801e9223e87810eb3db4596e7cfbcc`.
Compact receipt: [`receipts/EXP-325.json`](receipts/EXP-325.json).

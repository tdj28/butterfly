# EXP-357 — Third crossing correction

Status: failed; fixed-c correction reaches a conditioning floor

EXP-356 halves the maximum defect to `4.10058e-6` while remaining interior and
actively descending. EXP-357 binds its exact nodes and repeats the unchanged
fixed-`c`, 128-arc correction. Passing qualifies the curve point; the exact
fixed-`a` intersection remains separate.

Manifest:
[`../../experiments/manifests/EXP-357-jones-homoclinic-crossing-correction-3.json`](../../experiments/manifests/EXP-357-jones-homoclinic-crossing-correction-3.json).

The run remains failed at maximum defect `3.76458e-6` and
`a=0.17981749003698058`. Optimizer optimality collapses to `2.20e-10`, so the
same fixed-`c` correction has reached a conditioning floor. The nodes remain
interior with `0.97717` normalized margin.

These corrected nodes are nevertheless only `1.74900e-5` from exact
`a=0.1798`, about 51 times closer than the qualified EXP-350 source used by
the first direct solve. They are therefore preserved for a renewed fixed-`a`,
solved-`c` correction rather than another same-point restart.

Raw receipt: `artifacts/EXP-357/receipt.json`, 31,790 bytes, SHA-256
`622add457335304fed9b3269b747a3034c8cb2e1806433ad4c9a07a7eba4d685`.

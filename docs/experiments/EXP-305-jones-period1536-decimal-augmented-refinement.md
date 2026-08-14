# EXP-305 — Multi-resolution classical refinement of the eighth-flip candidate

Status: completed — failed only Richardson recovery into the EXP-302 bracket

EXP-304 validates a primitive 50-digit discrete augmented solution but fails
physical bracket and raw tangent-coordinate neighborhood gates at 1,024 RK4
steps per segment. EXP-305 preserves that failure and warm-starts 2,048- and
4,096-step classical-RK4 profiles with the same 2,048 orbit/tangent nodes and
8-by-8 cyclic Newton system.

Both `a` and period increments must converge at fourth order with ratios in
`[12,20]`. The fourth-order Richardson coordinate from 2,048/4,096 steps must
enter the untouched `1.04e-13` bracket. Every profile retains the `1e-22`
augmented residual and primitive half-node gates; finest nodes remain within
`1e-3`, and every pointwise tangent line—not its scale-dependent raw
coordinates—must agree with the pilot to absolute cosine at least `0.99`.

A pass validates a resolution-converged classical tableau sequence only. An
independent RK4 3/8 sequence remains mandatory before an eighth event is
promoted.

Manifest:
[`../../experiments/manifests/EXP-305-jones-period1536-decimal-augmented-refinement.json`](../../experiments/manifests/EXP-305-jones-period1536-decimal-augmented-refinement.json).

## Result

The multi-resolution numerical sequence is internally successful. Both new
profiles converge at 50 decimal digits. Their final orbit/tangent residuals are
`1.26e-33/5.06e-32` at 2,048 steps per segment and
`7.70e-28/1.31e-24` at 4,096 steps per segment, all below the frozen `1e-22`
gate. The parameter and period increment ratios are `15.7178` and `15.7060`,
consistent with fourth-order convergence. Primitive half-node RMS remains
`7.99e-6`; maximum node motion is `2.60e-7`; and the minimum pointwise
tangent-line cosine is `0.9999999999999599`.

The fourth-order Richardson coordinate is
`a=0.24070100822409128130272349728517`, however, which lies
`1.362e-11` below the lower endpoint of EXP-302's untouched bracket. The
receipt therefore fails exactly one gate, `extrapolated_a_bounds`, and no
eighth event is promoted.

This is a diagnostic failure of the inherited physical bracket, not of the
cyclic augmented formulation or its resolution convergence. EXP-302's
`1.04e-13` interval came from block-Floquet evaluation of continuation rows
whose orbit-correction uncertainty is larger than that interval. The next
experiment must independently recorrect a target-blind ladder of child
endpoints, then locate a fresh stable/unstable bracket before any independent
RK4 3/8 event sequence is attempted.

Raw receipt: `artifacts/EXP-305/receipt.json`, 702,705 bytes, SHA-256
`095cbdb2e5c7421371428fa43fb92f3ab10fe1e139dcfd0a5f70dd724b95fb19`.
Compact receipt:
[`receipts/EXP-305.json`](receipts/EXP-305.json).

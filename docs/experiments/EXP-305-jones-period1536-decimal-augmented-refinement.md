# EXP-305 — Multi-resolution classical refinement of the eighth-flip candidate

Status: frozen before execution

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

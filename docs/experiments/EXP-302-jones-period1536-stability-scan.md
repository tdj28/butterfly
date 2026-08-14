# EXP-302 — Scan the first period-1536 stability loss

Status: frozen before execution

EXP-299 independently classifies the primitive period-1536 source child as
stable; EXP-301 independently classifies the deterministic step-16 child as
unstable. EXP-302 scans every one of the 18 exact accepted EXP-300 rows from
the source through step 16. The failed continuation is admitted only as this
complete frozen prefix, and every source matching residual must remain below
`1e-8`.

DOP853 block-Floquet spectra are evaluated at four cyclic shifts per row. The
dominant transverse modulus is tracked without assuming a real `-1` flip.
Initial stability, terminal instability, cyclic relative-modulus agreement
within `0.02`, and at least one modulus-one bracket are mandatory. Real `-1`
and real `+1` brackets are reported separately only when their endpoint
imaginary parts remain below `1e-6`.

A pass nominates the first observed child stability boundary for an exact
independent refinement. It does not establish whether the boundary is a flip,
fold, or complex-pair crossing, and it does not establish an eighth event or a
period-3072 child.

Manifest:
[`../../experiments/manifests/EXP-302-jones-period1536-stability-scan.json`](../../experiments/manifests/EXP-302-jones-period1536-stability-scan.json).

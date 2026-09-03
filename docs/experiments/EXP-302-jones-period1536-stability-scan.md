# EXP-302 — Scan the first period-1536 stability loss

Status: completed — passed

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

## Result

All 18 rows pass. The source multiplier is real and stable at
`-0.1241962800`; the first continuation row is real and unstable at
`-4.4951424055`. EXP-302 therefore isolates exactly one stability-loss bracket
in the first interval,
`a in [0.24070100823770973, 0.24070100823781396]`, only `1.04e-13` wide. The
same interval is a real-`-1` endpoint bracket and nominates the next cascade
flip.

All source matching residuals remain below `9.97e-9`. Four-shift cyclic
relative-modulus spread is at most `2.35e-6`, far below the frozen `0.02`
ceiling. The negative multiplier reaches `-36.02`, returns toward the origin,
and changes to a positive real branch between scan indices 8 and 9 without
ever returning inside the unit circle. That coarse later interval is reported
as both real `-1` and `+1` endpoint brackets but is not interpreted: an
unsampled complex-pair or mode-exchange episode remains possible.

The first bracket is now admissible for a separately frozen augmented exact
period-1536 orbit-plus-antiperiodic-tangent solve. Until that succeeds, this is
a nominated eighth event—not an exact event or a period-3072 birth.

Raw receipt: `artifacts/EXP-302/receipt.json`, 46,448 bytes, SHA-256
`d3b23f17076d21ed890c5a3ab41afdd3270042ec7beaa99a9a1712cbf5372c4b`.
Compact receipt:
[`receipts/EXP-302.json`](receipts/EXP-302.json).

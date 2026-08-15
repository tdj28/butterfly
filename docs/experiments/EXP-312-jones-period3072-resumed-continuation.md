# EXP-312 — Resume the period-3072 branch from the exact EXP-311 prefix

Status: completed — failed the point-count and event-separation gates

EXP-311 passes all four full-step corrections and every orbit-level gate, but
the branch bends across the finite event coordinate and ends only `7.77e-13`
away. EXP-312 binds the raw EXP-311 receipt and resumes from its final two
rows. The complete five-row source prefix must be successful, retain matching
below `1e-8`, and retain primitive half-node RMS above `5e-6` before it can be
used.

The resumption permits eight pseudo-arclength corrections at nominal step
`0.000625`, with deterministic halving down to `0.00001953125` only on
correction failure. All nine resumed rows and at least `1e-11` terminal
absolute separation from the finite event coordinate are required, together
with the unchanged matching, primitive separation, terminal closure, neutral,
period-ratio, half-period nonclosure, and exact `3584/4096` identity gates.

A pass supplies farther exact period-3072 rows for a separately frozen
DOP853/Radau audit. It does not classify stability or eighth-birth direction.

Manifest:
[`../../experiments/manifests/EXP-312-jones-period3072-resumed-continuation.json`](../../experiments/manifests/EXP-312-jones-period3072-resumed-continuation.json).

## Result

EXP-312 accepts six resumed rows before step 6 misses the matching gate at the
frozen minimum arclength. The first three new rows pass at `0.000625`; step 3
passes at `0.0003125`, step 4 at `0.000078125`, and step 5 at the minimum
`0.00001953125`. The rejected next row has matching residual
`1.00429e-8 > 1e-8`. The result therefore has seven rather than nine resumed
rows and ends `4.744e-12`, rather than `1e-11`, from the finite event.

Every accepted row retains matching below `1e-8`, and half-node RMS grows from
`5.41e-5` to `9.53e-5`. Terminal full closure (`1.16e-4`), neutral mode
(`3.41e-3`), half-period nonclosure (`1.19e-4`), period ratio, and exact
`3584/4096` identity pass. The preliminary terminal multiplier `-58.924` is
not an independent stability result and is discarded.

The first accepted row whose absolute finite-event separation reaches
`4e-12` is step 3 at `a=0.24070100821872153`. That threshold is nearly four
times the finite-to-Richardson coordinate shift in the bound event receipt,
and the row was selected without any multiplier. A prospective independent
audit may bind this exact failed-receipt prefix; it must retain the unchanged
`1e-4` stability-classification margin and cannot promote EXP-312 as passed.

Raw receipt: `artifacts/EXP-312/receipt.json`, 1,766,926 bytes, SHA-256
`d12f7e73df018745e031384c1174342a39a45e8982f69312f589935db5258e02`.
Compact receipt: [`receipts/EXP-312.json`](receipts/EXP-312.json).

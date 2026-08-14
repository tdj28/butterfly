# EXP-300 — Continue the stable period-1536 candidate away from neutrality

Status: completed — failed at the frozen point-count gate

EXP-299 independently classifies the EXP-298 positive-mode primitive
period-1536 child as stable under DOP853 and Radau, but the common coordinate
is only about `1e-12` from the finite 8,192-step event coordinate. The
period-768 parent therefore remains inside the unchanged `1e-4` neutral
classification margin.

EXP-300 continues the same prospectively selected child for 32 frozen sparse
pseudo-arclength steps of `0.0003125`, with step halving permitted only on
correction failure down to `0.000009765625`. All 33 rows, at least `1e-11`
terminal separation from the finite event coordinate, matching below `1e-8`,
persistent half-node separation, terminal full/half closure, neutral mode,
period ratio two, and exact `1792/2048` section identity are mandatory.

A pass supplies a farther exact period-1536 child for a separately frozen
DOP853/Radau parent/child criticality audit. It does not classify terminal
stability or establish a supercritical seventh birth by itself.

Manifest:
[`../../experiments/manifests/EXP-300-jones-period1536-qualified-continuation.json`](../../experiments/manifests/EXP-300-jones-period1536-qualified-continuation.json).

## Result

EXP-300 accepts 22 continuation steps plus the source row before the next
correction exhausts the frozen minimum step. It therefore fails the required
33-row gate with 23 rows and is not promoted as a passed continuation.

The accepted prefix is nevertheless exact within every row-level gate. All
matching residuals are below `1e-8`; half-node RMS grows continuously from
`6.31e-6` to `1.277e-4`. Four deterministic halvings are needed at step 15,
after which seven more steps pass at `1.953125e-5`. Step 22 then misses the
matching gate at both permitted trials, ending at `1.00075e-8` under the
minimum step.

The terminal accepted row lies `7.56e-11` from the finite event coordinate and
passes full closure (`4.33e-5`), neutral (`2.60e-3`), half-period nonclosure
(`1.85e-5`), and exact `1792/2048` section identity. Its direct multiplier
`-45.30` is only a preliminary long-product diagnostic and is not promoted.

The first accepted row that crosses the prospectively declared `1e-11`
separation is step 16 at `a=0.24070100822533044`. It has matching residual
`9.82e-9` and half-node RMS `1.255e-4`. A new prospective protocol may select
that first-threshold row and independently recorrect both parent and child; it
must not reinterpret the failed EXP-300 receipt as a passed continuation.

Raw receipt: `artifacts/EXP-300/receipt.json`, 2,907,391 bytes, SHA-256
`c91fadcd01f8ac6095b97538796cc7e4c25b51a1af94f15531bb47e14ab41bf8`.
Compact receipt:
[`receipts/EXP-300.json`](receipts/EXP-300.json).

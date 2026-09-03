# EXP-317 — Tight segmented identity audit for period 3072

Status: passed

EXP-316 preserves a failed long single-shot half-period gate even though its
two independently corrected children agree to `3.34e-10` node RMS and retain
`9.01896e-6` aligned half-node separation. EXP-317 tests that discrepancy
without changing EXP-316.

Each event-relative child is freshly corrected using a tighter solver profile:
DOP853 at `3e-12/3e-14`, Radau at `3e-11/3e-13`, both with maximum step `0.01`.
For each corrected 4,096-node orbit, the two 2,048-node halves are compared
over every cyclic phase. Minimum separation must remain at least `5e-6` and at
least 100 times the largest base-to-tight or cross-solver node RMS. Matching,
phase, period agreement, and the bound exact `3584/4096` source identities are
also required.

A pass qualifies segmented primitive identity and may be combined with
EXP-316's unchanged stability evidence to promote a local subcritical eighth
birth. It does not make the failed EXP-316 single-shot gate pass.

Manifest:
[`../../experiments/manifests/EXP-317-jones-period3072-segmented-identity.json`](../../experiments/manifests/EXP-317-jones-period3072-segmented-identity.json).

## Result

EXP-317 passes after 1,330.49 seconds. The tighter DOP853 and Radau corrections
both terminate in one evaluation with matching residuals
`2.12e-10/1.45e-10`. Neither correction moves its source nodes at Float64
resolution.

After minimizing over all 2,048 cyclic phase shifts, the two orbit halves
remain separated by `8.66424730e-6/8.66424725e-6`; both select shift 1024.
The independent solver representations differ by only `3.34029e-10` RMS, so
the minimum primitive separation is `25,938.6` times the largest empirical
representation error, far above the frozen factor-100 gate. Period difference
is `1.22e-7`, and the bound exact `3584/4096` identities remain valid.

This independently qualifies segmented primitive period-3072 identity. In
combination with EXP-316's stable-parent/unstable-child classifications, it
promotes the eighth birth as locally subcritical. EXP-316's failed long
single-shot half-period gate remains a preserved failure and is not reclassified.

Raw receipt: `artifacts/EXP-317/receipt.json`, 505,250 bytes, SHA-256
`eef0f6c1e5171a4cb8028503c852e559132e5b28b2dd096ee0cb299bb1cedea3`.
Compact receipt: [`receipts/EXP-317.json`](receipts/EXP-317.json).

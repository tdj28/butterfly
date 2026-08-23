# EXP-317 — Tight segmented identity audit for period 3072

Status: frozen; not yet executed

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

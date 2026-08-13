# EXP-287 — Independent decimal Richardson audit for period 768

Status: passed

EXP-286 qualifies a converged 50-digit classical-RK4 Richardson multiplier at
the immutable EXP-281 coordinate. EXP-287 independently integrates all 1,024
segments with the distinct fourth-order RK4 3/8 tableau at 4,096, 8,192, and
16,384 steps per segment.

The independent sequence must show fourth-order raw convergence, successive
Richardson convergence, a flip residual within `1e-7`, and agreement with the
classical extrapolation within `1e-7`. Analogous neutral gates and cyclic,
characteristic, orbit, tangent, primitive, and exact-section gates remain
mandatory.

A pass qualifies the seventh exact numerical real-`-1` event and tangent
representation by two independently tableaued high-precision sequences. A
period-1536 switch, stability exchange, scaling law, and universality remain
separate prospective claims.

EXP-287 passed all thirteen frozen gates from clean commit
`d5bfe74897f9706ee15965b723aaf6f2184a41e7`. The independent RK4 3/8 raw
sequence converges with ratio `15.9599`. Its successive order-four Richardson
flip estimates differ by `1.06e-8`; the newest estimate is
`-0.9999999948805051`, only `5.12e-9` from `-1` and `5.22e-11` from the
classical-RK4 estimate. The corresponding neutral multiplier is
`0.9999999618242136`, with `7.13e-13` cross-tableau difference.

The finest independent profile also retains cyclic spread `7.64e-44`, maximum
characteristic residual `1.00e-49`, orbit/tangent matching below
`3.76e-11/1.02e-11`, proper-subperiod separation `7.54e-6`, and exact
`896/1024` section identity. The raw receipt is 9,117 bytes with SHA-256
`b0535b124411e3d7f4a18852843a9f47224ab4497bc9f27c10ecd9d8ccde939a`.

This independently rehabilitates the immutable EXP-281 representation and
qualifies the seventh exact numerical real-`-1` event at
`a=0.2407010081734325`. It does not yet qualify a period-1536 child or determine
the seventh event's criticality.

Manifest:
[`../../experiments/manifests/EXP-287-period768-decimal-independent-richardson.json`](../../experiments/manifests/EXP-287-period768-decimal-independent-richardson.json).

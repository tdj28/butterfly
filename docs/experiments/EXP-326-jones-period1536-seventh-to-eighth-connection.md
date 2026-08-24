# EXP-326 — Connect the seventh daughter to the eighth event

Status: completed — failed only integer-node phase identity

EXP-324/325 qualify collapse of the old EXP-299 higher-`a` seed. That retracts
the primitive/stability interpretation behind EXP-299 and the inherited
EXP-300--302 micro-bracket. It does not erase EXP-306's independently
converged primitive period-1536 real-`-1` root, but it reopens whether that
root lies on the immediate daughter sheet born at event seven.

EXP-326 binds the exact 4,096-step EXP-321 daughter continuation and the
algebraically independent 4,096-step EXP-306 event profile. It prospectively
continues four more 50-digit pseudo-arclength rows with the unchanged step and
map. Those rows must uniquely bracket the target event coordinate. A
parameter-interpolated seed is then corrected at the target's exact discrete
`a` coordinate with step-scaled Armijo damping.

A pass requires `1e-20` continuation and target correction, primitive
half-node RMS at least `5e-6`, phase-invariant target agreement within `1e-8`
node RMS, target-period agreement within `1e-6`, and unchanged cyclic and
neutral Floquet gates. It qualifies one bounded numerical sheet connection;
it does not prove global uniqueness or full-plane topology.

Manifest:
[`../../experiments/manifests/EXP-326-jones-period1536-seventh-to-eighth-connection.json`](../../experiments/manifests/EXP-326-jones-period1536-seventh-to-eighth-connection.json).

## Result

All four continuation rows pass below `9.41e-22`. They cross the target
coordinate between rows with dominant transverse moduli `0.90215` and
`1.33360`. Fixed-`a` correction of the interpolated seed then reaches
`8.98e-23` matching in two full Newton steps. The orbit remains primitive with
half-node RMS `7.9884935e-6`, its period differs from the target by only
`3.13e-22`, and it independently recovers multiplier
`-1.0000000000002505`.

The frozen receipt fails only `node_identity`: the best integer shift is 1024
nodes but leaves `1.1986e-6` RMS. Diagnosis shows that shifted target nodes
violate the connected orbit's continuous phase hyperplane by `3.16e-6`.
EXP-327 freezes exact shared-phase correction rather than relaxing or
reclassifying this failed gate.

Raw receipt: `artifacts/EXP-326/receipt.json`, 1,740,694 bytes, SHA-256
`f94a3c63dad90c729138c4902b5af44d7194bda42dd18c42f730737f640ff89f`.
Compact receipt: [`receipts/EXP-326.json`](receipts/EXP-326.json).

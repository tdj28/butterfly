# EXP-232 — Residual-safe exact period-12 flip localization

Status: complete — passed all frozen gates

EXP-231 stops administratively when Radau reports `xtol` termination at the
right endpoint despite raw closure `6.76e-9` and phase residual `2.09e-19`.
EXP-232 retains the bracket, solvers, exact source-event correction, bilateral
points, and every scientific threshold.

The sole change is receipt-visible correction handling: `success=false` is
accepted only for the exact `xtol` message and only when raw correction closure
is at most `2e-8` and phase residual at most `1e-8`. Root primitivity, `7/8`
versus `14/16` section identity, multiplier/neutral residuals, bilateral
stable/unstable exchange, and DOP853/Radau root agreement remain mandatory.

A pass establishes an exact sampled period-12 flip on this path. It does not
establish a stable period-24 child or supercriticality.

Manifest:
[`../../experiments/manifests/EXP-232-returning-period12-flip-residual-safe.json`](../../experiments/manifests/EXP-232-returning-period12-flip-residual-safe.json).

## Result

Both solvers independently localize the primitive period-12 real-`-1` event.
DOP853 gives `(a,c)=(0.240701181475830,7.625815600403827)` with multiplier
residual `8.71e-10`; Radau gives
`(0.240701180130267,7.625815566597550)` with residual `9.84e-8`. The roots
differ by `3.38e-8` in `c`, inside the frozen `2e-7` gate.

Both roots retain primitive period ratio `2.00005253`, minimum proper-
subperiod closure `0.0436954`, parent/child section counts `7/8` versus
`14/16`, and all orbit/correction gates. At `c_root-1.5e-4`, the child
multipliers are `-0.99872263` and `-0.99872220`; at `c_root+1.5e-4`, they are
`-1.00127807` and `-1.00127801`. Thus both solvers qualify stable-before and
unstable-after primitive period-12 behavior.

This establishes an exact sampled period-12 flip on the corrected returning-
arm offset path. It is a cascade rung, not the endpoint previously inferred
from interpolation. EXP-233 freezes a multiscale doubled-period branch switch
to search for the period-24 child.

Raw receipt: `artifacts/EXP-232/receipt.json`, 16,804 bytes, SHA-256
`462f8d2992327d1289a53bd0ed019b113c41d5512787765c2a56fc0147e85fa6`.
Compact receipt:
[`receipts/EXP-232.json`](receipts/EXP-232.json).

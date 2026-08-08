# FND-032 — Seven additional primitive UPO families persist

Status: qualified partial result from failed EXP-139

## Finding

Seven of the eight previously uncontinued primitive lower-side UPO families
reach `a=0.14825` on the frozen 21-point grid. These comprise lags 3, 5, 8,
three distinct lag-7 families, and one lag-13 family. All 147 points pass flow
closure, neutral Floquet accuracy, proper-divisor nonclosure, transverse
instability, and phase-robust fundamental crossing identity.

Lag-13 family 01 passes through `a=0.148025`, then its natural corrector stops
at `a=0.1480375`. The optimizer reports `xtol` convergence and closure
`1.0660e-10`: only `6.60e-12` above the corrector's internal `1e-10` success
floor, and well below the experiment's independent `1e-8` flow-closure gate.
Its last qualified point remains primitive and strongly unstable, with
unstable modulus `1718.23` and divisor nonclosure `10.50`.

## Consequence

The seven complete paths enlarge the cross-boundary periodic skeleton to ten
qualified persistent families when combined with EXP-136/138. The lag-13
family 01 stop is not presently evidence of orbit termination: its scale and
optimizer status make integration/correction precision the leading diagnosis.
EXP-140 therefore repeats only this family with tenfold tighter relative and
absolute integration tolerances and half the maximum DOP853 step.

EXP-140 passes the original stop but encounters the same `1e-10` internal
floor later, at the midpoint. This displacement rejects a boundary-locked
event interpretation of the raw corrector stop and exposes a systematic
threshold mismatch. EXP-141 freezes optimizer success separately from the
unchanged scientific orbit bounds.

Tracked receipt: `docs/experiments/receipts/EXP-139.json`.

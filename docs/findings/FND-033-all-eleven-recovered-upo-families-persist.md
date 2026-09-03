# FND-033 — All eleven recovered primitive UPO families persist

Status: qualified finite local census from EXP-136/138/139/141

## Finding

Every identity-qualified primitive UPO family recovered from the PIM saddles
at `a=0.148` and `a=0.14825` continues across the full 21-point interval at
fixed `(b,c)=(0.2,20)`:

- nine lower-seeded families with fundamental lags
  `3,5,7,7,7,8,12,13,13`;
- the independently distinct upper-seeded lag-12 family; and
- the upper-seeded lag-4 family.

EXP-141 closes the last numerical gap. Lag-13 family 01 passes all 21 points
when least-squares optimizer convergence is recorded separately from the
unchanged scientific `1e-8` closure criterion. Maximum corrected-seed closure
is `1.17e-10`, maximum independent flow closure `2.30e-9`, and every optimizer
succeeds. Its unstable modulus stays between `1696.69` and `1720.56`, proper-
divisor closure stays above `10.49`, and all shifted windows retain 13 Barrio
crossings.

## Consequence

For this finite recovered census, the two/three return-map transition is not
caused by:

1. creation or destruction of a recovered primitive UPO family;
2. conversion between the two recovered lag-12 families; or
3. a change in the fundamental Barrio-section crossing count of a recovered
   family.

The periodic skeleton persists while the chaotic-saddle return relation
changes. This strongly selects a global invariant-manifold connectivity,
admissibility/pruning, or reinjection event as the next mechanism class. It
does not prove that no unrecovered UPO bifurcates, nor does it identify the
specific manifold collision.

Tracked receipts: `docs/experiments/receipts/EXP-136.json`,
`EXP-138.json`, `EXP-139.json`, and `EXP-141.json` in the same directory.

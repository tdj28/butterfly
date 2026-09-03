# EXP-150 — Prospective UPO recovery across the `c=19.9` bracket

Status: passed prospective UPO recovery at both endpoints

## Question

Do both endpoints of EXP-132's newly qualified finite saddle-topology bracket
contain recoverable, identity-qualified unstable periodic orbits under the
unchanged EXP-133 PIM-seeded shooting procedure?

The cases are the two-branch saddle at `(a,b,c)=(0.145,0.2,19.9)` and the
three-branch saddle at `(0.150,0.2,19.9)`. Both use the already hashed
256-return EXP-132 PIM archive. No close-return distance, lag, corrected orbit,
or multiplier from either target was inspected before this manifest was
frozen.

## Frozen method and gates

The selector and numerical gates are copied unchanged from EXP-133: burn 100
PIM returns; rank scaled close returns at lags 2 through 20; retain at most one
candidate per lag and line below `1e-4`; and cap each endpoint at 18 candidates.
Every candidate must first close under exact DOP853 section returns within
`1e-3`, then pass phase-conditioned flow shooting, `1e-8` flow/phase closure,
`1e-4` neutral-multiplier accuracy, exact oriented crossing identity, and a
nontrivial multiplier modulus of at least `1.001`.

At least one accepted UPO is required at each endpoint. Passing establishes
recoverable periodic-skeleton seeds on a second transverse slice. It does not
establish uniqueness, primitivity, family correspondence with `c=20`, lobe
inclusion, a manifold event, or a continuous topology surface. Those require
separately frozen audits.

Immutable manifest:
`experiments/manifests/EXP-150-c19p9-pim-seeded-upo-discovery.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python scripts/discover_pim_seeded_upos.py \
  --manifest experiments/manifests/EXP-150-c19p9-pim-seeded-upo-discovery.json \
  --output artifacts/EXP-150/receipt.json
```

## Result

EXP-150 passes in `18.53` seconds. The two-branch endpoint yields 6 accepted
recoveries from 13 candidates at reported lags 3, 6, 10, and 13. The
three-branch endpoint yields 4 accepted recoveries from 5 candidates at lags
13, 14, and 15. Every accepted candidate clears exact-return, shooting,
closure, neutral-multiplier, section-identity, and instability gates.

Candidate counts are not yet distinct-family counts. EXP-151 applies the
pre-frozen divisor and continuous phase-identity audit to the hash-bound
receipt.

Tracked receipt: `docs/experiments/receipts/EXP-150.json`.

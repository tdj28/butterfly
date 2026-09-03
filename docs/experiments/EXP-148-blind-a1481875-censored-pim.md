# EXP-148 — Blind `a=0.1481875` PIM saddle

Status: passed blind two-branch qualification at both horizons

## Question

Does the untouched midpoint saddle have two or three scalar branches under the
identical qualified censor-aware PIM definition?

## Blind boundary

The complete midpoint UPO seed library and lobe atlas were frozen and executed
first. They establish only that a dense unstable-lobe reference exists. No PIM
trajectory, branch class, or left-lobe inclusion result at `a=0.1481875` has
been generated or inspected.

## Frozen design

EXP-148 repeats the EXP-128 blind PIM method with only `a`, identifiers, and the
deterministic bootstrap seed changed. Three fixed access lines are reconstructed
independently at 128- and 256-return censor ceilings. Each advances 800 returns
and discards 100. Both `y` and `z` must agree across all 15 fixed oracle
variants, with at least 2097 expected pooled pairs per coordinate/profile,
complete line support, no lifetime failures, and bounded within- and
cross-horizon critical-point drift.

The expected branch count is explicitly `null`. EXP-149 will later apply the
unchanged EXP-145 left-lobe threshold and distance gates to the hash-bound
EXP-147/148 artifacts. EXP-148 itself cannot use overlap to choose its class.

Immutable manifest:
`experiments/manifests/EXP-148-blind-a1481875-censored-pim.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python \
  scripts/qualify_censored_pim_saddle_controls.py \
  --manifest experiments/manifests/EXP-148-blind-a1481875-censored-pim.json \
  --output artifacts/EXP-148/receipt.json \
  --states-output artifacts/EXP-148/blind-a1481875-censored-pim-straddles.npz
```

## Interpretation boundary

A pass qualifies one additional finite PIM saddle class and enables the first
prospective lobe-inclusion association test. It does not locate a continuous
boundary or prove an exact manifold connection.

## Result

The clean eight-worker run passes after `4356.37` seconds. All three access
lines resolve at both 128 and 256 returns with no lifetime-evaluation failure.
Both `y` and `z` select two branches in all 15 oracle variants at both
horizons, with 2097 post-burn-in pairs per coordinate/profile and consensus
one. The nested critical-point spans are `0.008410` in `y` and `0.005129` in
`z`, both within the frozen gates. The finite sampled bracket narrows to
`[0.1481875,0.14825]`.

Tracked receipt: `docs/experiments/receipts/EXP-148.json`.

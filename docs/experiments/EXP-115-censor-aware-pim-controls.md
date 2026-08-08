# EXP-115 — Censor-aware PIM saddle controls

Status: preregistered; target controls not executed

## Hypothesis

The right-censored PIM construction in DEC-009 independently recovers a
two-branch saddle at `(a,b,c)=(0.118,0.2,20)` and a three-branch saddle at
`(0.149,0.2,20)` on the Barrio section, with stable critical locations at two
nested censor horizons.

## Frozen method

The adaptive DOP853 section return, stable period-4 reference cycle, capture
neighborhood, state scaling, and 15-variant branch oracle are inherited from
EXP-114. Three prospectively fixed lines cover `y=[-38,-8]` at
`z=0.0090,0.0096,0.0102`. Each line uses 33-point refinements to normalized
bracket width `1e-7`.

A captured point contributes its exact capture time. A point surviving the
declared return horizon contributes only a right-censored lower bound. A
contiguous censored block can be selected only when captured adjacent points
on both sides have strictly shorter exact lifetimes; boundary blocks and
integration failures are rejected. No censored lifetime is converted to an
exact value.

The complete construction is repeated independently at 64- and 128-return
censor horizons. Each resolved straddle is advanced for 800 returns; the first
100 are discarded. Raw middle-point states, line identities, censor counts,
certified-block counts, source commit, manifest hash, and artifact hash are
retained.

## Acceptance criteria

Each case and censor horizon must have:

- the independently reconstructed attracting control classified as period 4;
- at least two of three complete straddles and no integration failure;
- at least 1000 pooled consecutive return pairs per coordinate;
- all 15 branch-oracle variants agreeing on the expected two/three count;
- within-profile normalized critical-location span at most `0.03`; and
- combined EXP-112/PIM critical-location span at most `0.05`.

In addition, the 64- and 128-return profiles must have the same accepted
topology and a combined normalized critical-location span at most `0.04` in
both `y` and `z`. The whole experiment passes only if both controls pass every
profile and nested-horizon gate.

## Frozen execution

```sh
PYTHONPATH=python ./.venv/bin/python \
  scripts/qualify_censored_pim_saddle_controls.py \
  --manifest experiments/manifests/EXP-115-censor-aware-pim-controls.json \
  --output artifacts/EXP-115/receipt.json \
  --states-output artifacts/EXP-115/censor-aware-pim-straddles.npz
```

Target execution is forbidden until the implementation, tests, decision,
manifest, and this record are committed with a clean source tree.

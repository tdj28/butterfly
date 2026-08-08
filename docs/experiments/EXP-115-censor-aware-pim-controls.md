# EXP-115 — Censor-aware PIM saddle controls

Status: failed prospectively; fixed-128-horizon two-control result retained

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

The preregistration forbade target execution until the implementation, tests,
decision, manifest, and this record were committed with a clean source tree.

## Result

The complete experiment fails after `5574.91 s`. Both 64-return profiles fail,
so neither control has a resolved nested-horizon comparison. There are no
adaptive integration failures.

The failure modes are support failures, not contradictory branch labels. At
the unimodal control, all three 64-return straddles complete and provide 2097
pairs, but both coordinate projections fail the frozen `0.7` invariant-domain
coverage gate. At the bimodal control, only one of three 64-return lines
resolves, giving 699 pairs and missing the two-straddle/1000-pair gates.

Both 128-return profiles pass every per-profile gate. Three unimodal straddles
recover two branches and three bimodal straddles recover three, in `y` and `z`,
with all 15 oracle variants agreeing. The largest within-PIM critical span is
`0.01501`; the largest combined EXP-112/PIM span is `0.01511`. Each profile has
2097 pairs and zero integration failures.

The 41,177-byte raw receipt has SHA-256
`f7b483334fa911ace7c11c499bb38d97756fb4623535c5200f7f606ea7d7e9b5`.
The 116,376-byte state NPZ has SHA-256
`73962228b0d037c4e2c6e9dd16fc4b1a681af750e09aaf108a780459fc55b551`.
The tracked compact receipt is `docs/experiments/receipts/EXP-115.json`.

## Interpretation and next action

EXP-115 is not relabeled as passed. Its qualified subset is the first
independent PIM/DOP853 two-control corroboration at a fixed 128-return censor
horizon. The failed 64-return profiles prove that the censor ceiling affects
invariant-domain coverage and stable-set access rather than only computation
time.

Freeze a successor that compares the accepted 128-return result against a
256-return censor-aware reconstruction. Require both controls, coordinates,
all oracle variants, critical-location stability, and zero integration
failure before using PIM for saddle-boundary continuation.

# EXP-145 — UPO-lobe/PIM-saddle overlap

Status: passed retrospectively; prospective held-out test required

## Question

Does the UPO unstable escape lobe overlap the invariant PIM saddle only on the
qualified three-branch side of the local transition?

## Frozen design

All sources are hash-bound: the EXP-143 capture-truncated atlas and the
EXP-125/128 PIM receipts and state archives. The left lobe is defined by the
qualified three-side critical interval as
`y < -31.135026064071056`. Distances use both Barrio-section coordinates with
scales `(30, 0.0006)`.

The two-branch endpoint must have no post-burn-in PIM state in the left lobe on
any of three access lines at either 128 or 256 returns. The three-branch
endpoint must have at least ten per access line and horizon. Every retained
three-side PIM lobe state must lie within scaled distance `5e-5` of the full
nine-amplitude unstable atlas and `1e-4` of its nested five-amplitude subset.
Both atlas subsets must retain adequate lobe support.

Immutable manifest:
`experiments/manifests/EXP-145-upo-lobe-pim-overlap.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python scripts/analyze_upo_lobe_pim_overlap.py \
  --manifest experiments/manifests/EXP-145-upo-lobe-pim-overlap.json \
  --output artifacts/EXP-145/receipt.json
```

## Interpretation boundary

The run is retrospective and its finite PIM point clouds are not exact stable
manifolds. A pass would show that the left unstable lobe is excluded from the
qualified two-branch saddle but represented by the qualified three-branch
saddle, under nested atlas density and independent access-line/horizon
controls. A prospective held-out parameter and an eventual high-precision or
boundary-value connection solve remain mandatory.

## Result

The clean `ac65b0b` run passes in `0.0361 s`. The UPO atlas contains 1089
fine-grid and 617 coarse-grid two-side points in the declared left lobe, but
all six qualified two-side PIM access-line/horizon combinations contain zero
left-lobe states. Thus the geometric lobe exists but is excluded from the
reconstructed two-branch saddle.

The three-side atlas contains 956 fine-grid and 550 coarse-grid lobe points.
Every PIM access line contains 11–15 left-lobe states at both horizons. The
largest directed PIM-to-atlas distance is `2.399e-5` on the fine grid and
`6.099e-5` on the coarse grid, inside the frozen `5e-5`/`1e-4` limits.

Raw receipt SHA-256:
`4cc45edde38fe417563d954945bb0cd16776636090b43ff7943e0515beaedd62`.

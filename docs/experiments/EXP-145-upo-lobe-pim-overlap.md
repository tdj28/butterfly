# EXP-145 — UPO-lobe/PIM-saddle overlap

Status: frozen retrospective diagnostic; not yet executed

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

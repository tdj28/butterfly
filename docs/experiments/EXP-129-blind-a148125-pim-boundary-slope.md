# EXP-129 — Blind `a=0.148125` PIM and lower-support slope prediction

Status: passed

## Question

Does a frozen signed lower-support derivative predict the blind PIM branch
count at the midpoint of the qualified `[0.148,0.14825]` bracket?

## Calibration boundary

The derivative definition, sign mapping, and `0.1` minimum magnitude were
chosen after exploratory inspection of hashed existing PIM states. Eight
calibration profiles cover the published `a=0.118` two-branch and `a=0.149`
three-branch controls and the local `a=0.148` two-branch and `a=0.14825`
three-branch endpoints, each at 128 and 256 returns. All calibration archive
hashes and expected signs are frozen in the manifest. This is calibration,
not held-out evidence.

No target state at `a=0.148125` has been generated or inspected. Its expected
branch count is `null`.

## Frozen design

The target repeats the complete EXP-128 adaptive-DOP853 PIM construction with
only `a` and the deterministic bootstrap seed changed. Three fixed access lines
are reconstructed at 128- and 256-return right-censor ceilings. Each complete
straddle advances 800 returns and discards 100.

Two statistics are computed from each pooled coordinate/profile sample:

1. the existing gated critical-point branch count across all 15 bin/smoothing
   variants; and
2. the derivative of each normalized fitted relation at its first populated
   binned-source median.

Negative slope predicts two branches and positive slope predicts three. Every
variant in `y` and `z` at both horizons must share one sign, the smallest
absolute slope must be at least `0.1`, and the one slope-predicted class must
equal the blind branch count. All earlier PIM line, integration, pair-count,
oracle-consensus, and within/cross-horizon critical-location gates remain.

If the common blind result is two, the finite bracket becomes
`[0.148125,0.14825]`. If it is three, it becomes `[0.148,0.148125]`. A slope,
branch, numerical, or agreement failure leaves `[0.148,0.14825]` unchanged.

This experiment can qualify a local signed companion observable. It cannot by
itself prove that the derivative varies continuously in `a`, that its zero is
unique, or that a codimension-one TBA curve exists throughout the plane.

Immutable manifest:
`experiments/manifests/EXP-129-blind-a148125-pim-boundary-slope.json`.

## Reproduction command

```bash
PYTHONPATH=python .venv/bin/python \
  scripts/qualify_censored_pim_saddle_controls.py \
  --manifest experiments/manifests/EXP-129-blind-a148125-pim-boundary-slope.json \
  --output artifacts/EXP-129/receipt.json \
  --states-output artifacts/EXP-129/blind-a148125-censored-pim-straddles.npz
```

The target must run from the clean preregistration commit. Raw artifacts remain
outside Git; the result checkpoint will add a compact tracked receipt with
SHA-256 hashes.

## Result

EXP-129 passes from clean pushed commit `5178607` in `4374.08 s`. All six PIM
access lines complete. Both horizons provide 2097 retained pairs in each
coordinate, and all 60 branch-oracle cells return two branches.

The signed prediction also passes without ambiguity. Every one of 60 slope
fits is negative. The `y` interval is `[-1.2032,-0.4994]` and the `z` interval
is `[-1.4185,-0.8476]`, comfortably beyond the frozen `0.1` magnitude floor.
Both horizons therefore predict two branches and agree with the blind critical-
point count. Maximum cross-horizon critical span is `0.009643` in `y` and
`0.005037` in `z`. There are two certified censored selections at 128 returns,
none at 256, and no failed integration.

The finite sampled bracket becomes `[0.148125,0.14825]`. This prospectively
qualifies the slope sign as a local companion observable; it does not prove the
existence or continuity of a zero-level TBA curve.

Tracked compact receipt: `docs/experiments/receipts/EXP-129.json`. Raw receipt
SHA-256:
`d50719b5ec92994bdf5bc0e80cb5dfc850a0d49646f56b3f79962342d5080698`.

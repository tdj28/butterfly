# EXP-346 — Radius-0.02 nuisance-gauge validation

Status: passed; three-radius numerical homoclinic sequence qualified

EXP-345 solves the radius-`0.02` matching equations below `1e-8` and preserves
`a` to `4.34e-13`, but its nearly null departure-angle coordinate reaches the
frozen boundary. EXP-346 binds those exact nodes and performs no further
optimization.

Only the nuisance-angle half-width is widened from `0.15` to `0.5`. Radius,
physical geometry, 32 Radau arcs, the `a` box, and the prospective `1e-8`
residual and `2e-6` parameter-persistence gates remain unchanged. The exact
seed must reproduce and be interior in a single evaluation.

Passing establishes numerical persistence across matching radii `0.03`,
`0.025`, and `0.02`. It does not establish the exact radius-to-zero limit,
Jones's printed coordinate, or uniqueness.

Manifest:
[`../../experiments/manifests/EXP-346-jones-homoclinic-radius020-gauge-validation.json`](../../experiments/manifests/EXP-346-jones-homoclinic-radius020-gauge-validation.json).

## Result

The exact nodes reproduce at maximum block defect `5.60724e-9` and have
minimum normalized boundary margin `0.62557`. All gates pass without further
optimization. The parameter `a=0.18264360817372402` differs from the
radius-`0.025` source by `4.34e-13`.

Together with EXP-342 and EXP-344, this establishes a three-radius numerical
root sequence under independent DOP853/Radau and 16/32-arc representations.
It strongly qualifies a homoclinic connection at the revised coordinate, not
the paper's printed `a=0.1798`, and leaves curve continuation and uniqueness
open.

Tracked summary: [`receipts/EXP-346.json`](receipts/EXP-346.json). Raw receipt
SHA-256: `102f62fb9206b22e409977bf1ab8f5856344caa128a789c9e4de8499bb0f8265`.

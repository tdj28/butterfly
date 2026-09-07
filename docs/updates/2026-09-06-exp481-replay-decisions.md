# EXP-481: the raw-to-decision path passes its synthetic control

## What changed, in plain language

The experiment can now carry recorded crossings all the way into a common
trajectory sample and a joint return-map decision. It cannot claim success
by losing a difficult numerical profile, choosing a favorable time window,
dropping a fit variant, or silently replacing excluded trajectories.

This is useful engineering progress toward testing Jones's symbolic mechanism.
It is **not a new Rössler result**: no target trajectories were generated, and
no Jones letter, symbolic arrow or homoclinic claim was verified in this step.
The [numeric proposal](../experiments/EXP-481-sampling-and-analysis-proposal.md)
remains unreviewed and target execution remains disabled.

## Auditable path

- `paired_replay.py` checks expected source/design bindings, input seeds and
  externally supplied journal receipt hashes. Incomplete or changed journals
  cannot enter analysis. Pair indices still point back to raw committed event
  arrays; per-seed batch provenance survives the global-ID join.
- Both numerical profiles use the intersection of retained original IDs,
  with fixed calibration/holdout membership. Every population count and
  intersection loss is reported. Missing batches, duplicate IDs, substituted
  candidates and inconsistent population totals are rejected.
- `paired_decisions.py` requires the complete declared primary fit family in
  both windows and profiles. Conflicting branch counts, wide or overlapping
  ordered turning regions remain unresolved. Diagnostic coordinates cannot
  rescue the primary coordinate.
- Every supplied cycle point is compared with every turning region under
  every primary fit. The table preserves misses and unsupported points;
  unsupported slopes are null, not extrapolated. A one-branch map has no
  turning-region claim. The production wrapper must still bind the exact six
  reference rows and enforce complete two-case reporting.

Optional retained splines serialize knots, coefficients and support masks,
not executable Python objects. Tests verify identical reconstructed values
and derivatives after JSON round-trip, and unchanged analysis results when
model retention is toggled. The proximity table is a finite-resolution
distance/slope diagnostic, not proof of exact criticality.

## Evidence

The new synthetic-only command is:

```sh
PYTHONPATH=.:python .venv/bin/python scripts/qualify_paired_replay.py \
  --output-dir artifacts/EXP-481/synthetic-replay-NEW
```

Use a fresh output directory; partial and failed artifacts are not overwritten.
The completed run `synthetic-replay-01` recorded 2,048 circle trajectories per
step profile in 16 total batches. All original IDs survived the joint cohort:
1,024 calibration and 1,024 held-out seeds. All four primary window/profile
maps, with all five variants and 200 whole-seed bootstrap replicates each,
resolved the known identity return as one branch and no turning regions.
The two zero-valued diagnostic projections did not create a partition.

This control deliberately uses shorter windows, one pair per seed per window,
and synthetic section geometry; it is not the production adaptive qualification.
The raw journals, pair arrays, provenance, fits and full inventory receipt are
retained locally: 168 files totaling 3,580,752 bytes, excluding the receipt.
The [public summary](../experiments/receipts/EXP-481-synthetic-replay.json)
binds source and raw hashes. It does not pretend those local journals are a
public data release; the synthetic-only script needs no private inputs.

**33 new tests pass**, including analytic two-turn controls that retain all
point-by-region hits and misses across 20 fits, missing/changed variant
rejection, incomplete journals, global-ID order, and a good diagnostic that
cannot rescue a failed primary. The full suite passes **1,439 tests**, with
one Linux-only process test skipped on macOS. CI must also pass before merge.
The reduced-bootstrap unit controls are distinct from the full-default
circle smoke. Earlier source-bound receipts remain historical; they are not
silently relabeled as qualifications of the modified analyzer.

## Next execution item

Finish the adaptive early-transient adapter and bounded CPU supervisor, then
the authentic source/input/review-bound production preflight. Verify capture
reference rows against already-retained EXP-480 raw events. Obtain/adjudicate
the compact design review and push the exact executable freeze before new
target sampling. Both nominations stay in scope; no desired word selects a fit.

Separately, the [legacy stationary-inflection incident](../experiments/EXP-481-legacy-turning-point-incident.md)
still requires a historical-impact audit before a manuscript release. This
checkpoint neither overturns nor clears previous Rössler claims.

The research-integrity playbook influenced the implementation directly:
fixed seed identities, explicit exclusions, complete comparison grids, retained
negative controls and no target-result-driven tuning. No paid compute, model
review or remote upload was used for this checkpoint.

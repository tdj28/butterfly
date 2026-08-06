# EXP-009 — Fine recurrence candidate search

Status: completed discovery run; confirmation pending
Manifest: `experiments/manifests/EXP-009-fine-candidates.json`
Claim target: discovery stage for P0-009 and CLM-001

## Purpose

Search the hub neighborhood at ten times the linear resolution of EXP-006
without paying for a full Lyapunov spectrum at every point. The `41 x 41` grid
contains 1,681 points with spacing `delta a=0.00025` and `delta c=0.01`.

## Candidate observable

Every bounded crossing sequence retains its best normalized near-recurrence
over periods 1 through 16:

`candidate_normalized_error = recurrence_error / declared_tolerance`.

This score ranks follow-up targets even when no period passes the conservative
threshold. It is not a periodic classification. Exact periodic labels and the
lowest-scoring unresolved neighborhoods will be rerun with longer transients,
full spectra, multiple initial conditions, and local refinement.

## Execution

The grid is split into 32 immutable tiles of 52 or 53 points:

```sh
.venv/bin/butterfly tiled-scan \
  --manifest experiments/manifests/EXP-009-fine-candidates.json \
  --output-root artifacts/EXP-009 \
  --tile-count 32 \
  --workers 4 \
  --resume
```

Individual tiles may be executed with `--tile-index N`. Aggregation occurs only
after all 32 verified completion markers exist. `--workers` controls bounded
local process-level tile parallelism; workers never share an output shard.

## Prospective selection rule

Before inspecting the result, retain for confirmation:

1. every point classified periodic;
2. the lowest 1% of finite normalized candidate errors;
3. the eight-neighbor boundary of every retained point; and
4. any integration failure as a diagnostic target, never as a periodic point.

## Acceptance criterion

All 1,681 point indices must appear once in the verified aggregate. The report
must include period counts, candidate-score quantiles, selected coordinates,
tile/source hashes, and elapsed CPU cost. Scientific hub reproduction remains
open until the selected targets pass the confirmation stage.

## Result

The clean run from commit `b991b91e1c840a5854fa54193f89341d33ee5787`
completed all 32 tiles and all 1,681 unique point indices:

- wall time with four worker processes: 212.1 seconds;
- summed tile time: 834.4 seconds;
- tile elapsed range: 24.63 to 26.66 seconds;
- integration failures: zero;
- strict periodic classifications: zero; and
- unresolved recurrence-only labels: 1,681.

The lack of strict periodic labels means no sampled point converged to the
declared `~1e-6` recurrence scale during this discovery horizon. It does not
mean the score was uninformative. The normalized-error distribution was:

| Quantile | Normalized error |
| --- | ---: |
| minimum | 97.02 |
| 1% | 492,271.53 |
| 5% | 1,350,964.74 |
| median | 3,613,759.84 |
| 95% | 5,308,961.13 |
| maximum | 5,869,086.44 |

The three strongest near-recurrences are sharply separated from the bulk:

| `a` | `c` | candidate period | normalized error |
| ---: | ---: | ---: | ---: |
| 0.18475 | 10.35 | 6 | 97.02 |
| 0.18450 | 10.40 | 12 | 101.64 |
| 0.17675 | 10.42 | 8 | 568.72 |

All 17 prospectively selected lowest-1% points are retained in
[`receipts/EXP-009.json`](receipts/EXP-009.json); none is promoted to a
periodic finding here.

Aggregate result SHA-256:
`80296d185fddf2038fd3a93af180030ab8ec770aae45305ff30124051abd59b5`.
Independent `shasum -a 256` verification matched it.

## Next confirmation

Generate the frozen lowest-1%-plus-neighbors target set bound to the aggregate
hash. Rerun those coordinates with a longer transient, longer crossing record,
full Lyapunov spectrum, and multiple initial conditions. The three pronounced
low-score points above receive no special evidentiary status beyond priority
within that already-frozen set.

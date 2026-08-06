# EXP-009 — Fine recurrence candidate search

Status: prospective tiled discovery run
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

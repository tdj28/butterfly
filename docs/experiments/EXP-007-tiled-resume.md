# EXP-007 — Immutable tile and resume qualification

Status: passed local infrastructure qualification
Manifest: `experiments/manifests/EXP-007-tiled-resume.json`
Claim target: P0-007, P1-004, and infrastructure prerequisite for P0-009

## Purpose

Qualify deterministic grid partitioning, unique immutable tile outputs,
hash-verified resume, corruption rejection, completion markers written last,
and exact aggregation before any fine or interruptible scan.

This experiment does not qualify scientific labels. It intentionally uses the
recurrence-only path on a small `4 x 4` grid split into four tiles.

## Tile contract

Each tile ID binds the normalized plan hash, exact source commit, tile index,
tile count, and ordered point indices. Each tile writes its result and receipt
atomically, then writes `complete.json` last. Resume skips only a completed tile
whose ID and result/receipt hashes verify.

Aggregation verifies all tiles, rejects gaps or overlaps, sorts the full grid by
its original point index, and writes its own result, receipt, and final completion
marker.

## Command

```sh
.venv/bin/butterfly tiled-scan \
  --manifest experiments/manifests/EXP-007-tiled-resume.json \
  --output-root artifacts/EXP-007 \
  --tile-count 4 \
  --resume
```

## Acceptance criterion

- four distinct completed tile IDs cover point indices 0 through 15 exactly;
- a second `--resume` invocation skips and verifies every completed tile;
- aggregate row count is 16 and binds every tile result hash;
- corruption of a completed test tile is rejected;
- a simulated interrupted temporary write resumes safely; and
- the qualification run is bound to a clean source commit.

## Result

The clean run from commit `c154f07c42676dfb259d23d1a117560aa5edf8c7`
passed every local acceptance criterion:

- four distinct tile IDs each completed four unique points;
- their ordered point indices formed exactly `0..15` with no gaps or overlap;
- all tile source receipts reported `dirty=false`;
- the aggregate contained all 16 rows and bound all four tile result hashes;
- an immediate resume verified and skipped the four complete tiles in 0.39
  seconds, versus 4.7 seconds for the initial dirty-path qualification;
- the test suite rejected a deliberately corrupted completed result; and
- the test suite recovered safely from a simulated interrupted temporary file.

The aggregate result SHA-256 is
`a5e81c2c971fc4edfeb8890f2851a7cf5137d44974d4f6673599d6b1e8375b42`;
an independent `shasum -a 256` invocation matched it. The checked-in summary is
[`receipts/EXP-007.json`](receipts/EXP-007.json).

All 16 recurrence-only labels were `unresolved`, as expected at this short
horizon. They are infrastructure records and carry no scientific interpretation.

## Remaining interruption gate

The local simulated-interruption and corruption gates pass. P1-004 remains open
until an actual worker process is killed during a nontrivial tile and restarted
against its preserved output directory, first locally and then on the selected
remote execution stack.

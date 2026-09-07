# EXP-481: the complete numerical path passes a sealed circle control

The worker now runs qualification, collection, saved-event replay and both-case
analysis through the actual isolated command. On the analytic circle, all 24
integrator comparisons pass and both cases recover the expected one-branch
identity return map. This is a working numerical pipeline, not a new Rössler
result or verification of Jones's symbolic chains.

The previous input-audit checkpoint is merged on `main` at
`319b266903d5b56bbca9e519dec8d593e07decd3`. Its input reconstruction, bootstrap,
canonical environment and process supervision are reused.

## What the runner now does

`paired_phases.py` validates every trial configuration before any field call,
including both cases, both RK4 profiles, DOP853 and Radau, the original seed
coordinates, all six/eight reference rows, observation windows, map variants,
analysis gates and the three declared resource budgets. It rejects retries,
resume and inconsistent event/capture time tolerances. The existing comparator
uses one time tolerance, so a differently declared capture tolerance is rejected
instead of ignored. The proposal already declares both as `1e-4`.

Qualification writes the full declared trial grid before comparing profiles.
Comparisons reload complete raw events from the durable journals, including
rejected crossings; they do not compare only a final in-memory summary. The RK4
raw reader is shared with sampling, preserving the existing pair-selection
arithmetic. Collection requires an externally bound, passed qualification phase.
Analysis requires the complete collection phase, including its full file
inventory and ordered trial set. A missing, changed or extra file blocks it.

Every phase has exclusive start/completion or failure records with UTC times.
Each completed trial has a separate receipt binding its journal endpoints.
Technical failure stops the campaign and preserves the prefix without retry.
Numerically completed but unresolved analysis remains a reported result, not a
technical success that can be relabeled as scientific support.

Analysis saves all original IDs, failure/capture/ambiguity masks, selected raw
event indices, pair states/times, batch provenance and both-case results. All six
historical reference rows enter the critical-region assessment; no phase or
better-looking case is selected. The Rössler factory derives both section
geometries and the batched field from the audited parameters. Its validation
test evaluates a synthetic fixture's field but does not integrate a target.

## Observed qualification and preserved failures

Final control: `artifacts/EXP-481/sealed-phases-03`.

- Three isolated supervised numerical workers complete; a fourth worker rejects
  a wrong preceding-phase digest before creating a numerical phase directory.
  Owned process-group cleanup is verified for all four.
- Both cases have 2,048 original circle seeds: 1,024 calibration and 1,024
  validation. All are retained in both profiles, with no observed capture.
- Sixteen one-seed qualification trials give 24 pairwise comparisons. The
  maximum scaled event-state difference is `1.4710982251623766e-7`; the maximum
  event-time difference is `1.5819430929653322e-6`, both below `1e-4`.
- Sixteen collection batches feed both-case analysis. Both primary maps resolve
  one branch, correctly yielding no turning-region claim. All six reference
  rows are retained. These deliberately distant synthetic references are not
  Rössler cycle evidence, and this control does not test a positive capture.
- The final control preserves 510 files / 13,400,015 bytes excluding its receipt.
  The [public hash summary](../experiments/receipts/EXP-481-sealed-phases.json)
  binds those files' inventory and the exact source/runtime. Maximum sampled
  worker RSS was 113,754,112 bytes. These are observations, not target estimates.

Run 01 preserves a completed qualification worker followed by a harness error:
the harness requested `cleanup_verified` instead of the supervisor's actual
`owned_group_cleanup_verified` field. Run 02 completed all numerical phases but
failed the harness's expected-positive analysis assertion. Its small synthetic
fixture used 256 seeds and 6/8/10 bins; for example, the first 8-bin map had
14.0625% unsupported held-out rows, above the unchanged 5% gate, despite an
identity-fit error near machine precision. The analyzer correctly refused to
declare support. No failed directory was overwritten or erased.

Run 03 uses a denser positive fixture with 2,048 seeds and the proposal's
30/40/50-bin variants, minimum support counts and unchanged 5% support gate.
This is an explicitly revised synthetic control after inspecting control
outcomes; it is not confirmatory Rössler evidence. It uses shorter horizons,
coarser step sizes, one pair stratum, eight bootstrap samples and synthetic
60-second phase bounds. It cannot qualify the target numerical settings.

All nine startup controls also pass with the expanded 24-file runtime, preserved
as `sealed-startup-07`. The full suite passes **1,602 tests**, with one older
Linux-only process-identity skip on macOS. Thirty new tests cover the complete
pipeline, pre-field validation, corrupted predecessor evidence, preservation
of a failed first trial, duplicate-write refusal and the actual isolated CLI.

To reproduce the synthetic control without private research inputs:

```sh
PYTHONPATH=.:python .venv/bin/python -B scripts/qualify_paired_phases.py \
  --output-dir artifacts/EXP-481/sealed-phases-NEW
```

## Next execution item

Implement the final source/input/review-bound controller and target-only worker
authorization gate around these completed phases. The controller must verify
the actual pushed source and adjudicated review, bind the runtime/input package,
perform the genuine startup/input handshake, enforce the plan's 1,800/14,400/7,200
second phase limits and arm a corresponding parent-loss/deadline guard before
scientific imports. A receipt's copied source string is not proof of authority.
The current `execute` command still refuses target execution.

Then qualify that final path, obtain one compact review, adjudicate it and push
the executable freeze before new target trajectories. This is the next concrete
implementation item, not a request for another routine user approval. No new
GPU rental, paid review, remote upload or Rössler trajectory occurred here.

The experiment-integrity instructions shaped the complete trial accounting,
sealed-consumer controls and preservation of the failed controls. Jones's
alphabet/arrows, exact criticality and homoclinic existence remain unverified by
this checkpoint. The separate legacy stationary-inflection impact audit remains
open; new synthetic successes do not clear old branch-count claims.

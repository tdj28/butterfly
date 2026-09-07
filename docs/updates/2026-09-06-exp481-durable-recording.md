# EXP-481: interruption-safe recording is ready; the scientific design is next

The paired-section collector now has an opt-in, write-once journal. Both sections
still observe the same trajectories, including trajectories labeled captured.
This is infrastructure progress, **not independent verification of Jones's
symbolic chains**. No new nominated Rössler trajectory, partition, critical
letter, word or continuation arrow was generated in this checkpoint.

## What changed and what was verified

`python/butterfly/paired_journal.py` saves the fixed global seed table and ordered
raw event deltas, plus state/failure/capture arrays and physical-time checkpoints.
Each raw NPZ and its hash-chained JSON record are exclusively created and fsynced;
completion requires a separate terminal receipt agreeing with an audited, whole
prefix. Existing outputs cannot be overwritten or resumed. Interrupted or failed
writes are not automatically retried. Integration and journal failures report
the actual attempted step and phase separately.

The auditor checks raw hashes and sizes, bounded non-pickle arrays, fixed global
seed mapping, event step/time ownership, monotone state flags, immutable first
capture/failure records, checkpoint schedule/masks and the terminal chain.
Missing terminal receipts remain incomplete; extra uncommitted files cannot be
silently promoted into a completed run. Corrupt or partially written commit JSON
causes the audit to reject the artifact rather than invent a successful recovery.
Earlier files are retained for diagnosis. There is no automatic resume mechanism.

**43 focused tests pass:** 24 collector, 13 journal and 6 draft-preflight controls.
These include an actual synthetic child process killed with SIGKILL after its
first saved block: the prior block remains readable, and the run is incomplete.
An injected disk-full error preserves the earlier committed prefix and stops
without a retry. Deliberately rehashed seed/checkpoint corruption is rejected by
semantic checks. The full local suite passes **1,381 tests**, with one unrelated
Linux-only process-identity check skipped on macOS. These tests do not simulate
physical disk/controller failure and do not prove hardware power-loss durability.

The analytic-circle smoke run uses 128 seeds, a physical horizon of 20.5, steps
0.02 and 0.01, and a journal interval of 100 steps. Both profiles pass: 11 and 21
committed blocks respectively, each with 1,280 raw events per section and no
orphan files. Final raw arrays have the same hashes as the earlier in-memory
circle benchmark, although the executable source has changed. This is direct
evidence that journaling preserves this synthetic result, not Rössler performance
or a target partition result.

- [Exact synthetic configuration and source hashes](../experiments/receipts/EXP-481-synthetic-journal-configuration.json)
- [Synthetic result and journal audit summaries](../experiments/receipts/EXP-481-synthetic-journal.json)
- Local complete artifacts: `artifacts/EXP-481/synthetic-journal-02/`.

The earlier `synthetic-journal-01/` also passed and is retained. The second run
binds the final source after correcting the journal-failure diagnostic step;
neither run contains research targets. The optional benchmark command is:

```sh
PYTHONPATH=.:python .venv/bin/python scripts/benchmark_paired_sections.py \
  --output-dir artifacts/EXP-481/NEW-UNUSED-SYNTHETIC-DIRECTORY \
  --seed-count 128 --journal-interval-steps 100
```

## Remaining scientific work

The draft manifest and `scripts/check_paired_sampling_preflight.py` verify the
unchanged EXP-204 candidate bytes, complete EXP-479 nomination set and EXP-480
two-case qualification receipt. Their outcome-free input check passes.
`--mode execute` deliberately refuses before reading inputs or starting a solver.
Changing a Boolean in the draft cannot enable target execution. Source-bound
preflight additionally requires a clean, exact pushed source commit.

The journal is a numerical primitive: its caller-supplied `binding` is recorded
metadata, not authenticated provenance or execution permission. Before using it
for EXP-481, finish and review the seed distribution, capture references,
common-population/censoring rule, integration and tolerance profiles, physical
windows, memory/storage/process limits, trajectory weighting, seed-level
holdout/bootstrap, scalar-map adequacy/support and critical-membership rules.
Then bind the complete runner to the adjudicated review and pushed source.
The [implementation worklist](../experiments/EXP-481-common-population-partition-design.md)
lists these next actions; the completed journal should not be rebuilt.

The Git workflow playbook is applied here: an isolated behavior-change branch,
explicit staging and secret checks, opt-in behavior, tests and this verification
record accompany the change. No manuscript claim or published negative result
is changed. No paid compute or model call was made for this checkpoint. The
unresolved earlier Runpod create transaction remains guarded: a read-only check
found no exact task-name match and confirmed the existing watchdog alive. That
is not authoritative teardown evidence and does not permit a duplicate create.

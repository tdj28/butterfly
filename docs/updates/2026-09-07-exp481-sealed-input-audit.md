# EXP-481: the isolated worker verifies the actual reference inputs

The guarded worker now audits the preserved cycle references through its real
isolated command, not through the development checkout. The result exactly
matches the earlier reference audit for both candidates: six historical and
eight Barrio events, with identical ordered raw indices, states and times.
This verifies the new execution path, not new trajectories or Jones's symbols.

PR #42 is merged at `8ea615aa7538a9c477f4c88a6f1971236c086953`.
Its startup/environment/import checks are reused, not replaced.

## Input handling without the old GPU imports

The unchanged event-window reconstruction and raw-membership arithmetic moved
from `scripts/verify_paired_capture_inputs.py` into `paired_inputs.py`. The old
command remains a thin wrapper. The isolated runtime no longer imports the old
GPU scout just to obtain file-reading helpers; its observed import list contains
no `scripts.*`, Torch or Triton modules.

The new read-only IO helper bounds each declared file at 16 MiB, checks hashes
and declared sizes, and rejects noncanonical file paths, symlinks and nonregular
files. The input audit also rejects duplicate candidate identities and checks
the qualification summary's source, complete candidate set and raw-receipt hash.
These are stricter metadata checks, not changes to the recovered event values.

A local input package contains exactly nine files: the current proposal,
six declared JSON inputs and the two receipt-bound raw event archives. It is
6,285,537 bytes for the final control. Only those declared files are copied;
no credentials, broad source archive or unrelated research artifacts are included.
The independent package digest is supplied explicitly to the worker. Before and
after the audit it rechecks the complete package, runtime files, import origins
and actual environment. Writable audit evidence must be separate from inputs.

The sealed source list now has 22 files. Numerical modules are unchanged.
The input-only package contract and startup receipt both explicitly deny target
execution authority. `--mode execute` still refuses: an operator cannot convert
a successful old-input audit into permission to run the new experiment.

## Controls and preserved evidence

All six actual input-consumer controls pass: correct input; wrong digest;
changed, extra or missing input; and missing required arguments. Failed controls
leave no successful input-audit receipt and are checked for the expected failure
reason. Cleanup is verified for every worker. The original nine startup controls
also pass with the expanded 22-file runtime.

The public [source/hash summary](../experiments/receipts/EXP-481-sealed-input-audit.json)
binds `artifacts/EXP-481/sealed-input-audit-03` and `sealed-startup-06`.
Input-audit run 01 was a build-only probe; run 02 passed before the final metadata
checks and remains preserved. Run 03 includes those final checks. No old raw file
or earlier receipt was overwritten. The final audit's nested result equals the
hash-bound `capture-input-audit-02/receipt.json` exactly as a JSON value.

The full local suite passes **1,572 tests**, with one older Linux-only skip on
macOS and host access for real process controls. There are **25 new tests** for
input paths, byte limits, package identity, coherently rehashed bad metadata and
an actual isolated worker reading a synthetic package. CI does not need the
private historical inputs for these tests.

To repeat the preserved-input control when its declared local inputs are present:

```sh
PYTHONPATH=.:python .venv/bin/python -B scripts/qualify_paired_input_dispatch.py \
  --output-dir artifacts/EXP-481/sealed-input-audit-NEW
```

Hashes alone are not a public raw-data release. The control uses CPU processes;
it does not contact a compute provider or generate a Rössler trajectory.

## Next step

Wire the fixed qualification, collection, replay and analysis phases into the
source/input/review-bound production controller. Use this hash-checked input
path, the existing 512-batch/128-qualification trial grid, and both-case analysis.
The input-audit control's 60-second worker guard is not the future phase budget.
The completed production path still needs exact-source qualification, compact
review/adjudication and a pushed executable freeze before new target outcomes.

The integrity playbook influenced this checkpoint through exact input-role
accounting and validation inside the actual isolated consumer. No paid review,
GPU rental or remote upload occurred. A read-only safety check found no exact
task-name match for the unresolved Runpod create; the identity-checked watchdog
was alive and remains in place.

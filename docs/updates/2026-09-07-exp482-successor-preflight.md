# EXP-482: the real successor setup passes

The separately identified finer-step successor passed its authentic production
source preflight at `ba85d90ba23ec44d4c6f66639d337812374719cf`:

- **426 source-bound tests passed, zero skips**, including actual controller
  authorization controls for both experiment identities;
- both preserved raw-reference audits passed;
- all 128 qualification trials and 64 collection configurations validated;
- test and isolated-worker process cleanup was verified;
- no target trajectory ran and no target attempt was consumed.

The [receipt](../experiments/receipts/EXP-482-source-preflight.json) binds the
372-file source/test/design closure, runtime, inputs and actual worker result.
The [protocol](../experiments/EXP-482-successor-protocol.md) states every change:
finer RK4 steps, larger fixed batches, matching step/event caps, one-second
resource polling and a fresh deterministic sample. Every scientific accuracy,
support, prediction-error, capture and reporting threshold remains unchanged.

The original run cannot be silently retried: selecting EXP-482 requires its own
fixed plan, review identity and attempt marker. Cross-experiment reviews and
arbitrary experiment names are rejected. The full source closure now includes
both numeric designs because regression tests compare their exact differences.

The prior workload checkpoint is on `main` through PR51, merged at
`ea0ae3d4dc465a7e6386eb0a00cb12798db1ae6b` **after all four CI jobs passed**.
Its final local suite passed 1,728 tests with one existing Linux-only skip;
manuscript/reference, generated-table and public-file checks also passed.

Next is one compact prospective review of this materially revised design,
including the complete previous review and structured adjudication, numerical
failure and original failed resource estimate. The review packet is assembled;
no new paid review has occurred at this checkpoint. The prospective review is
required by the experiment-integrity playbook before any new target outcome,
not a request for routine user permission.

Jones' symbolic chain remains unverified. A passing setup establishes that the
next numerical test is ready for design review, not that its scientific result
will be positive. The prax backup remains local after the upload guard's renewed
rejection; that storage restriction has not stopped local progress.

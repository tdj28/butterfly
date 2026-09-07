# EXP-481: full-design setup before new trajectories

The production setup command now connects the actual live source/review checker,
source-bound tests, sealed runtime, preserved input package and isolated worker.
It validates every configuration in the 128-trial numerical qualification and
512-batch collection without calling a field, integrating a trajectory or
fitting a return map. This is an engineering checkpoint, not evidence for or
against Jones's symbolic dynamics.

The numeric-only design is now in
[`EXP-481-paired-design.json`](../../experiments/manifests/EXP-481-paired-design.json).
A regression test compares every scientific field with the preserved proposal.
Only administrative status, review placeholders and pending-work prose were
removed; the schema identifies a design, not an approval. Sampling, thresholds,
capture rules, resource limits and claim restrictions are unchanged. The
reviewed release remains separate and has not been fabricated.

## What the command does

`scripts/run_paired_campaign.py` defaults to source-only preflight. Its reviewed
mode calls the same actual release gate, requiring committed real review
evidence. Neither mode grants target execution or consumes a target-run slot.
Both preserve a fresh attempt directory, including failures.

Before loading numerical code, the controller checks its own committed bytes,
the live pushed ref, the independent source/test closure and the committed
design. It packages the exact nine preserved input files and constructs the
design from the raw reference audit. It runs the paired and direct numerical
tests with an explicit environment, disabled external pytest plugin autoload,
bound test-runner package inventories, resource supervision and a parent-loss
guard installed before pytest imports.

The actual worker then uses `-I -S -B -X utf8`, its canonical environment and
the sealed import checks. It audits the input package itself and validates the
complete design. The controller independently reconstructs the same design,
compares its identity, trial counts and all three declared phase limits, then
rechecks source, input and runtime bytes. The preflight guard is 120 seconds;
its receipt does not pretend that this startup budget enforces the later
1,800/14,400/7,200-second numerical phases.

While wiring real test execution, inspection found that the earlier source
checker covered the small worker and selected tests but omitted some older
helpers imported by the checkout tests. The source inventory now includes all
tracked Python files under `python/butterfly` and `scripts`, plus the old draft
and proposal read by those tests. This broader test-support closure does not
enter the 24-file numerical worker. No earlier receipt is relabeled as having
covered these files.

## Verification ledger

- Full local suite: **1,676 passed, one older Linux-only skip**, 57.34 seconds.
- New tests: **18 passed**, including real isolated workers on a synthetic
  reference package, full-grid setup, wrong bindings, missing source, invalid
  final adaptive configuration and independently reconstructed receipt checks.
- An initial test assertion expected the word `positive`, while the correctly
  refused invalid configuration reports `invalid bounded adaptive design`.
  The assertion was corrected; neither validator nor numerical rule changed.
- The first actual pushed-source command (`production-preflight-01`, source
  `e5fc0084baf0f7a4d370a7d091e6bbd916fb9146`) correctly stopped before tests or
  target outcomes: the host controller tried to use the worker-only import
  closure despite having normal virtualenv startup and a controller path outside
  that closure. Its failure and full checked source/runtime inventory are
  preserved. The repair keeps the host explicitly trusted and uses its verified
  minimal package, while leaving the child's isolated import policy unchanged.
  Two regression tests distinguish those paths. This is a pre-outcome setup
  incident, not a relaxed numerical or child-startup gate.
- The repaired actual pushed-source command on preserved research inputs is
  pending a new source commit. No target launch or paid review has occurred.

Tests establish trusted-host reproducibility checks, not protection against a
hostile operator or hermetic OS/native-library attestation. Hashes identify the
files actually checked; they do not mean a reviewer read omitted source.

## Next

Finish the one-use, actual-parent worker authorization and complete predecessor
receipt checks around the existing fixed numerical phases. Exercise that final
authorization boundary before the one compact paid review, adjudicate the real
response, push the executable freeze, and then generate the fixed research
outcomes. The experiment-integrity playbook requires this prospective ordering;
the current preflight is not a shortcut around it. Jones's alphabet, chain
arrows and homoclinic assertion remain unverified.

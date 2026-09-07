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

- Full final local suite: **1,679 passed, one older Linux-only skip**, 60.31 seconds.
- New tests: **21 passed**, including real isolated workers on a synthetic
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
- The second attempt (`production-preflight-02`, source
  `178ec9352896928e80d0d78c4c9e8d939b6624a5`) exposed another real startup bug:
  pytest's descriptor capture replaces stdin with `/dev/null`. The guard watched
  numeric FD0 and interpreted that replacement as parent loss, killing the test
  stage before test output. Cleanup was verified; this attempt remains failed.
  The guard now duplicates the original supervisor pipe before starting its
  thread and marks the duplicate non-inheritable. A real-process regression
  checks stdin replacement while that original pipe stays live. The same
  parent-loss/deadline policy remains in force; this is not an EOF exemption.
- The third actual command passed against pushed source
  `59c2e49940ee3b3a1cbe97d71e400ecc2ccfb8b8`: **361 source/test-support files**
  checked, **350 source-bound tests passed with no skips**, both actual reference
  audits reproduced, and all **128 qualification / 512 collection** configurations
  validated in the isolated child. The preserved receipt at
  `artifacts/EXP-481/production-preflight-03/receipt.json` is 10,689 bytes, SHA-256
  `65837bc76271d16b9f2212283788cbebbe12aa97d4b70778d28546cea2d9b0cc`.
  Its 52 evidence files total 7,654,684 bytes, excluding the aggregate receipt.
  The [public evidence summary](../experiments/receipts/EXP-481-production-preflight.json)
  includes the complete source inventory and the runtime, input, test-runner and
  actual child witness hashes. No target slot, trajectory or paid review was used.

The verified command was:

```sh
.venv/bin/python -B scripts/run_paired_campaign.py \
  --source-commit 59c2e49940ee3b3a1cbe97d71e400ecc2ccfb8b8 \
  --remote-ref refs/heads/codex/exp481-production-preflight \
  --output-dir artifacts/EXP-481/production-preflight-03
```

The command requires current HEAD and the live ref to equal the requested
commit. The later evidence-only commit and eventual squash merge do not change
the preserved observation into a test of those later Git identities. A new
execution freeze must run its own preflight; do not overwrite this attempt.

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

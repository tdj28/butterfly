# EXP-507: isolate the failed fold constraint

## Result: fold restored, joint contact still absent

**All 158 integrations pass the complete raw audit. The single fixed-c
correction restores fold proximity under the unchanged 1e-4 criterion.**
Both original and adjacent cycle-index checks pass; all four fold and eight
boundary representations qualify, with primitive six historical/eight Barrio
returns retained. EXP-504's rejected point remains rejected in its own record.

| Quantity | EXP-504 rejected point | EXP-507 corrected point |
| --- | --- | --- |
| a | 0.21559483661175796 | 0.21559083980240445 |
| c (unchanged) | 7.172000000000001 | 7.172000000000001 |
| Worst scaled full-state fold distance | 0.0001011886422 | 0.000003854359465 |
| Worst scaled limiting-boundary distance | 0.01192572254 | 0.01194264957 |
| Required distance for each contact | 0.0001 | 0.0001 |

The fold distance is now only 0.03854 times its limit. The absolute mean signed
fold residual falls **96.19%**, passing the separately declared 50% secondary
endpoint. These are different statistics: the signed scalar is not substituted
for the full-state primary decision. The boundary gap increases slightly
(about 0.142% in the mean residual) and remains about **119.43 times tolerance**.
The joint-contact endpoint still fails. This is useful local controller evidence,
not verification or refutation of Jones's flow-level symbolic chains.

The [complete public comparison receipt](../experiments/receipts/EXP-507-fixed-c-fold-restoration-result.json)
is 1,204,791 bytes, SHA-256
`b6d550882b761fb499a9b6e3f4d415aa05c0dc1d1f98f424bcffc2dacaba386d`.
It retains the full point, all 256 predicted/observed changes, all 26 parent
candidates, the separate endpoints and source/raw bindings. Its separate public
comparator passes; twelve controls include rehashed semantic substitutions for
source, plan, claim, quota, decision, parameters, missing boundary, cycle counts
and integration counts. These checks replay compact comparisons, not the raw
meshes or total on-disk byte count. Full raw replay was performed locally first.

## Execution and resource accounting

The frozen source is `dd1d18eb96f8fabdaff4bb44e9fc9f6a68b6ca49`, live-verified
before target execution and preserved at `codex/exp507-local-execution`.
All 80 source files still match the runtime inventory. The local run is
artifacts/EXP-507/target-dd1d18e; its consumed marker SHA-256 is
`2839f3f5cef2f37ea9750612225f2aea65dd6176152cfd3e136ddb989b04a204`.
Raw summary SHA-256:
`e339c6aca70ab1d2577f69614aff91a6f6d3b54c35ae9f6f42ce61de51272ebb`.
Point SHA-256:
`0e3a8134b4d5cd664bcac1a82eb57036d0d1a2848ea1d52d35356d505de29f3f`.

Execution took 485.06 seconds. There are 243 files totaling **1,084,682,426
bytes including the 198,525-byte final summary**, below the frozen 3 GiB limit.
Integration accounting is 134 products under the inherited convention plus
24 retained guard IVPs, totaling 158. The full audit re-counted all files
including the summary and reports `protocol_compliant=true`. That is a separate
execution of shared accounting code, not an independent audit implementation.
The new bounded writers prevented neither required retention nor normal
completion. EXP-506's distinct resource deviation remains unchanged.

No new paid review, cloud worker, remote computation, raw upload or deletion
occurred. The code, compact result and documentation are public Git products;
the 1.08 GB raw run remains local and is not claimed as a remote backup.

Public comparison command (no raw data or new integrations):

```sh
PYTHONPATH=.:python .venv/bin/python -B -m scripts.verify_exp507_public_restoration \
  --result docs/experiments/receipts/EXP-507-fixed-c-fold-restoration-result.json \
  --expected-sha256 b6d550882b761fb499a9b6e3f4d415aa05c0dc1d1f98f424bcffc2dacaba386d
```

Final local release checks passed **2,500 tests**, with one Linux-only skip,
in 180.38 seconds (artifacts/EXP-507/release-suite-01.xml). The twelve public
replay/tampering controls also passed separately in 7.11 seconds. Citation,
figure-availability and symbolic-control-table checks pass. The staged public
scan passed 2,844 tracked files. All final-head push and PR Python 3.12/3.13
checks must pass before normal exact-head squash merge of
[PR #74](https://github.com/tdj28/butterfly/pull/74).

## Next research action

Freeze a bounded predictor/corrector continuation from this qualified point:
predict a lower-c point, explicitly correct the fold at fixed c, and accept
only after all full-state, primitive-cycle and original/adjacent identity checks
pass. Retain rejected predictors and all corrective trials. Measure the
boundary movement separately; do not let a combined norm conceal a failed fold
constraint again. Plan storage for **both** predictor and corrector before
targets, retaining the complete-output writer and all old failures.
No new continuation target is part of EXP-507. Operational C/D identification,
the generating-partition question and a source-matched p-to-p+1 connection
remain open, as does the broader legacy impact audit.

## Pre-target checkpoint

The new [fixed-c corrective pilot](../experiments/EXP-507-fixed-c-fold-restoration.md)
is implemented. It uses one bounded a correction from the original fine
response, then recomputes the complete fold/boundary/primitive-cycle matrix.
The original EXP-504 rejection remains a rejection. Neither its diagnostic
boundary improvement nor this new proposal verifies a Jones symbolic arrow.

Twenty focused controls passed in 2.07 seconds. They check the known linear
correction, clipping, fixed c, missing/nonfinite representations, bad slopes,
full-state tolerance versus a favorable scalar residual, adjacent identity,
unchanged inherited numerical settings, exact JSON/NPZ/Decimal stream bytes,
pre-write quotas, reserved failure space, fresh paths and free-space refusal.
The authentic isolated copied-source startup passed with no target integrations.
All 34 original analytic-control files replayed successfully, also without
new integrations; the receipt is retained under
artifacts/EXP-507/preflight-control-replay-01.json.

The full local suite passed **2,488 tests**, with one Linux-only skip, in
174.96 seconds (artifacts/EXP-507/pretarget-suite-01.xml). Citation/figure
availability and the receipt-generated symbolic control table checks pass.
The staged public scan passed 2,841 tracked files. The 80-path machine plan has
SHA-256 `ac1ea02269f66d1ac005be552a6c8dbb1f7b0536ef94c02d1bbdce812b990788`.
Its sole proposal is a=0.21559083980240445, b=.2, c=7.172000000000001.
These checks preceded the source freeze, target execution and raw audit
reported above. No numerical source was changed after the freeze.

## Local design audit

This corrective direction is explicitly outcome-informed. The original fine
derivative is not relabeled as a current local measurement. Holding c fixed
isolates the scalar correction; it does not guarantee that the boundary stays
near a cycle or that a continuation path exists. The primary decision uses
all-variant full-state distances and both original/adjacent cycle identities,
not the predicted scalar improvement. A separate 50% signed-residual reduction
endpoint cannot override a failed primary decision.

The new output adapters preserve the old numerical producers byte-for-byte and
are scoped only to the new execution. Uncompressed JSON is admitted with the
complete canonical size; compressed streams admit every chunk and trailer.
NPZ buffers are per trajectory, not a whole-run copy. A final summary links to
the saved point rather than duplicating it. Both execution and audit include
summary bytes in the complete 3 GiB cap, with 1 MiB reserved for failure.
The prior EXP-506 overrun is not retroactively waived or repaired in place.

This same-agent design check and shared-code raw audit are not independent-team
replication. No paid model review, new cloud worker or raw upload is requested.
The next step after this one-point result will depend on its actual complete
qualification, under a separately frozen continuation design.

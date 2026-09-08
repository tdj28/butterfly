# EXP-482 cumulative evidence context

Summaries below were validated locally; the reviewer has not audited raw data.
No EXP-482 target trajectories exist. The separate prior-review context and the
structured disposition below reproduce the earlier documents in full (JSON
whitespace compacted); their authorization belonged only to EXP-481.

## N01: observed numerical failure motivating a new study

EXP-481 qualification completed all 128 trials/192 comparisons: 92 passed,
100 failed the fixed scaled event-state bound 1e-4; downstream collection and
analysis never ran. Both nominated cases had 50 failed comparisons. At .01/.005,
maximum RK4 vs DOP853 errors were .005996315/.000389655. DOP853 vs Radau passed
32/32, max 3.199006e-8. Counts, acceptance/capture membership and timing agreed.
Median sectionwise coarse/fine state-error ratio was 15.634, consistent with
fourth-order convergence, not a bound. Exact raw replay reproduced every row.
Preserved phase terminal SHA 51e4cf10dc4c3c2a4706a321fec6314251e9ca59ff2e234c275ed32452ecf2d9.
The consumed EXP-481 attempt is not reopened. Finer Rössler accuracy is unobserved.

## N02: full workload and disclosed resource redesign

Prospectively fixed synthetic workloads generated no Rössler trajectories.
The full t=300 circle uses batch512, actual recorder/replay, six/eight distant
reference rows, and discarded Rössler RHS arithmetic at every circle field call.
Both .0025/.00125 controls passed exact counts (146 raw/73 accepted per seed per
section), no failure/ambiguity/capture, analytic final-state/time error <1e-5.
Measured collection28.643/57.127s; replay .965/1.809s. Actual both-case8192-seed,
200-bootstrap analysis63.423s recovered3branches and the complete six-row near/far
matrix; matched two-sheet primary rejected. No shortened bootstrap extrapolation.
The original .25s-polling conservative gate FAILED: doubled full-tree scan overhead
projected collection50609s >14400. Preserve this failure; worker exit2, cleanup verified.
One-second polling is a post-observation design calculation, not a measured pass.
Same measured-data formula, unchanged headroom and caps: qualification217.093s,
collection7063.630s, analysis/replay304.343s, disk1676665584bytes, RSS644284416bytes.
Collection base=2*32*(28.643151792+57.126544208); projected full scan .111441951s
from slowest of3 local881-file scans scaled to23232files. Charge twice that full
scan at EVERY poll: base/(1-2*scan/poll). Not a hard runtime/retention guarantee;
unknown event frequency/geometry, growing inventories and OS load remain risks.
Less frequent RSS/disk sampling increases possible overshoot latency, while
integration/journals, pre-import deadline/parent guard and write caps are unchanged.
Original workload receipt SHA b8ae5599f85409ee6cd07ae9a3e20fa2083c0a1adbe1fd763dfc873434d78e3d.

## Source-qualified implementation

At ba85d90ba23ec44d4c6f66639d337812374719cf the authentic production source
preflight passed426bound tests/no skips, both raw-reference audits, and all
128qualification/64collection configurations. Includes actual ordinary-controller
three-phase analytic positive/negative grants, both experiment identities,
real Git/provider-packet tampering tests, cubic/two-sheet/inflection/failed-bootstrap
controls. The372-file closure includes both numeric designs and all paired source/tests.
Preflight receipt SHA968f90180975357fea511f382a7bf01cf533dd0d7840f3caf0cadab0e0aad74c.
No target slot consumed. A new reviewed release and fresh reviewed setup are still
required; saved preflight JSON does not authorize a worker. Selecting EXP-482
cannot reuse EXP-481 review or slot; arbitrary experiment IDs are rejected.

Later local historical audit: EXP-176/177 saved summaries lack crossing arrays,
splines and bootstrap root geometry. A nominal-root diagnostic does not close
that audit. Historical alphabet claims remain conditional; EXP-482 neither uses
those fitted partitions as its estimator nor treats nominations as independent.

## Preserved complete structured EXP-481 adjudication

```json
{"approved_for_execution":true,"changes":[{"after":{"bytes":11909,"sha256":"25534382c79c1b612a4f0e088fa21124eead187217010f6c9eb9201fe6ca1756"},"before":{"bytes":11306,"sha256":"44d8d624d02ff40ee9c1a9bc8ce06d202335994863e24981d64b05fde8df2ae8"},"findings":["I01"],"path":"python/butterfly/paired_campaign.py"},{"after":{"bytes":14311,"sha256":"6b9f84a9cd4b6c5b1df074f41dab2953d470e7f70242f91495e0aebfc70b361f"},"before":{"bytes":6356,"sha256":"68cb44b072a6a131c953b51f19a59c17806ab8e6dcdb3a276003ec56bcfec672"},"findings":["B01","B02"],"path":"scripts/qualify_paired_phases.py"},{"after":{"bytes":9116,"sha256":"84cefc0adbc74a365b08ce43b490b505720875e6063e827bdd786b8479574808"},"before":{"bytes":7866,"sha256":"3c716d445c038a1e7adcea85afdcb0c954d52472cc3db8cf3da9fd79dbb956ec"},"findings":["B01","B02","I01"],"path":"tests/test_paired_campaign.py"},{"after":{"bytes":4923,"sha256":"c5f0efe86cdc52d3a6d440213aaaf70c081b135a691c66874c79a4ecd6320b7f"},"before":{"bytes":4066,"sha256":"ea8f3e99a094187b952d6dcb38e13cad3425930ddf8eaf6ef6ebe4d2b2a0db5b"},"findings":["B02"],"path":"tests/test_seed_return_map.py"}],"code_freeze_commit":"68585e2bf853fcd2778b6efdf4b2e652bb6749db","experiment_id":"EXP-481","explanation":{"bytes":10585,"path":"docs/reviews/EXP-481-adjudication.md","sha256":"341d594526d3f60bdf653207196383b20e64d1de499b03b8809af8eb3813c3aa"},"final_inventory_sha256":"97b4867426f502d9b6efb4fc573f1616bd25c04b3a87cc01bba2fa9b8e5de7ff","findings":[{"authorizes_change":true,"decision":"accept","id":"B01","rationale":"Caps alone did not demonstrate feasible completion.","resolution":"Frozen guarded synthetic journal/replay, all-profile qualification and full-population analysis benchmark passes all doubled resource estimates; no target limits or sampling changed."},{"authorizes_change":true,"decision":"accepted_modified","id":"B02","rationale":"Existing campaign cubic tests already covered the combined path, but disclosure and adverse coverage needed strengthening.","resolution":"Full all-six-row matrix asserted; two-sheet campaign rejects positive support; failed bootstrap draws stay in denominator. 86 focused tests and full-population synthetic benchmark pass."},{"authorizes_change":true,"decision":"accept","id":"I01","rationale":"Fresh trajectories are separate fitting observations but capture-conditioned on the reference cycle.","resolution":"Machine result explicitly states reference-conditioned retained finite-time scope and reports q90, unsupported and coverage thresholds alongside all observed per-variant metrics; no rare-sheet or support-gap inference."},{"authorizes_change":false,"decision":"accept","id":"I02","rationale":"The known defect can affect nomination or interpretation, not the current raw event-construction path.","resolution":"EXP480 producer source matches its frozen execution version; variational correction and geometric raw roots do not call the old helper. Both raw six/eight-event audits pass again. Keep both conditional nominations; broader historical impact remains separately open."},{"authorizes_change":false,"decision":"accept","id":"I03","rationale":"Different failure mechanisms require different scientific interpretations.","resolution":"The bound adjudication document freezes a casewise five-category outcome table and full reporting template. Existing complete result preserves component reasons and all metrics; no new gate or outcome-selected threshold."}],"qualification":{"bytes":3530,"path":"docs/experiments/receipts/EXP-481-review-fixes.json","sha256":"4e2ba5aa6475cc7f3f14906c772c53c5d8acb0d75f4da51a33bac3df317e946b"},"review_sha256":"28ee5ad3cb9784693139b2b335b3a534b934afed353858e9d077828f8d19c6f9","reviewed_inventory_sha256":"3fe22cbe673dab7bf07ee2f49b3950101aaf879cab23832dd7360ccd471299e6","reviewed_packet_commit":"c8f4bc322f4e81aa94821bd1c2bc0435cc403542","schema":"butterfly.paired-review-adjudication.v1","self_sha256":"c2121c4338fa4ed9faa23ceec391a30fb8b8022a74f37e727cee3e3bbff66d40","verdict":"READY AFTER SPECIFIED FIXES"}
```

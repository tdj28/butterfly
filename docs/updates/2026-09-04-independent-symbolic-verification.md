# Independent symbolic verification: work log

## Starting point

The prominent chain diagram was transcribed and checked against Jones's
source. It was **not independently computed from new Rössler orbits**. The
user has now requested that verification explicitly. The historical diagram
and every connecting arrow remain attributed reproduction targets until new
dynamical evidence passes the necessary gates.

## Corrections made before target computation

- Clarified that the approximate-landmark test failed partition parity and
  word recovery, not a qualified symbolic-ordering test.
- Separated the local alphabet calibration at `c=20` from the landmark at
  `c=6.124`; no transport between them has been demonstrated.
- Removed the claim that the prior negative search excluded inadequate
  sampling at its tested points.
- Closed an encoder bug: a nonfinite permitted zero-slope residual could
  previously bypass the slope gate. Added regression controls; no historical
  result is silently changed or relabeled by the fix.

## New, separate verification tracks

[EXP-478](../experiments/EXP-478-quadratic-symbolic-control.md) independently
enumerates the quadratic map's finite critical-cycle words using exact
arithmetic, then compares them under a declared conditional dictionary.
This checks a limited combinatorial claim, not the flow realization.

[EXP-477](../experiments/EXP-477-symbolic-center-pilot.md) prepares a new
raw-retaining replay of the unfinished EXP-204 center scout. It uses no Jones
words and explicitly defers historical-section reconstruction, local
partition/alphabet qualification, critical membership and connecting paths.
GPU collection and local fitting are separate so the rented GPU can be
released before CPU spline/bootstrap analysis.

The read-only Runpod inspection found unrelated running workers. They are
outside this task's scope. No target execution or new paid worker has occurred
at this protocol-preparation checkpoint. Freeze commits, actual outcomes and
cost/teardown evidence will be appended rather than invented in advance.

## EXP-478 completed after public freeze

The enumerator and separate comparison were pushed at
[`f4b2ea1`](https://github.com/tdj28/butterfly/commit/f4b2ea13c60395713911240b0fbf0ce469850cc4)
before running from a clean detached checkout. Exact enumeration completed
for all prescribed periods. The conditional word-list and within-period order
comparisons both passed; the two third-branch nodes remain outside the scalar
model. The [complete experiment result](../experiments/EXP-478-quadratic-symbolic-control.md)
links the full certificates and comparison, and the manuscript now includes
a receipt-generated table. A separate code-review agent checked the source
identity, completeness and mapping after execution; this is not external
peer review or an independently implemented proof checker.

This is positive evidence for the finite combinatorial structure, not a
claim that the Rössler chains have been independently reproduced. No paid
compute was used for this calculation.

## Flow collection: storage gate, not a scientific outcome

The owned-worker executor adds authenticated task-key SSH, frozen runtime
installation, bounded raw retrieval, source/input hashes, and checks for all
551 candidates before collection can be marked complete. A partial archive
can be retrieved successfully while the experiment remains failed or
incomplete. CPU fitting is never performed on the rented worker.

Local storage currently prevents launch: the Mac reports about 8 GiB free,
whereas the frozen retrieval gate requires about 16.5 GiB for the bounded
archive, extraction and reserve. The user was asked to free at least 12 GB
or provide a writable external-drive destination. No existing research data
was deleted, and the retrieval limit was not weakened to bypass this gate.
No paid EXP-477 worker has been created. This is an operational blocker,
not a negative result about Jones's chains.

## Frozen runtime and local deployment control

The final runtime was pushed at
[`bf6231e`](https://github.com/tdj28/butterfly/commit/bf6231ed489bf9c2ee5599fa0f9ee71191578e9f)
and its exact remote SHA was checked before the known-anchor CPU control ran
from a clean checkout. Tags `exp-477-protocol` and `exp-478-protocol` retain
the exact source freezes across the eventual PR squash merge.

The [full CPU control receipt](../experiments/receipts/EXP-477-cpu-control.json)
is byte-identical to the retained local output: 219,604 bytes, SHA-256
`6849f6a1cf53689e96cc70f0b436c2823e669df105e18b378281dad0ca777118`.
Both prescribed step profiles completed and saved their event records.
This establishes the local deployment reference only: the GPU has not yet
been compared against it, and no target center or word was computed here.

Preparation-only was then attempted once. The storage gate reported
8,638,885,888 available bytes and 17,722,933,248 required bytes, and exited
before staging/upload or any provider call. No owned-worker state or cloud
attempt directory was created. The runtime is preparation-only by default;
live provisioning requires the explicit `--execute` opt-in.

Final local validation: 1,062 tests passed; the generated symbolic table,
citations/figure inventory, staged credential scan and LaTeX build passed.
The final manuscript is 70 pages with a blank author field. All pages were
visually inspected at reduced scale, with detailed checks of the new table
and revised main discussion. Python 3.12 and 3.13 CI passed on the runtime
freeze. These checks do not establish a live GPU deployment.

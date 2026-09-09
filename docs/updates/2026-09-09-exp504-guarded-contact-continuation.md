# EXP-504: follow the measured contact direction

## Current checkpoint

EXP-503 established a reproducible direction that reduced the dominant contact
gap by 5.64%, while leaving it far outside tolerance. EXP-504 now tests whether
up to eight smaller corrections can extend that improvement. The
[prospective protocol](../experiments/EXP-504-guarded-contact-continuation.md)
and [local design audit](../experiments/EXP-504-local-design-audit.md) define
the experiment before any new target trajectory is generated.

This is a directional secant continuation with warm numerical seeds, not eight
fresh two-axis derivative measurements or an independent cold-start replication.
Every step retains all 256 correlated residual variants, four fold
representations, eight boundary representations, both cycle solvers/windows,
both Decimal configurations and the unchanged full raw-data accuracy audit.
The cycle must retain its identity against both the preceding point and the
original anchor. A failed point ends the path; there is no backtracking or
replacement by a favorable earlier endpoint.

Before freeze, 68 focused tests passed, the isolated copied-source consumer
passed, and all 34 hash-bound original analytic-control files (9,701,176 bytes)
replayed without new target integrations. The first full-suite attempt retained
2,410 passes, one Linux-only skip and one new test failure: the test incorrectly
ran the production import-closure check inside the interpreter containing the
entire test suite. The test now invokes the actual isolated consumer; the
production closure restriction is unchanged. Its failed JUnit receipt is
retained under artifacts/EXP-504/pretarget-suite-01.xml.

Exact free space observed before freeze was 21,884,575,744 bytes versus a
21,474,836,480-byte admission minimum. The runner repeats admission immediately
before execution and preserves an 8 GiB floor. No data was deleted, no cloud
worker rented, no raw data uploaded and no paid model review requested.

The corrected full suite passed **2,418 tests**, with one Linux-only skip,
in 172.47 seconds; 75 focused tests also passed. Both manuscript/reference
checks passed and the staged public scan found no common credential patterns
in 2,805 files. The isolated startup passed again with the final test harness.

Before any target attempt, free space subsequently fell to 21,246,738,432 bytes,
below the draft 20 GiB admission limit. The prospective allowance was reduced
from 11 to 10 GiB and admission from 20 to 19 GiB together, preserving the
8 GiB floor and 1 GiB admission headroom. No scientific setting changed and
no target marker existed. Focused tests and isolated startup are repeated
after this resource-only change; the earlier full-suite receipt is retained.
They passed: 75 focused tests in 3.41 seconds and an isolated startup with no
target integrations. The frozen plan hash is
`a5cc08a114d1c967d6b6b22f8e7307959c7f02d7a5dc7b69af1e846ebce9774c`.

This checkpoint does not yet contain EXP-504 scientific results. The target
run and its full raw audit are the next actions after validation and live-pushed
source binding. Jones's flow-level chains remain unverified, not debunked.

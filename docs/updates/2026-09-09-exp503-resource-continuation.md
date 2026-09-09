# EXP-503 preparation: finish the same matrix if storage stops EXP-502

**Prepared, not launched.** EXP-502 continues under its original frozen caps.
Its first two complete points each occupy about 1.2 GiB. This operational
observation indicates that the 8 GiB whole-run allowance may be insufficient
for eight points plus a possible proposal. No evidence is being removed and
the original runtime's cap is not being edited.

The [resource-continuation protocol](../experiments/EXP-503-joint-contact-resource-continuation.md)
keeps every scientific setting unchanged. It requires the original archived
resource failure and at least six completed fixed points. It reuses every
complete point, preserves the interrupted attempt, and computes only the
remaining fixed slots in a new directory. Its own attempt marker is distinct;
it cannot reset the old one or race a still-running original experiment.

The first EXP-502 point's negative contact result has been inspected after
raw audit. The recovery's point selection does not depend on that result:
selection is strictly the original contiguous completed prefix. The full
matrix and exact original proposal rule still govern the result.

Only storage/time/integration-attempt allowances change prospectively. The
continuation permits at most 4 GiB of additional output, with 9 GiB free at
launch and a 6 GiB floor, retaining all original files. These are operational
limits, not relaxed accuracy or contact criteria. No paid calls, rentals,
credentials or uploads are involved. If it proves unnecessary, it will not
be run merely because the software exists.

## Outcome-free validation

Seventeen focused tests pass (`artifacts/EXP-503/preflight-focused-02.xml`).
They cover complete-prefix reuse, holes and favorable-subset rejection,
preserved unfinished slots, failed-point inclusion, exact remaining-point
selection, durable response-before-proposal ordering, unchanged/reused
proposals, resource-plan substitutions and refusal to recover a run without
an archived failure. These tests validate software, not the scientific result.

The original analytic control archive also passes replay through the successor
consumer without new integrations. Its receipt is
`artifacts/EXP-503/preflight-control-replay-01.json`.
The complete local suite passes **2,350 tests with one Linux-only skip** in
171.17 seconds (`artifacts/EXP-503/preflight-suite-01.xml`).

The final original-failure/raw hashes and the authentic isolated-source
startup can only be bound after the original process has stopped. Until then
this is prospective recovery preparation, not a final execution freeze.

# EXP-481: adaptive control passes; cycle references match their raw events

The next two implementation gaps are closed: a bounded adaptive numerical
adapter exists, and both nominated cycles' capture-reference rows have been
checked against the preserved EXP-480 raw events. No new Rössler trajectory
was generated. Jones's symbolic chain remains an unverified hypothesis.

## Numerical cross-check

`paired_adaptive.py` advances one original seed with public SciPy
[DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.DOP853.html)
or [Radau](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.Radau.html)
step/dense-output interfaces and Brent roots. Geometric membership and capture
updates now share small functions with RK4. This controls policy differences;
it is not an independent implementation of every modeling assumption.
The new adapter does not stop integration after capture.

Steps, field evaluations and raw event counts are bounded. A committed step
contains both section events and its state/capture labels together. Failures,
interruptions and callback errors return an explicit incomplete prefix; no
retry is attempted. Detached progress snapshots and an explicit final status
are available. **Durable adaptive recording and the process supervisor still
need production-path implementation and qualification.** A callback alone is
not a disk journal or a process-kill recovery guarantee.

The synthetic control uses four circle phases, physical coordinate scales
`(15,15,0.01)`, horizon 20, RK4 steps 0.01/0.005 and DOP853/Radau at
`rtol=1e-10, atol=1e-12, max_step=0.01`. Its synthetic capture threshold is two
crossings, so capture and continued observation are exercised within the short
control. That differs explicitly from production's five-crossing threshold.
All six integrator-profile pairs agree at all four seeds: **24/24 pass**.

- Largest scaled event-state discrepancy: `4.006e-11` (rounded upward).
- Largest event-time discrepancy: `1.630e-9` (rounded upward).
- Largest first-capture-time discrepancy: `9.164e-10` (rounded upward).

Each is below its `1e-4` control threshold. Ordered raw and accepted counts,
orientations and membership are checked without dropping or realigning roots.
Ambiguous roots cannot qualify, even when both methods report the same ambiguity.
These are finite-horizon analytic controls, not evidence of long-time shadowing
or complete root detection. Endpoint bracketing can miss unbracketed tangencies
or multiple roots in one step in both implementations.

The shared-policy refactor was also checked against the previous circle
integration/replay smoke: **all 2,049 arrays in all 67 NPZ files match exactly**,
including dtypes and missing-value locations. The new full replay smoke passes.
Old receipts and frozen execution sources remain untouched.

## Capture-reference input audit

`verify_paired_capture_inputs.py` checks the nominated candidates, the exact
EXP-480 source receipt, the DOP853-refined result files and their raw-file
hashes. It then recomputes vector-field normal velocities and section membership
at the saved raw states and reconstructs the exact ordered `[0.25,1.25)`-period
window. Both cases match their summaries exactly: six historical and eight
Barrio points each, with raw row indices retained. This is an audit of old
inputs, not another trajectory integration or a verified alphabet mapping.

The first attempt stopped because the newer journal's safe NPZ reader forbids
the old producer's hyphenated array names. That attempt remains preserved as
`capture-input-audit-01`. A separate exact-old-schema bounded reader fixed the
compatibility issue; the journal schema and historical bytes were not weakened
or modified. `capture-input-audit-02` passed. The future production preflight
must invoke this check again, with its own authenticated input/source bindings.

## Reproduce and inspect

```sh
PYTHONPATH=.:python .venv/bin/python scripts/qualify_paired_adaptive.py \
  --output-dir artifacts/EXP-481/synthetic-adaptive-NEW
PYTHONPATH=.:python .venv/bin/python scripts/verify_paired_capture_inputs.py \
  --output-dir artifacts/EXP-481/capture-input-audit-NEW
```

The first command needs no private inputs. The second requires the declared
local EXP-204/479/480 evidence; its hashes do not imply a public data release.
Use new output directories; do not overwrite old evidence. The
[source/hash summary](../experiments/receipts/EXP-481-adaptive-and-input-controls.json)
records the observed runs. Full raw arrays and metadata remain local.

**30 new tests pass; the full suite passes 1,469 tests**, with one Linux-only
test skipped on macOS. Code review checked callback completion, mutation
isolation, step/event/field caps, ambiguity, seed identity, rejected-root
membership, capture mismatches and malformed legacy inputs. CI is required
before merge.

## Next

Implement the bounded production supervisor and durable adaptive snapshots;
wire every fixed trial, both cases, expected-source/input checks and complete
aggregation through the real production CLI. Qualify that exact startup and
failure path before the compact design review. Then adjudicate, push the exact
freeze and run the target experiment. No additional routine user permission is
needed; the playbook's outcome-before-review boundary still applies.

The unreviewed numeric proposal now explicitly lists raw-root/capture agreement,
all six profile pairs, per-seed caps and a qualification wall bound. These are
pre-outcome clarifications, not thresholds selected from target results.
The research-integrity playbook drove preservation of failures, raw concordance
and the separation of synthetic qualification from scientific verification.
No paid model review, compute worker or remote upload was used here. The legacy
stationary-inflection historical-impact audit remains open before manuscript
release; this checkpoint does not clear earlier branch-count claims.

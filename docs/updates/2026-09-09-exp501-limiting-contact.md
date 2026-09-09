# EXP-501: does the limiting boundary meet the periodic orbit?

**The complete target run and raw audit pass: the limiting boundary still
does not meet the periodic orbit at this anchor.** All eight representations
and sixteen precision profiles qualify. None of the 384 full-state
comparisons is within the primary 1e-4 scaled-distance tolerance. The best
all-variant cycle index has distance 0.01346118, approximately 135 times the
tolerance. It also fails every declared sensitivity radius, including 1e-3.

This removes the finite-perturbation explanation for the old mismatch. It
does **not** debunk Jones's chain: our current one-fold proximity point is not
a verified combined-contact point, and this is our reconstructed section and
finite-return curve, not recovered Jones code.

The extra projected turn and the complete event census are established for
the previously tested numerical trajectories. The next missing link is
**critical-object membership on a primitive periodic orbit**, not another
crossing count. EXP-498 found a mismatch, but its preceding return states
were measured at finite perturbations to either side of grazing. EXP-501
computes the limiting boundary itself and tests whether that distinction
changes the conclusion.

## What was tested

All eight first-case boundary representations were localized with
40-digit and 50-digit state-plus-variation trajectories. Each qualified
boundary trajectory supplies its last regular return before grazing, with a
complete stored-polynomial census up to 0.05 time units before tangency.
Every resulting predecessor was compared with every one of the six cycle
events, both old integrators and both repeat windows. There is no best-case
selection and no new symbolic-label assignment.

The decimal affine initial curve is explicitly a new realized input. Old
rounded side states are not silently treated as points on it, and the prior
side-geometry checks do not automatically validate its geometry. The cycle
reference remains the original qualified EXP-497 binary64 calculation.

The [protocol](../experiments/EXP-501-limiting-grazing-contact.md) and source
were pushed before target generation at
`a8816a5cd82eae79b6a8947bbc2876f767063771`. The runtime checked that exact live
remote head. Raw coefficients, Newton iterations and certificates are retained
under `artifacts/EXP-501/target-a8816a5`; the exclusive attempt marker is
`artifacts/EXP-501/target-once.json`. No paid review, API call, rental,
credential loading or raw upload was used.

## Validation and preserved failures

The 19 focused tests pass, including analytic state/tangent identities,
known grazing recovery, complete analytic event counts, coefficient
corruption, partial archives, singular systems, box exits, complete-matrix
decisions, immutable inputs and isolated copied-source startup. The separate
saved analytic rehearsal and coefficient audit pass all four profiles.

The first full-suite invocation was sandboxed. It recorded 2,287 passes,
seven failures, eight errors and eleven skips because the older synthetic
supervisors could not execute `/bin/ps`. The exact failure evidence remains
in `artifacts/EXP-501/preflight-tests-01.xml` and the
`preflight-sandbox-process-denial` JSON/log files. No failed worker remained
in the process inventory. No scientific code or tolerance was changed.

The unchanged full suite, rerun with the required host process access,
passed **2,312 tests with one Linux-only skip** in 165.17 seconds:
`artifacts/EXP-501/preflight-tests-02.xml`. The staged public scan passed on
2,765 files; manuscript references and the symbolic control table also pass.

The local design audit specifically rejected interpreting a projected
section tangency as a second smooth scalar-map critical point, reusing old
side states as newly exact affine inputs, or selecting the closest cycle
event separately for each representation. The protocol forbids all three.
These are local checks, not external peer review or independent-team
replication.

## Audited result and replay

All 38 target integrations completed in 105.42 seconds. The saved evidence
contains 120 files before the summary, totaling 449,391,598 bytes. Every
state/tangent polynomial and Newton iteration was replay-audited locally;
every retained prefix certificate was independently checked by the separate
polynomial-count verifier. Shared event classification and Newton decision
replay are not described as independent implementations.

There are 72 accepted prefix events across the sixteen profiles. Their counts
are 4, 1, 4, 1, 5, 8, 5, 8, each measured in both precisions. These are history
prefix lengths, **not primitive periods**. All paired accepted sequences pass.

| Cycle event index (zero-based) | Worst scaled distance across all 64 variants |
|---|---:|
| 0 | 0.33316406 |
| 1 | 0.01346118 |
| 2 | 0.79531212 |
| 3 | 0.35287911 |
| 4 | 0.01619704 |
| 5 | 0.77749971 |

Each column entry takes the maximum over eight boundary representations, two
precisions, two cycle integrators and two repeat windows. It does not choose
the closest index separately for each row. Every individual comparison also
fails the primary tolerance. These repeated numerical representations are
not independent samples.

The limiting predecessor is approximately
(-11.5197725422, -0.02775458473, 0.01069530504). Its maximum scaled spread over
all sixteen numerical profiles is 1.42e-23. The grazing states themselves
have spread 6.38e-22. Thus the upstream representations recover essentially
the same physical boundary, not eight different critical objects. These are
agreement diagnostics, **not absolute error bounds or a theorem about the
exact flow**. The deliberately tangent endpoint was excluded from the prefix
census, and no new side-winding measurement was performed.

The unchanged 34-source execution freeze is preserved on
`codex/exp501-local-execution`. Summary SHA-256:
`3e47be50a4633dac544d12a1a9fdb2c0bd63430549f02afbfe8d88a3bbb0cba2`.
The [public compact result](../experiments/receipts/EXP-501-limiting-grazing-contact-result.json)
is byte-identical to `artifacts/EXP-501/primary-audit-01.json`: 510,554 bytes,
SHA-256 `c97b64e4770e1b53a66802c9bf6791fe4dbbf22e84d6d12281ccda9ae451b485`.
It preserves all comparisons, trace summaries, prefix events, input hashes
and the complete 26-candidate inherited ledger. Original EXP-492/498/499
failures remain unchanged; a new limiting-curve result does not repair them.

The post-run public verifier checks the compact comparisons without raw data:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.verify_exp501_public_contact \
  --result docs/experiments/receipts/EXP-501-limiting-grazing-contact-result.json \
  --expected-sha256 c97b64e4770e1b53a66802c9bf6791fe4dbbf22e84d6d12281ccda9ae451b485
```

With the retained local raw directory, the frozen full auditor can replay
every trajectory into a fresh receipt:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.audit_exp501_limiting_contact \
  --run artifacts/EXP-501/target-a8816a5 \
  --expected-sha256 3e47be50a4633dac544d12a1a9fdb2c0bd63430549f02afbfe8d88a3bbb0cba2 \
  --output artifacts/EXP-501/reader-audit.json --public
```

The second command is documented, not claimed as a second executed audit.
Full coefficients and certificates remain local. No off-machine raw backup,
public raw download or separate-environment trajectory reproduction is claimed.

Final release checks pass **2,318 tests with one Linux-only skip** in 165.39
seconds (`artifacts/EXP-501/release-tests-01.xml`), including 25 focused
numerical/public-replay tests. The public replay reports zero proximate cells.
All 34 frozen source hashes remain unchanged. The staged credential scan
passes on 2,769 tracked files; manuscript references and the symbolic control
table verify. Code, compact evidence and this interpretation are reviewed
through [PR71](https://github.com/tdj28/butterfly/pull/71); the public comparison
verifier is explicitly post-run and does not replace the frozen raw auditor.

## Next scientific decision

The complete negative contact result means this one-fold anchor is not
simultaneously a boundary-contact point under the declared criterion.

The limiting residual now qualifies. The next substantive experiment combines
it with the distinct right-fold residual and varies a and c jointly. Further
fixed-anchor precision refinements are not the goal. Neither one contact nor
two fitted residuals alone establish a consistent branch dictionary or a
primitive p-to-p+1 periodic-family connection.

# EXP-523: from one corrected point to a short tested path

2026-09-10. Design and local validation, not a new scientific result.

The next question is whether the accepted EXP-522 contact can be followed
toward the same inner maximum's section grazing through two successive steps.
Each step refreshes both a and c derivatives with eight new measurements,
tests a quadratic-c predictor, and permits at most one separately tested
normal correction. A failed predictor remains a failed predictor even when
its correction qualifies. The accepted endpoint radius is tightened to 1e-7;
none of the inherited geometry, identity or prediction thresholds is relaxed.

The local adversarial review found a substantive pre-execution bug: replacing
the root reference with native event order after a cyclic shift can silently
switch the physical roots represented by labels 5 and 13. The controller now
rotates only a copied reference census into the uniquely matched full-root
order, preserving the measured census and its certificates. A regression
rotates all sixteen roots and verifies their identities through successive
recentering. The scalar auditor also independently enforces branch acceptance
and normal-correction authorization, rather than checking residual size alone.

Twenty-six analytic, synthetic writer/census/auditor, source-integrity,
one-shot, sealed-consumer and deployment-metadata tests passed before freeze.
They include a tight endpoint with a correctly recorded failed prediction:
the independent scalar pass rejects its unauthorized acceptance.
The audit-phase deadline is separately tested: an audit timeout leaves the
executed raw summary intact and does not create a passing audit receipt.
The broader EXP-519/520/521/522/523 regression run also passed all 148 tests
collected before the final audit-deadline test was added; the focused 26-test
run includes that final test. The real isolated consumer validates 202 bound
source paths and a 206-file physically materialized closure.

Execution uses the existing prax host, not a paid GPU or API. Only the frozen
public source and public compact inputs are fetched from GitHub. No historical
raw archive is uploaded. The existing raw-upload restrictions remain in force.
The new output stays on prax with a consumed marker, complete raw retention,
bounded disk/wall/IVP limits and an automatically following raw audit. See the
[protocol](../experiments/EXP-523-refreshed-contact-path.md) for exact commands
and limits. Preparation, execution and audit status will be recorded separately
without changing frozen inputs or examining unaudited headline outcomes.

No C/D dictionary, grazing endpoint, homoclinic connection, exact critical
locus or Jones symbolic arrow is established by this design. A successful
result would be a short locally qualified sampled path, not the finish line.

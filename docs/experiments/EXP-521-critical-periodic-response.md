# EXP-521 — Follow periodic reinjection while preserving fold contact

Prospective, outcome-informed local mechanism test, 2026-09-10. This document
and the complete execution/audit sources are frozen before new target IVPs.
No paid review, GPU rental, or raw upload is requested. This is an investigative
Git freeze, not a registered confirmatory proof of a Jones symbolic arrow.

## Question and relevant controls

EXP-519 restored full-state fold/orbit proximity at fixed c. EXP-520 found the
actual inner periodic maxima, but their signed section gaps were still negative.
Can a bounded change in c, accompanied by an a correction preserving fold
contact, move the first inner maximum toward its section grazing? The second
inner maximum remains tracked even if it moves away. A section crossing without
fold contact does not answer this question.

The audited corrected EXP-519 point is the common seed for four fresh c offsets:
−0.005, +0.005, −0.0025, +0.0025. Each uses all four recovered fold constructions
(histories 4 and 7, both directions), DOP853 and Radau, and both periodic windows.
The existing periodic primitive/correspondence checks and historical/Barrio
counts 6/8 remain validity checks. If they change, retain the point as
unqualified; do not call a censored family an absent orbit or a verified arrow.

Every stored periodic dense segment receives the EXP-520 exact-rational
polynomial stationarity census. The raw auditor uses the separately expanded
polynomial basis and verifies every root certificate. This establishes coverage
of the **stored polynomials**, not rigorous exact-flow enclosures. Cross-solver,
callback, mesh, field-consistency, and repeated-window tests are unchanged.

Cross-parameter correspondence requires a **unique** cyclic matching of all 16
stationary points, full state, phase, and curvature. The maximum circular phase
displacement is 0.01; maximum state displacement scaled by (15,15,20) is 0.05.
These are local tracking bounds, not solver error tolerances. Source indices
5 and 13 identify the two already-observed inner maxima; nearest-index agreement
alone is not identity. All other extrema remain in the record and matching gate.

## Approximate predictor and predeclared verdict

The a derivative of full fold contact comes from EXP-519's audited coarse/fine
stencil. The corresponding gap derivative uses all four EXP-520 a-stencil
censuses, matched to the corrected anchor. Its center differs from the new
c-stencil center: this is explicitly a **two-center approximation**, not an
exact new Jacobian or proof of the tangent to an invariant locus.

Fresh c derivatives use the realized floating-point stencil separations.
Every one of 16 six-component fold variants and eight gap variants must have
coarse/fine relative disagreement at most 0.05. Full-vector and x-component
fold checks both apply. The historical a response must also qualify.

The predictor restores the mean scalar x-contact residual by a linear a
correction, then chooses the bounded c step minimizing the predicted absolute
mean gap of the first inner maximum. It is clipped to |delta c| ≤ 0.005,
|delta a| ≤ 1e−5, and the original measured a-stencil domain. No extrapolation
beyond that a domain is permitted. Realized increments, both derivative centers,
all predicted components and both inner gaps are recorded.

At most one correction is measured. It is allowed only if the response qualifies
and predicts improvement in all four contexts of the first maximum. Acceptance
requires the **freshly measured** point to pass physical correspondence, all 16
full-state contact distances ≤ 1e−4, all 16 full-vector prediction errors ≤ 0.1
of predicted motion, and all eight gap prediction errors ≤ 0.1 of predicted
motion. Denominator floors are 1e−12 for full vectors and 1e−8 for gaps. Each of
the first maximum's four measured absolute gaps must improve. The second maximum
need not improve, but cannot fail identity or prediction checks. A failed or
absent predictor is reported, never replaced by the most favorable stencil point.

These variants are numerical robustness checks of one branch, not independent
statistical samples. There are no confidence intervals or population claims.

## Execution, accounting, and audit

The immutable EXP-519 and EXP-520 completed audit receipts are authenticated
directly by fixed SHA-256. Their numerical runtime sources remain byte-identical.
The new runner does not rerun the expanding historical authorization chain;
it does audit every new raw midpoint, fold, guard, cycle, and polynomial record.
This input-authentication design cannot retroactively approve a failed parent.

Before target access, the complete source allowlist runs the real validator in
a fresh `python -I -B` tree without raw targets. Analytic census controls,
synthetic known linear response, failed stencils, false branch matches, full-state
and secondary-gap failures, scalar-audit tampering, and one-shot guards must pass.
The live remote must match the clean frozen source commit. Runtime Python,
NumPy and SciPy versions are recorded before outcomes.

One consumed marker, one fresh output namespace; no silent retry. Limits: 768
target IVPs, 7,200 seconds, 600,000 stored segments, 3 GiB output, 12 GiB initial
free space, 8 GiB free-space floor, 1 MiB failure reserve. All raw numeric arrays
remain local, retained in their existing binary format; public compact audit
receipts permit checking derived values but are not a substitute for raw data.
Producer and auditor share geometry and controller code, with separate scalar
predictor arithmetic and exact-basis checks: do not call this independent-team
verification. Infrastructure or scientific failures remain recorded.

Commands (with the actual pushed commit and dedicated ref substituted):

```sh
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp521_critical_response.py --prepare
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp521_critical_response.py --startup
PYTHONPATH=.:python .venv/bin/python -B scripts/run_exp521_critical_response.py --execute --source-commit COMMIT --remote-ref refs/heads/codex/exp521-local-execution --output artifacts/EXP-521/target-COMMIT
PYTHONPATH=.:python .venv/bin/python -B scripts/audit_exp521_critical_response.py --run artifacts/EXP-521/target-COMMIT --expected-sha256 SUMMARY_SHA --output artifacts/EXP-521/primary-audit-01.json
```

## Claim boundary and escalation

A positive result is one empirically validated, local contact-preserving step
toward the identified periodic grazing candidate. It is not a critical endpoint,
a C/D dictionary, an exact invariant locus, a homoclinic orbit, a Jones word
arrow, or coverage of the full parameter plane. A negative result rejects this
predictor or its local validity, not Jones globally. Stop for new authority if
paid review, new private-data transfer, or a material risk/scope expansion is
required. Ordinary numerical follow-up is not blocked on optional Pro review.

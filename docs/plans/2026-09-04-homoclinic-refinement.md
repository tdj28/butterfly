# Next bounded homoclinic accuracy test

Status: proposed implementation task after EXP-475, **not a frozen protocol or
an executed experiment**. Commit a validated manifest and passing control tests
before any new target run. Do not change acceptance gates after seeing results.

## Question

Can numerical discretization sensitivity be separated from the effect of
approximating the infinite homoclinic orbit by finite-radius endpoints?
EXP-475's tolerance change shifted `a` more than its final radius change.
Tightening only the smallest-radius case does not settle the endpoint trend.

## Proposed design

Use the same hash-bound EXP-342 initial trajectory and unchanged canonical
Rössler equations at `(b,c)=(0.2,10.3084)`. Keep the eigenspace endpoint
conditions, parameter/time box, and independent short-arc replay. Reconstruct
the initial guess independently for every case rather than warm-starting from
another grid result.

| Departure and arrival radius | Collocation tolerances |
| --- | --- |
| 0.01 | `1e-6`, `1e-7`, `1e-8` |
| 0.005 | `1e-6`, `1e-7`, `1e-8` |
| 0.0025 | `1e-6`, `1e-7`, `1e-8` |

Within each radius, run loose to tight tolerance. Preserve all nine paths and
diagnostics, including any unsuccessful solve.

## Implementation checklist

- [ ] Add a v2 manifest/analysis path to the existing runner; preserve the
  four-case EXP-475 v1 behavior and its frozen evidence.
- [ ] Validate a complete Cartesian grid with unique radius/tolerance pairs.
  Compute comparisons by metadata, not positional case indices.
- [ ] Repeat analytic Duffing controls at tolerance `1e-8`, including the
  positive-`mu` negative control (`H'=mu*y^2` implies energy injection).
- [ ] Test missing/duplicate grid cases, failure propagation, comparison
  grouping, nonfinite diagnostics, and deadline behavior before target use.
- [ ] Freeze explicit numerical and resource gates, then commit and push
  source and protocol before the target invocation.

## Proposed gates to freeze

Retain EXP-475's boundary limit `1e-8`, parameter-interiority margin `1e-4`,
minimum excursion `5`, and source-parameter agreement `2e-5`. Require a
successful short DOP853 replay with maximum state defect no larger than the
case's collocation tolerance.

At each radius define `D1=|a(1e-7)-a(1e-6)|` and
`D2=|a(1e-8)-a(1e-7)|`. A proposed empirical refinement criterion is
`D2 <= 1e-9` and `D2 <= 0.3*D1 + 1e-10` at every radius. Compare adjacent
radii at the common `1e-8` tolerance. Treat a radius effect as empirically
resolved only when the neighboring `D2` values sum to at most one-quarter
of that radius difference; otherwise report it as unresolved, or below the
declared empirical resolution when both effects are sufficiently small.
The exact classification rule must be encoded and tested in the manifest
implementation, not decided after the target results.

Keep technical success, discretization refinement, and endpoint-effect
resolution as separate outcomes. These remain sensitivity tests, **not
rigorous parameter error bounds**. A failed accuracy comparison must not
erase valid finite-radius solutions or trigger an automatically retuned run.

Proposed resource caps: 45 seconds per case, 300 seconds overall, and 48,000
collocation nodes, with cooperative deadline checks. EXP-475's 6,545-node
refined case does not establish that the old 16,000-node cap accommodates
two further tolerance reductions. The proposed larger cap is a bounded
capacity choice, not a runtime or convergence guarantee. Stop and retain the
failure if a resource cap is reached. No GPU or paid worker is needed for
this proposed local pilot.

Only after this initial-point study should selected pre-turn and near-turn
points be tested, with bound seed metadata, trajectory-identity checks, and
separate sensitivity estimates for `a` and `c`.

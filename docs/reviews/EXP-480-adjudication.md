# EXP-480 review adjudication and pre-target amendment

The GPT-6 Astra Pro/medium review returned **READY AFTER SPECIFIED FIXES**.
This is advisory model review, not independent scientific verification.
Its exact packet and response are retained in `EXP-480-review-01/` beside
this document. The original brief, protocol and review-closure note remain
unchanged so that the submitted packet can be reconstructed. This amendment
supersedes their draft endpoint and adds the gates below before any target run.

| Finding | Decision and implementation |
| --- | --- |
| B01 | Accepted with clarification. Every plane root retains signed scaled gate distance. Every oriented root, including a gate-rejected root, is unresolved within `1e-5` of the gate. Low-angle roots of either orientation are unresolved across the entire horizon. Added inside/outside/near-edge and weak-orientation tests. On the exact historical Rössler plane, `dy/dt=x-x_small`, so gate edge and zero normal velocity are related; the review's generic geometric independence argument is not literally applicable here. The absolute scaled margin still provides a useful additional numerical exclusion. |
| B02 | Accepted. Gate units and interpretation are specified below. Added an anisotropic analytic attracting cycle with a perturbed initial state/period through the actual variational shooting corrector and all four event profiles. The former tests stubbed correction; this test does not. All 23 focused tests pass locally, including the predetermined adverse cases. No threshold was fitted to either nomination. |
| I01 | Accepted by narrowing. Endpoint is paired-section event reproducibility on the same corrected trajectory. No cross-section bijection, event transport map, or robust merged interleaving is established. No merged-order algorithm added. |
| I02 | Accepted. Runtime emits casewise and overall `qualified`, `numerically-unresolved-or-not-qualified`, or `invalid-execution` outcomes alongside detailed diagnostics. Both cases must qualify for an overall pass; failures or mixed results do not authorize selecting only a favorable case for the successor. |
| I03 | Accepted with explicit operator policy below. No claim of a hard per-solver timeout or a new paid host. |
| I04 | Deferred to the separately frozen successor, mandatory before its execution. Seed/trajectory is the sampling unit; unequal event counts require an explicit weighting estimand as well as common capture conditioning. Holdout, coordinate choice, map adequacy, support and sample-size rationale must be fixed without optimizing for a desired source word. |

## Gate definitions and accuracy interpretation

Let `S=diag(15,15,0.01)`, `d_s(u,v)=||S^-1(u-v)||_2`, normal `n`,
plane function `h(u)=n.u-offset`, vector field `f`, and corrected period `T`.
These are numerical agreement budgets, not validated upper error bounds or
coordinate-invariant topological certificates. Solver agreement can share bias.

| Metric | Gate, units and purpose |
| --- | --- |
| Flow closure | `||u(T)-u(0)||_2 <=1e-9`, raw nondimensional state coordinates |
| Shooting phase | Absolute dot product with unit physical phase direction `<=1e-10`; same raw coordinates |
| Seed correction | `d_s(corrected,seed)<=1e-3`; preserve the nominated cycle locally |
| Period agreement | Relative seed change `<=1e-5`, cross-profile change `<=1e-7`; dimensionless |
| Event state agreement | `d_s<=1e-6`; componentwise implies x/y differences at most `1.5e-5`, z at most `1e-8` |
| Event phase agreement | `|t_1/T_1-t_2/T_2|<=1e-7` within corresponding fixed windows; no fitted rotation |
| Gate margin (new) | Signed `(u[gate_axis]-gate_upper)/S[gate_axis]`; absolute value must exceed `1e-5` at all oriented roots, even rejected ones; ten times the scaled state-agreement budget (historical x margin `1.5e-4`) |
| Orientation | `|n.f|/(||n|| ||f||)>=1e-6` at all detected plane roots; zero speed is unresolved |
| Distinct events | Every pair in a window has `d_s>=1e-5`, ten times state agreement |
| Window boundary | All accepted event phases stay at least `1e-7` from either fixed endpoint; counts cannot be stabilized by moving a window |
| Near-plane extremum | Minimum `|h|/||n*S||>=1e-8` among gate-relevant detected normal-velocity extrema; diagnostic only, not evidence that undetected roots/extrema do not exist |

First-order sensitivity is `delta t approximately -delta h/(n.f)` and
`delta phase approximately delta t/T`. Thus a state-comparison threshold
alone cannot guarantee the phase threshold, especially at low speed; both are
checked separately, alongside angles and margins. The gate margin is a
conservative operational exclusion relative to observed agreement, not a
probabilistic confidence interval. Boundary/phase and extremum gates similarly
do not convert solver tolerances into a rigorous uncertainty enclosure.

Any numerical or geometric gate failure means this setup is not qualified;
it does not falsify the orbit, partition or Jones chain. A missing profile or
interruption is incomplete qualification. A final source/raw integrity failure
invalidates both casewise qualifications. A pre-execution binding failure
prevents target execution entirely and is recorded by the operator.

## Analytic calibration and retained control scope

The new exact cycle is `(15 cos t,15 sin t,0.01(1+cos t))`, period `2*pi`.
In scaled coordinates it solves `X'=X(1-X²-Y²)-Y`,
`Y'=Y(1-X²-Y²)+X`, `q'=X'-(q-1-X)`. Its radius and q direction are
attracting. The test substitutes this field and its analytic Jacobian into the
unchanged production shooting function, not a simulated correction result.
It starts at radius `1+2e-7` and period `(2*pi)(1+1e-7)` and requires multiple
corrector evaluations. All four profiles pass the full correction-to-event
pipeline; recovered period agrees with `2*pi` within `1e-9`, event phases
within `1e-7`, and analytic event states within `1e-6` in the declared metric.

Adverse controls cover gate distances `-2e-5,-5e-6,+5e-6,+2e-5`, an
analytically weak transverse projection, and synthetic near-plane extrema,
fixed-boundary ambiguity and indistinguishable neighboring events. They
establish those declared outcomes, not general all-root detection. All focused
tests passed on the same local Python 3.13/SciPy environment intended for the
target run; JUnit output is retained with the review bundle. The canonical
review helper's 22 tests/10 subtests also passed, but were rerun while the API
request was already in flight, not represented as an earlier qualification.

## Execution policy

Run once on the current local Mac CPU from the clean pushed source after
adjudication binding. Retain both nominations, all four profiles, all original
numerical thresholds other than the added gate exclusion, and every failure.
No automatic retry, threshold relaxation or target-driven redesign. The
cooperative 1,800-second budget remains; an operator monitors the job at most
30 seconds apart and sends SIGINT to this exact job at 2,100 seconds if still
running. If it fails to return within 60 seconds, terminate only that job and
retain the launcher exit status and whatever files exist. An absent final
receipt is incomplete, never a pass. This is an operator policy, not a
hard real-time guarantee. Expected raw storage is below 100 MB for eight short
profiles; preserve partial output on disk pressure and do not discard failures.

The next decision is casewise numerical qualification only. Even if both pass,
partition/critical-membership/letter/arrow tests require their separate freeze.

## Review provenance and cost

One generating request completed. The first local attempt (`review-01`) failed
on broad `.env` permissions before key loading/token counting/generation. It
was preserved; permissions were restricted to owner-only access. The identical
packet completed in `review-02` and is promoted under the originally reserved
public `EXP-480-review-01` name; directory numbering is not a count of paid calls.
Canonical completed-bundle verification passed; response metadata matches the
exact packet at pushed commit `82d5915da16e61342bb4bcf42b5390b854b972e0`.
Reported usage reconstructs a conservative cost of **$0.58094**, below the
$1.50 authorization guard. The exact token-count reserve was $1.1643. This is
the cost of this review, not an account-wide or cumulative project spend total.

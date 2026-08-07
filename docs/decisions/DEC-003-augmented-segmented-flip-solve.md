# DEC-003 — Replace outer scalar refinement with an augmented segmented flip solve

Date: 2026-08-07
Status: completed; exact-Jacobian validation and target solve passed

## Context

EXP-093 prospectively brackets the period-640 signed `-1` crossing inside
`1e-8`. EXP-094 through EXP-096 then localize the baseline-solver sign change
far beyond the parameter-uncertainty target but fail the frozen pointwise
multiplier residual. EXP-097 proves that block-cyclic roots and four direct
monodromy products agree near `1e-13`; it identifies integration accuracy as
the remaining shift. EXP-098/099 repeat the refinement with the audited tight
solver and retain a `3.22e-15` sign bracket, but the closest pointwise residual
is `1.697e-8`, narrowly outside the unchanged `1e-8` gate.

At this scale, an outer root finder asks a separately corrected periodic orbit
and a postprocessed multiplier to agree at a parameter displacement of only a
few double-precision ulps. Repeating secant resumes is no longer a defensible
way to improve the scientific claim.

## Decision

Implement a square augmented multiple-shooting system that solves the periodic
orbit, `b`, and the `-1` tangent direction simultaneously.

For `N` shooting segments, use unknowns

```text
(x_0, ..., x_{N-1}, T, b, v_0, ..., v_{N-1})
```

with `6N+2` scalar components. Enforce:

1. `3N` orbit matching equations
   `Phi_i(x_i; T/N, b) - x_{i+1} = 0` with cyclic state indexing;
2. one orbit phase condition;
3. `3(N-1)` tangent transport equations
   `D Phi_i v_i - v_{i+1} = 0`;
4. the three-component anti-periodic boundary equation
   `D Phi_{N-1} v_{N-1} + v_0 = 0`; and
5. one eigenvector normalization `||v_0||^2 - 1 = 0`.

This is a square `6N+2` system. The anti-periodic boundary encodes the full-
orbit multiplier `-1` directly; it does not infer the sign by taking a modulus.

## Validation order

1. Run the implementation at the already passed EXP-089 period-320 event with
   32 segments. Require recovery of its event parameter and signed multiplier
   within frozen validation tolerances.
2. Only if that validation passes, apply the unchanged implementation to the
   EXP-099 period-640 bracket with 64 segments and the EXP-097 tight solver.
3. Independently recompute block-cyclic and direct-product spectra at any
   accepted solution.
4. Attempt a period-1280 branch switch only after all augmented event gates
   pass.

## Acceptance boundary

The future manifest must freeze bounds, scaling, Jacobian strategy, iteration
budget, known-event validation tolerances, target matching/phase/tangent/
normalization residuals, source-bracket containment, prediction error, and
independent spectral agreement before execution.

If a finite-difference sparse Jacobian is used initially, its sparsity pattern
must reflect the local segment dependencies and the result must be repeated at
a tighter differencing scale. An analytic or automatic-differentiation
second-variational implementation remains the preferred production endpoint.

## First implementation result

EXP-100 implemented the square system with a colored sparse finite-difference
Jacobian. It exhausted 30 evaluations after `2367.32 s`; tangent transport
fell to `2.14e-9`, but orbit matching stopped at `1.73e-7` and the known event
was missed by `4.91e-9`. Direct monodromy products give
`-0.99999998557114`, so the anti-periodic equation is acting on the intended
flip direction, but the corrector does not pass.

The next implementation will integrate the Rössler flow, first variation,
parameter sensitivity, tangent transport, and Hessian-vector action together.
Because the Rössler Hessian has only the bilinear third-component coupling,
this supplies the exact augmented Jacobian with one integration per segment
and removes the colored finite-difference multiplier. Independent validation
will identify the flip cluster by proximity to `-1`; EXP-100 showed that the
generic neutral/nontrivial block labels are ambiguous at the simultaneous
`+1`/`-1` unit-circle collision.

EXP-101 implements that exact Jacobian and passes its finite-difference unit
checks. Its first frozen run is `11.4x` faster and reaches orbit/tangent
residuals `1.78e-9`/`1.77e-10`; direct and block flip multipliers agree within
`3.20e-14`. It nevertheless exhausts 20 evaluations with parameter error
`1.086e-9`, above the `5e-10` known-event gate. The analytic formulation is
therefore numerically supported but not yet validated. One receipt-bound resume
is allowed before changing scaling or nonlinear solver.

EXP-102 binds that full state and passes. It recovers the known event at
`b=0.17971249399303613`, `8.94e-13` from EXP-089, with orbit/tangent residuals
`9.21e-13`/`1.01e-11` and block/direct flip agreement `8.88e-15`. The
analytic augmented formulation is validated at period 320. Validation order
now permits a frozen 64-segment application to period 640; it still forbids a
period-1280 branch switch until the target event itself passes.

EXP-103 applies the validated formulation to the 64-segment period-640 parent
and passes at `b=0.17971219643223899`, with orbit/tangent residuals
`1.46e-12`/`7.81e-12` and direct multiplier
`-0.999999999809874`. DEC-003's event-solve objective is complete. Its final
acceptance boundary now unlocks a separately frozen period-1280 branch switch
and qualification; it does not itself establish the child or criticality.

## Consequences

- CLM-021 retains a prospectively successful signed bracket for the eighth
  event, not a corrected eighth event.
- EXP-094 through EXP-096, EXP-098, and EXP-099 remain failed experiments; the
  augmented solve cannot retroactively convert them into passes.
- The period-1280 child remains unclaimed.
- The three-worker EXP-097 audit shows that local CPU parallelism is effective.
  GPU rental remains unnecessary for this serial/corrector bottleneck.

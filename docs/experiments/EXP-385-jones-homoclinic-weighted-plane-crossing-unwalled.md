# EXP-385 — Unwalled weighted-plane homoclinic crossing

Status: completed; failed direction and historical-section gates

EXP-384 aborts before solving because its exact passed EXP-383 warm start lies
below the optimizer's prospective `c>=current+1e-6` wall.  EXP-385 removes
only that optimizer bound.  It keeps the final forward-`c` acceptance check,
so a wrong-direction root still fails, and it keeps the explicit
`a<=0.1798` section requirement.

All mathematical settings remain unchanged: exact EXP-367/368 sources, exact
EXP-383 512-arc warm state, `Delta c=7.5e-5`, unit `a/c` and `0.01` nuisance
weights, analytic variational sensitivities, CSR/LSMR correction, Radau
tolerances, source-centered node/global bounds, and `1e-8` matching and
arclength gates.

Manifest:
[`../../experiments/manifests/EXP-385-jones-homoclinic-weighted-plane-crossing-unwalled.json`](../../experiments/manifests/EXP-385-jones-homoclinic-weighted-plane-crossing-unwalled.json).

A pass qualifies a bracket with EXP-368, not the exact fixed-`a` root or a
uniqueness claim.

## Result

The solver converges normally in 11 evaluations to a root with maximum
matching-block defect `7.486335903e-9` and weighted-plane residual
`-1.33740e-13`.  The method and root gates therefore pass.  The point is

```text
(a, c) = (0.17982131899981937, 10.31706975194687)
```

It moves backward from EXP-368 in `c` and remains above `a=0.1798`, so both
prospective scientific gates fail.  The wrong-side result is preserved as an
intersection/basin diagnostic, not added to the qualified curve and not used
as a historical bracket.

EXP-386 retains the identical weighted plane and forward optimizer bound but
starts from the forward full-state predictor instead of the incompatible
zero-step warm state.  This tests whether the regularized system has a forward
root without allowing the optimizer to return to EXP-385's basin.

Raw receipt: `artifacts/EXP-385/receipt.json`, 80,166 bytes, SHA-256
`a6ea4797363909cbb76b741120a2e6642403a8fefa0d1c915053640e8e6ce10e`.

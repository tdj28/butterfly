# EXP-387 — Small-step weighted homoclinic continuation

Status: executed; failed prospectively

EXP-386 shows that the `7.5e-5` crossing predictor is too aggressive for the
forward-constrained weighted plane: correction returns to the lower `c` wall.
EXP-387 reduces only the desired increment to `2e-5` and the forward optimizer
floor to `1e-7`.  The resulting predictor remains above `a=0.1798`; this is a
continuation recovery step, not a bracket experiment.

The exact EXP-367/368 sources, 512 arcs, weights, analytic sensitivities,
CSR/LSMR solver, Radau/manifold settings, source-centered bounds, 40-evaluation
budget, and `1e-8` matching/arclength gates remain unchanged.  A pass would
have added a twelfth qualified curve point and supplied a shorter secant for
the next historical-section attempt.

## Result

EXP-387 does not pass.  Reducing the requested step from `7.5e-5` to `2e-5`
improves the maximum matching defect from EXP-386's `6.18779e-7` to
`6.13398e-8`, while the weighted-plane residual closes to `7.55e-12`.  The
corrector nevertheless lands at

```text
(a, c) = (0.1798178734985330, 10.317081588742070)
maximum block defect = 6.133982101150316e-8
matching residual norm = 7.701744001286874e-8
```

The final `c` is, to numerical precision, the prospective lower wall
`current c + 1e-7`; its normalized boundary margin is `1.87e-13`.  The root
gate and global-interiority gate therefore both fail.  This is not a twelfth
curve point and is not evidence that the qualified branch terminates.

The roughly tenfold defect improvement under a 3.75-fold step reduction shows
that step size matters, but repeated wall capture in EXP-386 and EXP-387 says
that shrinking the step alone is no longer the best next test.  The next
prospective control reduces the nuisance contribution of the weighted closing
plane while retaining enough of it to regularize the pure physical plane's
near-null node mode.

Raw receipt: `artifacts/EXP-387/receipt.json`, 81,118 bytes,
SHA-256 `0784966ec1933319d8ed7a678b0c98ce92ec26426fcc4f801b48763be7dce92d`.
Compact receipt: [`receipts/EXP-387.json`](receipts/EXP-387.json).

Manifest:
[`../../experiments/manifests/EXP-387-jones-homoclinic-weighted-plane-small-step.json`](../../experiments/manifests/EXP-387-jones-homoclinic-weighted-plane-small-step.json).

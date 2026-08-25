# EXP-386 — Forward-predictor weighted-plane crossing

Status: completed; failed on forward optimizer wall

EXP-385 proves that the weighted square system has a sub-gate wrong-side root
when correction starts from the zero-step warm state without a directional
optimizer wall.  EXP-386 returns to the frozen forward bound from EXP-384 but
removes the incompatible warm-start binding.  Correction therefore begins at
the declared full-state predictor, which is strictly inside every bound.

All scientific choices remain fixed: EXP-367/368 sources, 512 arcs,
`Delta c=7.5e-5`, unit `a/c` and `0.01` nuisance weights, analytic
sensitivities, CSR/LSMR, manifold/Radau settings, `1e-8` matching and plane
gates, final forward motion, and `a<=0.1798`.

Manifest:
[`../../experiments/manifests/EXP-386-jones-homoclinic-weighted-plane-predictor-crossing.json`](../../experiments/manifests/EXP-386-jones-homoclinic-weighted-plane-predictor-crossing.json).

A pass qualifies a bracket with EXP-368.  It does not yet qualify the exact
fixed-`a` intersection or uniqueness.

## Result

EXP-386 runs the full 40-evaluation budget.  It reduces the maximum matching
defect from `1.18019e-3` to `6.18779e-7` and closes the weighted plane to
`1.10200e-13`, but it lands exactly on the prospective
`c=current_c+1e-6` optimizer wall.  The final point

```text
(a, c) = (0.17982129005720598, 10.317082488741885)
```

remains above the historical section.  Root, global-margin, optimizer-status,
and section gates fail.  The monotone late residual decrease does not license
more iterations at the wall.

EXP-387 reduces the desired forward increment from `7.5e-5` to `2e-5` and
the proportional optimizer floor to `1e-7`.  It seeks another qualified point
above the historical section; no crossing gate applies.

Raw receipt: `artifacts/EXP-386/receipt.json`, 86,294 bytes, SHA-256
`24471c96d0324a71a4a1bcbf5ef56905cfb226dfc847fc549ce88b7eed5412a2`.

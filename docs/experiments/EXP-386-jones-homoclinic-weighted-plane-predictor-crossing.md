# EXP-386 — Forward-predictor weighted-plane crossing

Status: frozen; not yet executed

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

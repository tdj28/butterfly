# EXP-392 — Local-tangent homoclinic forward step

Status: frozen; not yet executed

EXP-391 passes the local-tangent zero-step control and measures a scaled `c`
component of `0.00138650`.  A `Delta c=5e-7` predictor therefore has normalized
tangent length `0.09015`, conservatively below the `0.167--0.527` normalized
steps of EXP-366--368.

EXP-392 freezes that first forward step.  The Jacobian-derived tangent, passed
`0.003` closing metric, 512 arcs, analytic sensitivities, CSR/LSMR corrector,
Radau/manifold settings, bounds, 40-evaluation budget, `1e-8` root/arclength
gates, `1e-8` tangent-residual gate, and `5e-10` conditioning gate are
unchanged.  The prospective forward optimizer floor is `current c+1e-8`.

A pass adds a twelfth qualified curve point above `a=0.1798`.  It does not
qualify the historical section, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-392-jones-homoclinic-local-tangent-forward-step.json`](../../experiments/manifests/EXP-392-jones-homoclinic-local-tangent-forward-step.json).

# EXP-389 — Lower-weight homoclinic forward step

Status: frozen; not yet executed

EXP-388 passes the prerequisite zero-step control under nuisance weight
`0.003`, reproducing the EXP-368 root while retaining a minimum Jacobian
singular value of `1.76697e-9`.  EXP-389 now executes the licensed forward
test.

The desired increment remains the smaller EXP-387 value `Delta c=2e-5`, and
the predictor must lie inside `c >= current c + 1e-7`.  The exact EXP-367/368
sources, 512 arcs, analytic sensitivities, CSR/LSMR solver, Radau/manifold
settings, source-centered bounds, and 40-evaluation budget remain unchanged.
The `1e-8` matching/arclength gates are joined by the prospectively established
`5e-10` minimum-Jacobian-singular-value gate.

A pass adds a twelfth qualified curve point above `a=0.1798` and licenses a
shorter-secanted section attempt.  It does not itself qualify the exact
historical fixed-`a` intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-389-jones-homoclinic-lower-weight-forward-step.json`](../../experiments/manifests/EXP-389-jones-homoclinic-lower-weight-forward-step.json).

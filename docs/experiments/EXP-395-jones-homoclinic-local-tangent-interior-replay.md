# EXP-395 — Interior-bound local-tangent replay

Status: frozen; not yet executed

EXP-394's quarter step terminates normally with `7.14831e-9` maximum block
defect and passing tangent/conditioning gates, but its predictor was only
`1.225e-7` from the forward optimizer wall.  It was therefore incompatible
with the unchanged `1e-6` global-interiority gate before the solve began.

EXP-395 removes only that optimizer wall.  It retains the independent final
`c>current` direction gate, `Delta c=1.25e-7` (`0.02254` normalized step), the
wide angle interval, 512 arcs, analytic sensitivities, weighted metric,
CSR/LSMR corrector, 40-evaluation budget, manifold/Radau settings, and every
tangent, root, arclength, conditioning, and scientific margin threshold.  The
runner now preflights the predictor against the frozen acceptance margin.

A pass adds a twelfth qualified above-section curve point.  A backward result
or non-root remains a preserved failure; neither outcome alone qualifies the
historical intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-395-jones-homoclinic-local-tangent-interior-replay.json`](../../experiments/manifests/EXP-395-jones-homoclinic-local-tangent-interior-replay.json).

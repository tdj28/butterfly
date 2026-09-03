# EXP-366 — Sixth homoclinic pseudo-arclength step

Status: passed

EXP-366 chains the recovered 256-arc EXP-365 root with qualified EXP-363,
deterministically subdividing only the older source. It retains 256 arcs,
`Delta c=0.00025`, both free parameters, all manifold and Radau settings,
analytic sensitivities, bounds, the 40-evaluation cap, and both `1e-8` gates.

Passing supplies the next point toward a bracket of exact `a=0.1798`. It
cannot alone qualify that section or establish uniqueness or
computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-366-jones-homoclinic-pseudoarclength-step6-256arc.json`](../../experiments/manifests/EXP-366-jones-homoclinic-pseudoarclength-step6-256arc.json).

EXP-366 passes all ten checks with normal `gtol` termination after four
function evaluations. The qualified point is
`(a,c)=(0.17994735760827762,10.316682603352687)`, with maximum matching defect
`5.88416329959764e-9`, matching-residual norm `1.581889444633071e-8`, and
arclength residual `-4.103722570092394e-12`. Node margin is `0.87842`.

The local slope is `-0.3255534558`, projecting exact `a=0.1798` at
`c=10.3171352406`. The point remains `1.47358e-4` above the historical
section.

Raw receipt: `artifacts/EXP-366/receipt.json`, 40,734 bytes, SHA-256
`dee39d00b301ee7b551b808c4a90c7d45479cf3f13fc84d7b7c833baafbfedfb`.

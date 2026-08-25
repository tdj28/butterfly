# EXP-394 — Quarter-step local-tangent homoclinic continuation

Status: executed; administrative acceptance-geometry failure

EXP-393's wide-angle control moves the departure angle well into the interior,
but the `0.09015` normalized tangent step remains on its forward-`c` wall,
above the matching gate, at the evaluation budget, and just below the frozen
conditioning floor.

EXP-394 implements the preregistered step reduction.  It reduces
`Delta c=5e-7` to `1.25e-7`, hence the normalized local-tangent step from
`0.09015` to `0.02254`, and proportionately reduces the prospective `c` floor
to `current+2.5e-9`.  It retains the `1.0` angle half-width, 512 arcs, analytic
sensitivities, weighted metric, CSR/LSMR corrector, 40-evaluation budget,
manifold/Radau settings, and every tangent, root, arclength, conditioning,
direction, and margin gate.

A pass adds a twelfth qualified above-section curve point.  Failure preserves
the eleven-point curve and triggers a coordinate/phase-gauge audit rather than
another post hoc threshold relaxation.  Neither outcome alone qualifies the
historical intersection, uniqueness, proof, or global topology.

## Result

EXP-394 does not pass, but its numerical correction is substantially better:

```text
(a, c) = (0.17981754274779513, 10.317081496973122)
maximum block defect = 7.148310862159073e-9
arclength residual = 6.189249040036184e-11
minimum singular value = 1.888056812441179e-9
```

The optimizer terminates normally after seven evaluations, the tangent and
conditioning gates pass, and normalized node motion falls to `0.04591`.
However, the generic global-interiority gate requires `1e-6` clearance from
every optimizer wall.  The `1.25e-7` predictor is only `1.225e-7` above its
prospective `c=current+2.5e-9` floor, so the experiment was incapable of
starting inside its own acceptable `c` region.  The final point remains only
`5.73e-9` from that wall and therefore cannot be counted.

This is an administrative acceptance-geometry incompatibility, not evidence
against the root or tangent.  The runner now rejects such manifests before an
expensive solve.  EXP-395 removes the optimizer's forward wall while retaining
the independent final `c>current` direction gate and all scientific margins.

Raw receipt: `artifacts/EXP-394/receipt.json`, 79,816 bytes,
SHA-256 `6d1f6438b25a5015d63f962a3d077a6c94638076459cc7672664142ffc4ee71d`.
Compact receipt: [`receipts/EXP-394.json`](receipts/EXP-394.json).

Manifest:
[`../../experiments/manifests/EXP-394-jones-homoclinic-local-tangent-quarter-step.json`](../../experiments/manifests/EXP-394-jones-homoclinic-local-tangent-quarter-step.json).

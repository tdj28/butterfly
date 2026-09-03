# EXP-392 — Local-tangent homoclinic forward step

Status: executed; failed prospectively

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

## Result

EXP-392 does not pass.  The local tangent remains machine-accurate, but the
corrector terminates at

```text
(a, c) = (0.1798182756914287, 10.317081498741986)
maximum block defect = 1.1738036769570498e-7
arclength residual = 2.8969626827621275e-11
```

Both the prospective `c=current+1e-8` floor and the departure-angle lower
bound are active; the latter has only `5.15e-11` normalized margin.  The
matching and global-interiority gates therefore fail.  Node displacement is
`0.19648`, still interior but much larger than the zero-step control.

This is a local nonlinear-correction failure, not a tangent failure: the
tangent residual remains `1.40565e-16` and the conditioning gate passes at
`1.20583e-9`.  Because the angle wall is independently active, the next
prospective successor widens only its half-width from `0.25` to `1.0` before
reducing the tangent step.

Raw receipt: `artifacts/EXP-392/receipt.json`, 85,175 bytes,
SHA-256 `b0589f9900683aa21144235ad559e2731deec9992d7327a967b6e10a5e63f6f6`.
Compact receipt: [`receipts/EXP-392.json`](receipts/EXP-392.json).

Manifest:
[`../../experiments/manifests/EXP-392-jones-homoclinic-local-tangent-forward-step.json`](../../experiments/manifests/EXP-392-jones-homoclinic-local-tangent-forward-step.json).

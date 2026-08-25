# EXP-396 — Standard local-tangent plane positive control

Status: executed; passed prospectively

EXP-395's wall-free quarter step finds an interior root but moves `0.47244`
radians in departure angle and ends `7.03e-8` backward in `c`.  Its weighted
closing normal is `0.87565` node norm but `0.40470` in `c`, whereas the actual
scaled matching-Jacobian tangent is `0.999992` node norm and only `0.0013865`
in `c`.  This nominates closing-plane rotation as the next controlled factor.

EXP-396 is a zero-step positive control.  It sets every scaled tangent-group
weight to one, making the closing-plane normal the normalized local tangent
itself.  It retains the exact source bindings, 512 arcs, analytic
sensitivities, CSR/LSMR correction, wide angle interval, stationary-`c` gate,
12-evaluation budget, manifold/Radau settings, and every tangent, root,
arclength, conditioning, and margin threshold.

A pass licenses one wall-free quarter-step replay with the standard plane.  It
does not add a curve point or qualify the historical intersection, uniqueness,
proof, or global topology.

## Result

EXP-396 passes every prospective gate:

```text
local tangent residual = 1.4056470405395967e-16
maximum block defect = 4.008452520993577e-9
arclength residual = 5.33665993340815e-14
minimum singular value = 1.6948986116687517e-9
```

The zero-step corrector converges by gradient tolerance in four evaluations,
holds `c` within `7.01e-9`, and limits normalized node motion to `0.002005`.
All boundary, stationarity, root, tangent, and conditioning checks pass.  The
standard tangent-normal plane is therefore numerically regular and licenses
EXP-397's wall-free quarter-step replay without any threshold change.

Raw receipt: `artifacts/EXP-396/receipt.json`, 79,086 bytes,
SHA-256 `8d4a0a56e471021970df473dd3cd5fc0164e1084222e02fcafbc78882662511c`.
Compact receipt: [`receipts/EXP-396.json`](receipts/EXP-396.json).

Manifest:
[`../../experiments/manifests/EXP-396-jones-homoclinic-local-tangent-standard-plane-control.json`](../../experiments/manifests/EXP-396-jones-homoclinic-local-tangent-standard-plane-control.json).

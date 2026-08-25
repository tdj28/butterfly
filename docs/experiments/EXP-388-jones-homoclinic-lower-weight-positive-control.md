# EXP-388 — Lower-weight homoclinic-plane positive control

Status: executed; passed prospectively

EXP-386 and EXP-387 both land on prospectively imposed forward-`c` walls under
the `0.01` nuisance-weight plane.  The smaller EXP-387 step improves the
matching floor by about one order of magnitude but does not escape the wall.
EXP-388 therefore changes plane orientation without attempting a forward step.

Node, angle, and flight-time weights are reduced from `0.01` to `0.003`; the
physical `a` and `c` weights remain one.  This is a prospective compromise
between the pure physical plane, whose measured minimum singular value was
`2.70368e-10`, and the `0.01` control, whose value was `1.79318e-9`.  In
addition to the unchanged zero-step root, stationary-`c`, arclength, and
interiority gates, EXP-388 requires a final minimum Jacobian singular value of
at least `5e-10`.  Thus a pass must retain a measured conditioning improvement
over the pure plane rather than merely reproduce the orbit.

A pass licenses one forward step with the same `0.003` plane.  It does not add
a curve point, qualify the historical fixed-`a` intersection, establish
uniqueness, or prove the homoclinic connection.

## Result

EXP-388 passes every prospective gate in three evaluations:

```text
(a, c) = (0.1798174973592475, 10.317081491124430)
maximum block defect = 5.108701573712036e-9
arclength residual = -4.0991374706346234e-14
minimum Jacobian singular value = 1.7669731555522209e-9
```

The final `c` drift is `2.38e-9`, inside the unchanged `1e-8` stationary gate.
The minimum singular value is `3.53x` the prospective `5e-10` floor and
`6.54x` the pure physical-plane measurement.  The normalized closing tangent
is `99.96%` physical in squared norm: its node and angle group norms are only
`0.02108` and `0.02090`.

This licenses a forward `2e-5` continuation step under the `0.003` plane.  It
does not add a twelfth branch point by itself.

Raw receipt: `artifacts/EXP-388/receipt.json`, 78,310 bytes,
SHA-256 `bd072349ed698f8d12dd5e6bd233b92296d377d190cd8376ed5d2e5f2953d55e`.
Compact receipt: [`receipts/EXP-388.json`](receipts/EXP-388.json).

Manifest:
[`../../experiments/manifests/EXP-388-jones-homoclinic-lower-weight-positive-control.json`](../../experiments/manifests/EXP-388-jones-homoclinic-lower-weight-positive-control.json).

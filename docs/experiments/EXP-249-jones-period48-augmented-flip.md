# EXP-249 — Exact segmented period-48 flip

Status: completed — failed residual and independent gates

EXP-248 supplies one unambiguous real-`-1` bracket on the primitive period-48
branch. EXP-249 initializes from the exact index-2 nodes and solves the
64-segment orbit plus anti-periodic tangent field as one augmented system at
fixed `(b,c)`, with `a` constrained to that bracket.

The gates require small orbit, phase, tangent, and normalization residuals;
independent Radau closure and a real-`-1` multiplier; exact `56/64` section
identity; and nonclosure at every proper subperiod. A pass supplies the event
and tangent representation for a separately frozen period-96 switch.

Manifest:
[`../../experiments/manifests/EXP-249-jones-period48-augmented-flip.json`](../../experiments/manifests/EXP-249-jones-period48-augmented-flip.json).

## Result

The solve reaches the correct event neighborhood but exhausts 30 evaluations.
Its direct multiplier residual is `2.01e-8` and tangent residual is
`2.14e-10`, but orbit matching plateaus at `3.22e-8`, above the frozen `1e-8`
gate. The resulting long Radau replay fails closure, neutral, and multiplier
gates, so the event is not qualified.

The bracket endpoints are exact, phase-aligned continuation rows. EXP-250
therefore changes only the initial guess to their multiplier-secant node and
period interpolation and raises the evaluation ceiling to 60. All scientific
thresholds and both solvers remain unchanged.

Raw receipt: `artifacts/EXP-249/receipt.json`, 17,642 bytes, SHA-256
`88fdb648b3d924ade9b62ea8935f28f80fe64fd7e9aff40a1619cc810d7e8fb1`.
Compact receipt:
[`receipts/EXP-249.json`](receipts/EXP-249.json).

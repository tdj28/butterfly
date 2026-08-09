# EXP-191 — Second Jones period-6 window atlas

Status: passed as a discovery atlas; the selected component is vertically
truncated

## Question

What is the resolved stable period-6 window surrounding Jones's other exact
period-6 landmark `(a,b,c)=(0.215,0.2,7.6)`?

## Frozen computation

EXP-191 runs the already qualified Float64 GPU atlas kernel on 40,401 points:
`a in [0.21,0.22]` at spacing `5e-5` and `c in [7.4,7.8]` at spacing `0.002`,
with `b=0.2`. It retains the established `dt=0.005`, 2,400-unit transient,
800-unit observation window, historical root-interpolated section, and blind
recurrence classifier through period 32.

The bounds are symmetric around the source coordinate. They resolve the
corresponding EXP-021 atlas pixel by a factor of 50 along each parameter axis.
After execution, the only selected discovery domain is the eight-connected
period-6 component containing the anchor pixel. No word, critical location,
Floquet zero, or expected center enters the classifier or component rule.

Manifest:
[`../../experiments/manifests/EXP-191-jones-second-period6-window-atlas.json`](../../experiments/manifests/EXP-191-jones-second-period6-window-atlas.json).

## Claim boundary

This is a high-resolution single-basin discovery raster. A pass supplies a
bounded domain for identity-safe cycle correction and direct two-critical
optimization. Raster membership alone proves neither continuation nor double
superstability.

## Result

The secure RTX A4500 execution from clean commit `28f3651` completed all
40,401 points with no numerical failures. It classified 3,551 pixels as
periodic, including 1,058 period-6 pixels, at approximately
`1.782e9` state steps per second.

The exact anchor pixel is period 6. Its deterministically selected
eight-connected component contains 981 pixels, spans
`a in [0.2145,0.21555]`, and reaches both sampled `c` boundaries at `7.4` and
`7.8` while touching neither `a` boundary. The experiment therefore passes as
a coherent search-domain discovery but does not capture the full vertical
extent of the component. A wider prospective atlas is required before testing
whether it reaches Jones's first period-6 landmark.

Compact receipt: [`receipts/EXP-191.json`](receipts/EXP-191.json).

![EXP-191 local period atlas](../../artifacts/EXP-191/EXP-191-second-period6-window.png)

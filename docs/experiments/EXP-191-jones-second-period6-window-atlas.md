# EXP-191 — Second Jones period-6 window atlas

Status: preregistered; not yet executed

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

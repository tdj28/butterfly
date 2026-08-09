# EXP-192 — Two-landmark period-6 band atlas

Status: executed; passed numerically; frozen component-membership test is
negative

## Question

Does the eight-connected period-6 raster component anchored at Jones's exact
landmark `(a,b,c)=(0.215,0.2,7.6)` reach the nearest grid point to the other
exact period-6 landmark `(0.21564,0.2,6.124)`?

## Frozen computation

EXP-192 extends the qualified EXP-191 atlas to 92,736 points over
`a in [0.2135,0.2175]` at spacing `2.5e-5` and `c in [5.9,8.2]` at spacing
`0.004`, with `b=0.2`. The first landmark lies exactly on the `c` grid and
`1e-5` from its nearest `a=0.21565` pixel; the second landmark lies exactly on
both axes. Integration and blind recurrence classification are unchanged from
EXP-191.

The selector retains only the eight-connected period-6 component containing
the second landmark and reports the first landmark's nearest-pixel period and
component membership. It uses no symbolic word, return-map critical location,
Floquet target, or expected connection.

Manifest:
[`../../experiments/manifests/EXP-192-two-jones-period6-landmark-band.json`](../../experiments/manifests/EXP-192-two-jones-period6-landmark-band.json).

## Acceptance and claim boundary

The atlas passes numerically when no more than 0.1% of pixels fail integration.
The scientific outcome is the frozen nearest-pixel membership report, whether
positive or negative. Even a positive result establishes only raster
connectivity under one basin seed. Periodic-orbit correction and continuation
are required before calling the landmarks one dynamical family.

## Result

The secure RTX A5000 execution from clean commit `3f42faa` completed all
92,736 pixels without a numerical failure. It classified 26,490 pixels as
periodic, including 4,192 period-6 pixels, at approximately
`2.128e9` state steps per second.

Both landmarks land on period-6 pixels. The second-landmark anchor belongs to
an eight-connected 2,598-pixel period-6 component spanning
`a in [0.2135,0.215775]` and `c in [7.124,8.192]`. The nearest pixel to the
first landmark is `(a,c)=(0.21565,6.124)` and is also period 6, but it is not in
the anchor component. Thus the two source coordinates do not lie in the same
resolved stable period-6 raster component. This does not exclude a subpixel
bridge or continuation through unstable period-6 orbits.

Compact receipt: [`receipts/EXP-192.json`](receipts/EXP-192.json).

![EXP-192 two-landmark period atlas](../../artifacts/EXP-192/EXP-192-two-landmark-band.png)

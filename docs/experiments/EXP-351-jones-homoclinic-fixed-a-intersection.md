# EXP-351 — Direct historical fixed-a homoclinic intersection

Status: frozen; not yet run

EXP-347 and EXP-350 independently qualify two local continuation points and
give successive secant slopes `-0.3255142594` and `-0.3255310084`. The latter
prospectively predicts an intersection with Jones's historical path
`a=0.1798` at `c=10.3171353942`.

EXP-351 is the direct test. It binds the exact passed 128-arc EXP-350 receipt,
holds `(a,b)=(0.1798,0.2)` fixed, and solves for `c` with analytic segment
variational sensitivity. The local `c` box is centered on the frozen secant
prediction with half-width `0.01`; all physical geometry, Radau tolerances,
128-arc segmentation, 40-evaluation budget, and the `1e-8` maximum-block gate
are retained.

Passing qualifies a local intersection of the homoclinic root curve with the
historical fixed-`a` path. It cannot validate Jones's printed
`c=10.3084`, establish uniqueness or completeness, or replace a
computer-assisted proof.

Manifest:
[`../../experiments/manifests/EXP-351-jones-homoclinic-fixed-a-intersection.json`](../../experiments/manifests/EXP-351-jones-homoclinic-fixed-a-intersection.json).

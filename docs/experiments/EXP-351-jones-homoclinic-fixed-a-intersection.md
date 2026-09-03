# EXP-351 — Direct historical fixed-a homoclinic intersection

Status: failed; preserved as the first direct fixed-a correction

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

The frozen local run exhausts 40 evaluations and is preserved as failed. It
reduces the initial maximum block defect from `0.0245206906` to
`0.000209830047`, remains fully interior, and solves to
`c=10.317127477271764`, only `7.91689e-6` from the prospective secant target.
The scientific `1e-8` gate is not relaxed.

Residual localization is informative: 121 of 128 blocks are already below
`1e-8`; five of the seven remaining failures are the final five blocks next
to the nonlinear stable-manifold target. A hash-bound warm restart from these
exact fixed-`a` nodes is therefore preferable to another interpolation or an
immediate global segmentation change.

Raw receipt: `artifacts/EXP-351/receipt.json`, 31,787 bytes, SHA-256
`68f3a15703b6f129ff00239774b1d9d41d216e576ba31057deddd9d2e70fa387`.

Manifest:
[`../../experiments/manifests/EXP-351-jones-homoclinic-fixed-a-intersection.json`](../../experiments/manifests/EXP-351-jones-homoclinic-fixed-a-intersection.json).

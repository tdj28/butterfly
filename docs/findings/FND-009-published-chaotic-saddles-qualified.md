# FND-009 — The published two- and three-branch chaotic saddles are qualified

Status: passed finite-time CPU control reproduction

## Result

EXP-112 passes every preregistered gate at the two regular-window controls from
Barrio, Blesa, and Serrano's Figure 2:

- `a=0.118` has a stable period-4 attractor and a two-branch nonattracting
  chaotic saddle;
- `a=0.149` has a stable period-4 attractor and a three-branch nonattracting
  chaotic saddle.

The result is not based on one long transient or one fitted curve. Fourteen
complete survival ensembles cover three independent scrambled Sobol sequences,
nested sample sizes 4096/8192/16384, RK4 step halving, and later survivor
conditioning. Both section coordinates are evaluated with 15 binning/smoothing
variants and 50 bootstraps per variant. All 420 topology cells return the
expected count with variant consensus `1.0`, for 21,000 bootstrap refits.

## Numerical envelope

| Gate | `a=0.118` | `a=0.149` | Threshold |
|---|---:|---:|---:|
| Maximum survivor-fraction difference | `0.01013` | `0.01135` | `0.05` |
| Maximum across-run normalized critical drift | `0.01485` | `0.01283` | `0.04` |
| Maximum short-horizon scaled state error | `2.07e-6` | `2.46e-6` | `1e-3` |
| Maximum short-horizon time error | `5.53e-7` | `3.15e-6` | `2e-5` |
| Minimum final survivors | `1485` | `884` | `100` |
| Minimum return pairs per coordinate | `12375` | `7438` | `1000` |

No ensemble trajectory fails numerically. At `a=0.118`, the across-run critical
interval is `[-21.72523,-21.44322]` in `y` and
`[0.009532463,0.009536627]` in `z`. At `a=0.149`, the two intervals are
`[-31.27239,-31.08434]` and `[-21.11389,-20.81875]` in `y`, and
`[0.009359465,0.009362804]` and `[0.009542207,0.009547411]` in `z`.

## What is now established

Within the declared finite-time sprinkler construction and published section,
the nonattracting chaotic invariant structure continues through these two
stable windows and has the published two/three branch distinction. The
distinction survives integration, conditioning, sampling, coordinate, spline,
and bootstrap perturbations. This directly closes the first CPU control gate
that the attractor-only EXP-109 could not address.

For the Barrio paper, this is a direct modern reproduction of its two Figure 2
chaotic-saddle controls with substantially more explicit uncertainty and
provenance. For Jones, it strongly supports the shared premise that branch
topology remains dynamically relevant inside regular windows. It also supplies
the previously missing nonattracting set on which a third-branch reinjection
observable can be defined.

## What remains open

Two control points do not establish the global TBA curve, its tangency to every
doubly superstable point, a topological template equivalence, or a complete
parameter-plane explanation. Jones's distinctive claim—that the third branch's
reinjection geometry predicts `p -> p+1` spiral connections—has not yet been
tested.

The immediate corroboration gate is a structurally different PIM-triple or
stagger-and-step saddle trajectory. The engineering gate is Float64 GPU parity
on the same scrambled ensembles. Only after those gates should this sampler be
used to continue a saddle-defined TBA curve through the full `(a,c)` plane.

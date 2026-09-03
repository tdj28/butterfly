# FND-026 — Signed lower-support slope predicts the blind midpoint

Status: prospectively qualified local companion-observable result

## Finding

EXP-129 blindly qualifies the nonattracting saddle at
`(a,b,c)=(0.148125,0.2,20)` as two-branch. Independently of that discrete
critical-point count, the frozen lower-support derivative is negative across
all declared fits, both scalar coordinates, and both censor horizons. Its
calibrated sign therefore predicts the same two-branch class. The finite
sampled bracket narrows to `[0.148125,0.14825]`.

## Evidence

- All eight hash-bound calibration profiles pass before target execution.
- All six target PIM access lines complete and each horizon supplies 2097
  retained return pairs per coordinate.
- All 60 target branch-oracle cells return two; none returns three or
  unresolved.
- All 60 target slope fits are negative. The full normalized intervals are
  `[-1.2032,-0.4994]` in `y` and `[-1.4185,-0.8476]` in `z`; the frozen
  minimum magnitude is `0.1`.
- Maximum combined 128/256 normalized critical-point span is `0.009643` in
  `y` and `0.005037` in `z`.
- The stable period-4 reference passes. There are two certified censored
  selections at 128 returns, none at 256, and no failed lifetime integration.
- The run starts from clean pushed commit `5178607` and completes in
  `4374.08 s`.

## Implication for Jones and the TBA

This is the first held-out evidence that a signed edge observable anticipates
the discrete two/three classification. It directly operationalizes Jones's
statement that at `TTL23` the edge of the second branch becomes the second
critical point: the edge derivative supplies a differential test, while the
critical-to-support distance on the three-branch side supplies a geometric
test.

The local support also separates sharply. At `a=0.148125`, its minima remain
near the two-branch endpoint (`y=-30.4507`, `z=0.00937285`); at the three-branch
`a=0.14825` endpoint they extend to `y=-31.7536`, `z=0.00935025`. This is
consistent with the published closed/open-branch picture, but it does not yet
identify the unstable-orbit or manifold event that opens the branch.

## Limits and next action

The derivative and branch count share PIM states and spline variants, so this
is a predictive companion statistic rather than a second saddle reconstruction.
One parameter midpoint does not prove continuity, a zero, uniqueness, or a
codimension-one curve. The next experiment should leave pure one-dimensional
bisection and perform a transverse `(a,c)` pilot: use the qualified GPU
sprinkler for discovery, bracket the signed branch-opening change at new `c`
values, and validate selected cells with independent adaptive PIM. In parallel,
search the added lobe for the unstable periodic orbit/manifold collision that
could define a smooth event function.

Raw receipt SHA-256:
`d50719b5ec92994bdf5bc0e80cb5dfc850a0d49646f56b3f79962342d5080698`.

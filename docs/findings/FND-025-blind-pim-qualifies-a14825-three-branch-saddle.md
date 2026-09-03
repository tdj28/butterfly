# FND-025 — Blind PIM qualifies `a=0.14825` as three-branch

Status: prospectively qualified finite-horizon invariant-set result

## Finding

EXP-128 independently qualifies the nonattracting saddle at
`(a,b,c)=(0.14825,0.2,20)` as three-branch. No expected label or prior critical
location was encoded. Together with EXP-125's two-branch result at `a=0.148`,
the finite sampled transition bracket narrows to `[0.148,0.14825]`.

## Evidence

- All six fixed PIM access-line constructions complete at the 128- and
  256-return censor ceilings.
- Each horizon supplies 2097 retained pairs in each coordinate.
- Every one of 60 coordinate--horizon--oracle cells resolves as three; none is
  two-branch or unresolved.
- The two critical points persist across horizons. Maximum combined normalized
  span is `0.009043` in `y` and `0.009093` in `z`.
- The stable period-4 cycle and all lifetime integrations pass.
- Horizon 128 uses the already qualified censor rule for 31 censored
  evaluations and 29 certified block selections; horizon 256 has no censor.

## Scientific implication

The identical stable-set-targeting method now gives two branches at `a=0.148`
and three at both `a=0.14825` and `a=0.1485`. This is a second blind
localization step, independent of the transient-domain lifetime mechanism
rejected by EXP-127. It strengthens the local ordering and places the finite
classifier boundary within a width of `0.00025` in `a`.

This is still a bracket, not a continuous TBA curve. Further midpoint
classification has diminishing theoretical value unless paired with an
independent dynamical continuation observable. The next experiment should
freeze a critical-point--to--invariant-support boundary margin across the
qualified bracket and test whether its zero predicts the blind labels.

Raw receipt SHA-256:
`a4aae2dc04b3d0171e9b74bd88cd3a9d79e73cd123715a8f81642d9a0664423e`.

EXP-129 subsequently qualifies `a=0.148125` as two and prospectively matches
that blind count with a negative lower-support slope, narrowing the current
finite bracket to `[0.148125,0.14825]`.

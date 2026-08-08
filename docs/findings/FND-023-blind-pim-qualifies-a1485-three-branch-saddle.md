# FND-023 — Blind PIM qualifies `a=0.1485` as three-branch

Status: prospectively qualified finite-horizon invariant-set result

## Finding

EXP-126 independently qualifies the nonattracting saddle at
`(a,b,c)=(0.1485,0.2,20)` as three-branch. No expected label or prior critical
location was encoded. With EXP-125's two-branch qualification at `a=0.148`, the
finite sampled transition bracket is `[0.148,0.1485]`.

## Evidence

- All six fixed PIM access-line constructions complete at the 128- and
  256-return censor ceilings.
- Each horizon supplies 2097 retained pairs in each coordinate.
- Every one of 60 coordinate--horizon--oracle cells resolves as three; none is
  two-branch or unresolved.
- The two critical points persist across horizons. Maximum combined normalized
  span is `0.014702` in `y` and `0.008531` in `z`.
- The stable period-4 cycle and all lifetime integrations pass.
- The 119 right-censored evaluations and 104 certified selections at horizon
  128 are handled by the rule qualified before midpoint continuation; horizon
  256 has no censor.

## Scientific implication

The change from two branches at `a=0.148` to three at `a=0.1485` is recovered
with the same stable-set-targeting method, access lines, censor horizons,
integrator, coordinates, and oracle. This is the strongest local evidence so
far for the Jones/Barrio-Blesa-Serrano topology transition inside a regular
period-4 window. It is no longer an attractor-pixel observation or a comparison
between differently conditioned sprinkler subsets.

The result localizes a finite classifier boundary; it does not interpolate a
continuous codimension-one TBA curve. Independent continuation of a critical
orbit or stable-set invariant must still connect this bracket through the
parameter plane, and branch-conditioned escape must test the proposed
third-branch reinjection mechanism. EXP-127 has now rejected faster mean
capture for the transient extra branch at `a=0.148` and replaced it with a
delayed-but-bounded capture pattern. This does not alter the PIM bracket; it
does require reinjection tests to use the genuinely three-branch invariant-set
construction rather than the `a=0.148` transient branch.

Raw receipt SHA-256:
`1b2b044e803aed5ba64124305796b6a4847f74c7ef617fcff99270912fd8851a`.

EXP-128 later qualifies `a=0.14825` as three under the same method, narrowing
the current finite bracket to `[0.148,0.14825]`.

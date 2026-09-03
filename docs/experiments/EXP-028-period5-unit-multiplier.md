# EXP-028 — Coupled period-5 nontrivial +1 multiplier solve

> **Identity correction after EXP-047.** The event below is on a fundamental
> period-3 family represented twice, not the period-5 family named in this
> historical title. The solve remains valid; the continuation switched
> families before this event.

Status: executed; passed
Manifest: `experiments/manifests/EXP-028-period5-unit-multiplier.json`
Claim target: EXP-025 through EXP-027 period-5 branch interaction

## Hypothesis and method

The reproducible `+1` crossing near `b=0.272283` is a genuine nontrivial unit
Floquet event rather than interpolation error or accidental selection of the
autonomous flow-neutral multiplier.

At fixed `(a,c)=(0.245,5.1)`, solve simultaneously for the three-component
initial state, flow period, `b`, and a real three-component Floquet vector.
The residual contains flow closure, a phase condition, `(M-I)q=0`, unit-vector
normalization, and orthogonality of `q` to the local flow direction. The last
condition explicitly excludes the ever-present neutral flow mode. The
overdetermined nine-residual/eight-unknown system can vanish only when a second
unit direction is present.

## Acceptance and limits

The event must remain inside the frozen EXP-027 multiplier bracket. Closure,
eigenvector, and flow-orthogonality residuals must each be at most `1e-8`.

Passing locates a nontrivial `+1` event and supplies an event eigenvector for
branch switching. It does not, by itself, determine whether the interaction is
transcritical-like, pitchfork-like, symmetry-related, or nongeneric. EXP-029
must perturb along the event null direction, correct both signs, and continue
every distinct local branch prospectively.

## Result

The clean run at commit `71169b49a2f2ca5bd36a00b487027e118db10d9a`
passed after four nonlinear evaluations. It located the event at
`b=0.2722840597934716`, inside the frozen EXP-027 bracket, with flow period
`33.79007747453978`. Closure was `1.61e-12`, the nontrivial eigen residual was
`5.48e-13`, and flow orthogonality was `1.90e-19`.

The computed multipliers are approximately `0`, `1.000000000000037`, and
`0.999999999915999`. The last two are respectively the autonomous neutral
direction and the independently constrained event direction. The event vector
is `(-0.9999938,-0.0014959,-0.0031955)`. The complete receipt SHA-256 is
`bcd3ffcd261f48298ba58ed1ac1eb08f446bd2d68f6d0a4234cf0155a32a6e54`.

## Decision

The period-5 `+1` event is accepted as a coupled numerical solution, not merely
a linear-interpolation estimate. Its extended phase-conditioned shooting
Jacobian has a second near-zero singular value (`4.64e-11` in the EXP-029
design diagnostic), consistent with a local branch point. This still does not
name the generic bifurcation. EXP-029 prospectively constructs the secondary
null direction, switches in both signs, and attempts local continuation.

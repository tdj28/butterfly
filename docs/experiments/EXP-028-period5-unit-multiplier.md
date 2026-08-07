# EXP-028 — Coupled period-5 nontrivial +1 multiplier solve

Status: preregistered; pending clean local execution
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

# EXP-180 — Local Jones critical track across the branch-birth band

Status: executed; failed one frozen support point

## Question

Does the critical point independently qualified at the EXP-177 unimodal
control persist locally across the global branch-count disagreement band and
land on the higher-coordinate critical of the trimodal endpoint?

## Frozen design

EXP-180 was committed and pushed before execution. It introduced a local
critical oracle whose normalized anchors are the independent EXP-177 critical
midpoints (`x=0.418072127976923`, `z=0.330879856361210`). Every spline variant
selects the nearest prominent critical and bootstraps that local identity
without requiring a stable total critical count. Selection required anchor
distance at most `0.12`, runner-up margin at least `0.15`, all seven variants,
local bootstrap consensus at least `0.8`, and combined normalized span at most
`0.05`.

The experiment used a fresh initial state, 21 DOP853 path points, and Radau
controls at five points. Every local row had to resolve. Adjacent location
steps, solver parity, recurrence, integration, global two/three endpoint
controls, and the endpoint descendant index were independent acceptance gates.

Manifest:
[`../../experiments/manifests/EXP-180-jones-local-critical-track.json`](../../experiments/manifests/EXP-180-jones-local-critical-track.json).

## Result

The clean run at source commit
`ad7a1993534a15a2e54780f08feae89f6dd79220` failed overall. Twenty of 21
DOP853 path points resolve the local critical in all seven variants and both
coordinates. Four of five Radau controls also resolve and agree with DOP853;
the largest finite solver delta is `0.0022638` in x and `0.0015841` in z.

The sole failure is `a=0.156` under both solvers and both coordinates. It is a
support failure, not a competing identity:

- all nominal x variants locate the critical in `0.47419–0.48310`;
- all nominal z variants locate it in `0.36026–0.37598`;
- conditional spread ratios are below `9e-5`; but
- occupied-bin coverage is only `0.14–0.233`, below the frozen `0.70` floor.

Because the local result is unresolved at that row, the full-path local,
adjacent-step, and solver-parity gates fail as designed. Integrations,
recurrence exclusion of periods through 64, and endpoint controls pass.

At `a=0.160`, both solvers and coordinates make the frozen endpoint assignment:

| solver | coordinate | local location | distance to index 1 | runner-up margin |
|---|---|---:|---:|---:|
| DOP853 | `x` | `0.498278` | `0.005144` | `0.416702` |
| DOP853 | `z` | `0.360631` | `0.003908` | `0.316151` |
| Radau | `x` | `0.497527` | `0.005657` | `0.415538` |
| Radau | `z` | `0.360649` | `0.003664` | `0.316402` |

All four select increasing-coordinate critical index 1.

## Interpretation

EXP-180 substantially strengthens the directional identity evidence: the same
locally bootstrapped feature is observed at 20 surrounding DOP853 points, four
independent Radau points, and the trimodal endpoint. It still does not qualify
an uninterrupted attracting-set track because the banded invariant support at
`a=0.156` does not sample enough of the return-map domain.

A retrospective recurrence diagnostic finds no period through 512 and a poor
best lag-28 recurrence, so the hole must not be called a regular window without
further classification. The next identity test should construct a
nonattracting or transient invariant-set cloud that restores domain support at
the frozen gap, or explicitly fail if such a cloud cannot be qualified.

Raw receipt SHA-256:
`54267eba6b911022efd8d493b2fbb2704ef35ab275aeb6ee286e6b444ac3a949`.
Compact receipt:
[`receipts/EXP-180.json`](receipts/EXP-180.json).

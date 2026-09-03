# EXP-178 — Attracting-set Jones critical-identity path

Status: executed; failed one frozen acceptance gate

## Question

Can the single neutral critical point in the two-branch Jones-section regime be
identified with one of the two neutral critical points in the three-branch
regime using a prospective local path rather than distant-endpoint proximity?

## Frozen design

EXP-178 was committed and pushed before execution. It sampled 24 fixed
`(b,c)=(0.2,20)` values over `a in [0.11,0.20]` from the same initial state and
historical negative section used by EXP-176/177. Each point used DOP853, at
least 1000 crossings, seven unchanged branch-oracle variants, and independent
`x` and `z` decisions. Periodic attractors and unresolved oracles were declared
gaps and could not vote.

Identity was evaluated only between the last unanimously resolved two-branch
row and the first unanimously resolved three-branch row. Critical-interval
midpoints were normalized by each occupied scalar domain. Passing required a
nearest-descendant step no larger than `0.12`, a runner-up margin of at least
`0.05`, the same increasing-coordinate descendant index in `x` and `z`, and a
resolved parameter bracket no wider than `0.005`.

Manifest:
[`../../experiments/manifests/EXP-178-jones-critical-identity-path.json`](../../experiments/manifests/EXP-178-jones-critical-identity-path.json).

## Result

The clean run at source commit
`439f0a8b433a32ed5932d385839fc4343541c71c` preserved an overall failure. The
last resolved two-branch point was `a=0.150`; the first resolved three-branch
point was `a=0.160`. The resulting width `0.010` fails the frozen `0.005` gate.
All other global gates pass: both endpoint controls resolve as predicted, no
resolved `x/z` branch-count contradiction occurs, and both coordinates select
the same descendant.

| coordinate | source midpoint | three-branch candidates | selected descendant | step | runner-up margin |
|---|---:|---:|---|---:|---:|
| `x` | `0.474741` | `0.076485`, `0.503190` | `K1` | `0.028449` | `0.369807` |
| `z` | `0.341078` | `0.040420`, `0.364265` | `K1` | `0.023187` | `0.277470` |

The large margins strongly reject the lower-coordinate candidate under the
frozen operational rule. They do not override the failed bracket-width gate.
The intervening `a=0.1525`, `0.155`, and `0.1575` rows are chaotic-looking but
unresolved because oracle variants disagree; earlier period-4 windows are also
retained as gaps.

## Interpretation

This is positive directional evidence for Jones's symbolic reconstruction:
the unimodal critical point locally continues to the higher-coordinate
three-branch critical point in both observables. It is not yet a qualified
identity result. EXP-179 therefore increases sample power and path resolution
inside the failed bracket without changing any oracle, identity, or acceptance
threshold.

Raw receipt SHA-256:
`4817dc6d9fd7a027d36560453816140cb05dbae912cf153a8c3eed9ddf2d3133`.
Compact receipt:
[`receipts/EXP-178.json`](receipts/EXP-178.json).

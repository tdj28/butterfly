# EXP-177 — Two-branch control on the recovered Jones section

Status: executed; passed

## Question

Does the parameter point reported as unimodal by Barrio, Blesa, and Serrano,
`(a,b,c)=(0.11,0.2,20)`, also support a two-branch neutral operational
partition on the distinct recovered Jones negative half-plane?

## Frozen design

The experiment was committed and pushed before execution. It copied the
successful EXP-176 solver, 16000-unit observation, 1000-pair calibration
segment, 200-pair guard gap, 1000-pair held-out validation segment, seven
oracle variants, 100 bootstraps, and every acceptance threshold. Only the
parameter point, expected branch count, and neutral partition cardinality
changed. The prediction was two branches in both `x` and `z`; no equivalence of
the Jones and Barrio sections was assumed.

Manifest:
[`../../experiments/manifests/EXP-177-jones-section-two-branch-control.json`](../../experiments/manifests/EXP-177-jones-section-two-branch-control.json).

## Result

The clean run at source commit
`49f9e9495b161b3d8746891dea28db25a0a5a0c6` succeeded with 2582 accepted
crossings. Every one of the seven variants resolved two branches in both
segments and both coordinates; every variant consensus is `1.0`.

| coordinate | domain | `K0` interval | maximum normalized joint span |
|---|---|---|---:|
| `x` | `[-26.7453239482,-10.7565020831]` | `[-20.1570308584,-19.9646554761]` | `0.0120319` |
| `z` | `[0.00427961170,0.00650506807]` | `[0.00499343296,0.00503850780]` | `0.0202542` |

Both joint spans clear the unchanged `0.04` gate. The result remains neutral:
increasing-coordinate branches are `B0/B1`, the critical interval is `K0`,
and `historical_mapping` is `null`.

## Interpretation

DEC-014's dense two- and three-branch control pair is now qualified on the same
negative-oriented historical representation, independently in both scalar
coordinates. This is stronger than assuming the section declared by Barrio is
interchangeable with the recovered Jones section.

The endpoint controls do not identify which three-branch critical interval is
the continuation of the unimodal `K0`. That identity must be tracked across
parameter space, including regular gaps via an invariant-saddle cloud, before
neutral critical labels can be renamed `C/D`. No Figure 6 word or transition
is yet qualified.

Raw receipt SHA-256:
`37a19c52715792553f7a61383bd4df9172080ffbfc965a41b1dc601daf10228f`.
Compact receipt:
[`receipts/EXP-177.json`](receipts/EXP-177.json).

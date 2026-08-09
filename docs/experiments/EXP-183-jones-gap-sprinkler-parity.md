# EXP-183 — Statistical parity for the Jones support-gap survivor cloud

Status: executed; passed

## Question

Does the survivor-cloud critical recovered at `a=0.156` survive a factor-two
RK4 step refinement, attractor false-negative controls, and a meaningful
short-horizon DOP853 trajectory audit?

## Frozen design

EXP-183 is the scientifically unchanged successor to EXP-182's pre-manifest
launcher failure. It was committed and pushed before execution. The same
8,192 initial states, independent DOP853 attractor clouds, capture rule,
midpoint window, seven local oracle variants, and physical flank predictions
were run at RK4 steps `0.01` and `0.005`.

Both profiles had to resolve the local critical in x and z. Their checkpoint
survivor fractions could differ by at most `0.02`; their physical critical
locations could differ by at most `0.8` in x and `0.00012` in z. All 128
validation-attractor seeds had to capture by time 100 at both steps. Five
declared seeds also had to match DOP853 over their first five returns within
scaled state error `0.001` and event-time error `2e-5`. No long-time chaotic
trajectory identity was required.

Manifest:
[`../../experiments/manifests/EXP-183-jones-gap-sprinkler-parity.json`](../../experiments/manifests/EXP-183-jones-gap-sprinkler-parity.json).

## Result

The clean run at source commit
`a962cd2a55fcc08ce1ef6ef5674bc5aeba4a5888` passes every gate in `117.74`
seconds.

| quantity | RK4 `dt=0.01` | RK4 `dt=0.005` | comparison |
|---|---:|---:|---:|
| final survivors | 7552 | 7689 | maximum checkpoint fraction difference `0.016724` |
| return pairs per coordinate | 64,571 | 65,731 | both above 1000 |
| x critical | `-18.5765441` | `-18.5759583` | difference `0.000585813` |
| z critical | `0.00518224715` | `0.00518247038` | difference `2.23230e-7` |
| attractor survivors at time 75 | 0/128 | 0/128 | both pass |

All fourteen profile-coordinate local decisions resolve across all seven
variants. Their normalized location spans are at most `0.020321`. The x
critical misses the frozen flank prediction by only `0.001203` and `0.000618`;
the z errors are `8.17e-7` and `5.94e-7`. Global branch count remains
variant-dependent and is not promoted.

All five short-horizon audits provide five comparisons. The maximum scaled
state error is `4.47266e-7`, and the maximum event-time error is
`2.29186e-6`, far below the frozen gates.

## Interpretation

EXP-183 closes EXP-180's sole local-support hole under the declared finite
survivor-cloud definition. Combined with the 20 surrounding attracting rows,
two-solver controls, and four endpoint assignments, it qualifies the local
operational identity: the unimodal critical continues to the
higher-coordinate critical of the three-branch partition.

This is not a global TBA curve, a stable/unstable manifold proof, or an
assignment of Jones's historical `C/D` and numeral alphabet. The global
shallow-critical birth remains deliberately unresolved by the variant matrix.
Those are the next independent gates.

Raw receipt SHA-256:
`a1898e9a942bc7a15d0dbffb3c3833be33bc8b9d5eca7be85d61929334f8d4f3`.
State artifact SHA-256:
`7c7640a0c2632bd74ff866970d673b3e087d1d2737f4a3b03645fbe409b10ea6`.
Compact receipt:
[`receipts/EXP-183.json`](receipts/EXP-183.json).

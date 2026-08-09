# EXP-174 — Blind Figure 6 landmark classification

Status: executed; strict profile-stability gate failed, late-time solver parity passed

## Question

What recurrence labels and fundamental periods are present at the ten
approximate parameter landmarks printed in Jones Figure 6 when the coordinates
are evaluated exactly as printed, without supplying expected words or periods?

## Frozen design

The manifest binds the source transcription by SHA-256 and loads its ten
parameter triples in printed order. It deliberately contains no expected
periods, landmark-to-word associations, or local search radius.

Two initial states are tested. DOP853 must return the same recurrence signature
after 800- and 1600-time-unit transients. At the longer profile, independent
Radau must return the same signature. Both profiles collect up to 160 crossings
on the recovered Jones half-plane and test the smallest period through 16 using
six repeated blocks. Every integration must contribute at least 96 crossings.

The experiment passes its numerical gate only if all integrations succeed and
the solver/profile comparisons agree. A consistently unresolved landmark is a
valid scientific outcome because the printed coordinates are explicitly
approximate. Initial-condition disagreement is reported rather than coerced
into one label.

## Claim boundary

EXP-174 is reconnaissance for the Figure 6 target. It cannot validate a
symbolic partition, Jones word, `p -> p+1` arrow, caustic, mutant-shrimp
connection, or homoclinic mechanism. No parameter refinement is permitted in
this experiment.

## Result

All 60 integrations succeed and meet the crossing-count gate. At the qualified
1600-unit transient, DOP853 and Radau agree for every landmark and both initial
conditions. Eight exact printed coordinates resolve periodically:

| `(a,b,c)` | Qualified period |
|---|---:|
| `(0.21888,0.2,5.816)` | 5 |
| `(0.21564,0.2,6.124)` | 6 |
| `(0.204,0.2,7.22)` | 8 |
| `(0.20676,0.2,7.18)` | 14 |
| `(0.215,0.2,7.6)` | 6 |
| `(0.199,0.2,7.9)` | 5 |
| `(0.19368,0.2,8.456)` | 14 |
| `(0.2013,0.2,7.55)` | 14 |

The exact printed coordinates `(0.190,0.2,8.9)` and
`(0.18696,0.2,9.38)` remain unresolved under both solvers and both initial
conditions. They are not coerced into chaos or a nearby period label.

The full frozen gate fails for one informative reason. At
`(0.19368,0.2,8.456)`, the second initial state is unresolved after the
800-unit transient but reaches the same period-14 attractor as the other
initial state after 1600 units; Radau independently confirms it. The failed
early/late profile comparison is retained as delayed-capture sensitivity.

Compact receipt: [`receipts/EXP-174.json`](receipts/EXP-174.json). Raw receipt
SHA-256: `521cc4d4e459109f88a26a59c2ca7f0dc7a8c663b84efc8b39b8e82493ad1fc5`.

# EXP-181 hits the gap prediction but fails capture parity

Date: 2026-08-07

EXP-181 executed from pushed clean commit
`b6cb854a9f8fd9fc7e536eecce04a7be7b0d1870`. The raw receipt and state
artifact are frozen at SHA-256
`6b59c47d75d0c14fbe6ad46c3e601def0ca695c7472e8efe9d8ef0e83df5905b`
and `23fb0dc5914d7933f3da16cc97935b5ce5d2f9eabd5f5d3df8fc3cd55916fd7c`.

The 64,571-pair x/z survivor clouds pass every local critical variant and land
within `0.001203` and `8.17e-7` of the frozen physical predictions. The strict
experiment remains failed because its inappropriate long-time pointwise
capture audit achieves only 62.5% agreement. The successor will copy
EXP-113's validated parity logic: compare survival statistics and critical
geometry across step sizes, and compare DOP853 trajectories only before
chaotic decorrelation.

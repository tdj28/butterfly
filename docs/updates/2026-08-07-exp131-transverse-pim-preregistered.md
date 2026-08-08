# Update — EXP-131 transverse PIM endpoints preregistered

EXP-130 showed exactly where GPU sprinklers stop being a claim-bearing saddle
oracle. EXP-131 now transfers the qualified adaptive-DOP853 PIM construction
to the four prospectively selected endpoints at `c=19.8/19.9`.

The test freezes both endpoint branch predictions and signed lower-support
predictions before any PIM target is generated. Passing all four endpoints
would provide the first two finite transverse saddle-topology brackets. It
would not yet establish a continuous TBA curve; a 256-return replication and
an orbit/manifold continuation condition would remain mandatory.

## Result checkpoint

The clean `2eddd2f` run fails its strict gate without any integration or PIM-
access failure. The `c=19.9,a=0.150` endpoint passes as three/positive. Both
`a=0.145` lower endpoints are 12/15 two-branch with negative slopes and only
coverage-censored remainders. The key `c=19.8,a=0.148` prediction is
prospectively falsified: it is predominantly two-branch and all 30 signed
slopes are negative. This displaces the candidate boundary toward larger `a`
at `c=19.8`; it does not establish a curve.

The next frozen experiment will use the 256-return horizon and the independently
qualified EXP-121 censor rule to test `[0.148,0.150]` at `c=19.8` and
`[0.145,0.150]` at `c=19.9`.

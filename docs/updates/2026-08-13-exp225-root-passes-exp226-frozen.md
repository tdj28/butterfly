# EXP-225 localizes the crossing; EXP-226 is frozen

DOP853 and Radau independently place the offset-path parent flip at
`c=7.62537830`, agreeing to `3.96e-9`. The left primitive child and DOP853
right double-cover controls pass. Only the singular redundant-period Radau
Newton correction prevents the global gate from passing.

EXP-226 keeps all numerical points and thresholds and audits the Radau double
cover by correcting the fundamental parent and integrating exactly `2T`.

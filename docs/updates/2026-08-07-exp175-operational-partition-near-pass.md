# EXP-175 operational-partition near-pass

Date: 2026-08-07

EXP-175 executed from pushed clean commit
`aefee0f35676f6131234ff81de3431ad03514e70`. The 1370-crossing run cleanly
qualified a neutral three-branch `x` partition on independent calibration and
validation segments. Calibration `z` also passed, but held-out `z` failed the
strict all-variant gate when the 50-bin bootstrap consensus reached only
`0.64`; the other six variants resolved three branches and no contradictory
count appeared.

The failed raw receipt is preserved at SHA-256
`18014be724884e1c9335ff28c4e8f433918b1839a4f8edb5c33f98fc3669621c`.
This is not being relabeled as a pass and does not permit Figure 6 word
assignment. EXP-176 is the unchanged-threshold power successor: a fresh initial
condition, 1000 calibration pairs, a 200-pair guard gap, and 1000 validation
pairs.

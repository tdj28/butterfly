# EXP-155 schedule correction frozen

Date: 2026-08-07

EXP-154 reached the reported hub coordinate and passed every scientific gate but produced one
extra row, so its formal result is false. The defect duplicated the seed after
putting a below-seed Radau checkpoint into the upward schedule. The raw failed
receipt is preserved.

EXP-155 freezes a direction-aware schedule correction with all 118 scientific
targets and all numerical gates unchanged. This is an administrative successor,
not a retuned scientific test.

The clean successor passes. It verifies the same one-winding family from
`c_H+0.001` through the reported hub coordinate, recovers the square-root amplitude exponent
`0.5017311`, brackets a first `-1` multiplier crossing, and passes all six
Radau checkpoints. The finite hub orbit remains `10.031` units from the
equilibrium, so the homoclinic connection is still a distinct open problem.

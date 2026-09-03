# EXP-189 freezes all period-6 zero-edge candidates

The direct two-critical program begins with a deterministic candidate set.
EXP-189 selects every one of EXP-188's 65 adjacent signed-Floquet zero edges,
interpolates each crossing, and independently corrects its period-6 orbit.

There is no best-candidate selection at this stage and no symbolic input. At
least 60 stable, identity-safe corrections are required before the GPU
survivor reconstruction is allowed to rank the two explicit critical-to-orbit
residuals.

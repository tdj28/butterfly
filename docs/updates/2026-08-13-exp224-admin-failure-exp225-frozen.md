# EXP-224 is administratively unresolved; EXP-225 is frozen

EXP-224 produces no receipt because its closest left Radau control is too
ill-conditioned for the frozen nonlinear-corrector success rule. This is not a
scientific rejection.

EXP-225 retains the same two-solver root and all scientific gates, moves only
the bilateral controls from `5e-5` to `1.5e-4` in `c`, and makes future
qualification exceptions receipt-visible.

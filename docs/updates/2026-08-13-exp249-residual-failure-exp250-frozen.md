# EXP-249 stalls above tolerance; EXP-250 is frozen

The first 64-segment augmented solve reaches a direct multiplier residual of
`2.01e-8`, but its orbit residual plateaus at `3.22e-8` and the long Radau
replay fails. EXP-249 is retained as failed.

EXP-250 freezes the standard bracket-secant initial guess using both exact,
phase-aligned endpoint node sets. Only the seed and evaluation ceiling change;
all scientific and independent-solver gates are identical.

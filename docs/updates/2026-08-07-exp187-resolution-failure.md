# EXP-187 preserves a coarse-mesh resolution failure

EXP-187 stops after five evaluated cells because only the exact seed satisfies
every preregistered continuation gate. The neighboring orbit corrections are
mostly numerically excellent, but their parameter steps are too large for the
frozen whole-orbit identity threshold. No quadratic saddle fit, refinement,
word, or Figure 6 target is evaluated.

The signed multipliers nevertheless bracket zero twice along the first a
stencil: `-1.37298`, `+0.219271`, `-0.523691`. This is precisely the kind of
sub-cell structure the coarse grid could miss. The unchanged-objective EXP-188
successor will use steps `0.00005` in a and `0.0025` in c over only that failed
coarse cell, retaining all center-selection and independent-solver gates.

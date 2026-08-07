# DEC-002 — Use multiple shooting for high-period cascade continuation

Status: adopted after EXP-078

Full-period single shooting remains accepted through the period-160 parent and
the 160→320 Floquet event. It is not accepted for switching the doubled
period-160 orbit: EXP-078 misses the frozen singular-value gate by nearly an
order of magnitude and returns only parent-sheet solutions.

For doubled durations near `2092` and above, build a segmented matching system
with independent node states, cyclic continuity equations, total duration,
parameter sensitivity, and one phase condition. First audit its residual and
singular spectrum against segment counts. Then implement a multiple-shooting
pseudo-arclength corrector and validate it by reproducing a lower-period switch
before retrying period 320.

Remote compute should parallelize independent segment-count, tolerance, and
parameter tasks. A GPU is not assumed beneficial for the sparse nonlinear
solve until profiling identifies a batchable integration or linear-algebra
kernel.

EXP-079 validates this decision quantitatively: 32 segments reduce the event's
smallest singular value from `7.75e-7` to `9.07e-10` (factor `854`) while
retaining `1.25e-9` matching residual. Proceed with the block corrector; do not
return to full-period predictor tuning at this rung.

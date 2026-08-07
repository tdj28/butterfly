# EXP-085 — Multiresolution phase identity for period 320

Status: preregistered after EXP-084; pending clean execution

Repeat the continuous segmented-orbit comparison from EXP-084, but replace the
invalid unimodal scalar minimizer with five deterministic grid refinements.
Each stage evaluates 129 points across one current half-width on either side of
the best phase, selects the global subgrid minimum, and reduces the next search
to one grid spacing. Starting from the frozen 256-point coarse search, the
final phase spacing is below `4e-12`.

All scientific gates remain unchanged: phase-aligned RMS `<=1e-5`, segment
endpoint error `<=1e-8`, period difference `<=1e-8`, stable modulus `<=0.999`,
and lower-period block-Floquet calibration error `<=1e-5`. The full refinement
history is retained whether the identity hypothesis passes or fails.

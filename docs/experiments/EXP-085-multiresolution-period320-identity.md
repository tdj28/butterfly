# EXP-085 — Multiresolution phase identity for period 320

Status: executed; passed

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

The clean run at `d4779509a4460ca2943d5f7b4e523917847668ea` passed. The
five-stage search resolves the phase offset to `0.5000000198306`; whole-orbit
RMS falls from the coarse `3.17e-4` to `1.19e-8`. Maximum segment endpoint
error is `5.99e-11`, the two fixed-parameter periods differ by `2.27e-11`,
and their calibrated dominant nontrivial moduli are `0.05496991` and
`0.05496954`. Full receipt SHA-256:
`cdd49f2a46bf659e3c54e64cd8da0cb303fce3e55191f0f0ce7e59373d47810f`.

Together EXP-082, EXP-083, and EXP-085 establish that the 160→320 switch
produces one geometrically identified, strongly stable period-320 child below
the event. The sixth local supercritical cascade rung is numerically closed.

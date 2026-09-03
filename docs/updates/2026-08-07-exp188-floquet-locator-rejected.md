# EXP-188 rejects a Floquet-only center locator

EXP-188 repairs the coarse continuation scale and qualifies 289 period-6
cells, but it fails the frozen coverage and saddle-refinement gates. The local
surface has 65 sign-changing edges rather than one clean transverse pair. Its
only coarse saddle candidate disappears under the first fully valid `5 x 5`
refinement.

The result redirects rather than weakens the program. A period multiplier
combines every orbit phase, so zero alone cannot identify which of the two
critical points generated a superstability curve. The next experiment will
retain the word-blind policy but compute two explicit survivor-derived
critical-to-orbit residuals, using GPU acceleration across the 65 frozen zero-
edge candidates where it is useful.

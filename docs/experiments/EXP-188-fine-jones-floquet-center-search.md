# EXP-188 — Fine period-6 Floquet-center search

Status: preregistered; not yet executed

## Administrative change from EXP-187

EXP-187 evaluated only the exact center and its four immediate neighbors. The
center passed, three neighbors corrected with sub-`5.33e-13` closure but
violated the local whole-orbit identity scale, and the fourth failed
correction. Its mandated stop rule prevented the saddle search. The signed
multiplier nevertheless changed from negative to positive to negative along
the a stencil, showing that the requested surface varies within one coarse
cell.

EXP-188 changes only the search resolution, bounds, experiment identifier, and
provenance. Its `0.00005` a and `0.0025` c steps are exactly ten times finer;
the `21 x 21` bounds span only the central cell of EXP-187. The seed, period,
continuation ordering, identity threshold, signed-Floquet observable,
quadratic saddle-zero rule, candidate ranking, three refinement factors,
DOP853/Radau validation ring, and every scientific threshold are unchanged.

No Figure 6 word, alphabet symbol, or landmark-to-word association enters the
runner or manifest.

Manifest:
[`../../experiments/manifests/EXP-188-fine-jones-floquet-center-search.json`](../../experiments/manifests/EXP-188-fine-jones-floquet-center-search.json).

## Claim boundary

A pass nominates an intersection-like period-6 Floquet center. It does not
establish doubly-superstable critical membership. A fresh survivor-derived
two-critical test remains mandatory before word encoding.

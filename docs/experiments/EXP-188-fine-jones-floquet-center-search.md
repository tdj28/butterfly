# EXP-188 — Fine period-6 Floquet-center search

Status: executed; failed coverage and saddle-refinement gates

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

## Result

The clean run at source commit
`b10642e6e6952ff2afc29e57b3159524339eb704` evaluates 319 cells and accepts
289, so the tenfold mesh repairs the first-step continuation failure. Every
valid correction closes below `5.19e-12`; 181 have stable transverse modulus
below one. The frozen coarse-coverage gate nevertheless fails at `0.655329`
against the required `0.75`.

The signed surface contains 67 positive and 222 negative cells, 65 adjacent-
cell sign crossings, and 17 cells with multiplier magnitude below `0.02`.
This is substantially more folded than a single clean pair of crossing zero
curves. One preliminary quadratic stencil has four sign changes near
`(a,c)=(0.2151826902,6.1070846923)`, but its fitted stationary multiplier
`-0.0112034` and RMS `0.00686797` already exceed the final `0.005` gates. Its
fully valid `5 x 5` half-step refinement spans multipliers
`[-0.0175944,0.0226967]` yet contains no qualifying stationary saddle. The
mandated refinement stop therefore leaves no selected candidate and no Radau
validation ring.

Raw receipt SHA-256:
`8a66371f14a0c2507ad409a66069d098a8d7e0a409049db55dc4cf009e5fd5b3`.
Compact receipt: [`receipts/EXP-188.json`](receipts/EXP-188.json).

## Claim boundary

A pass would have nominated an intersection-like period-6 Floquet center.
EXP-188 does not. It rejects this local Floquet-saddle locator, not the
existence of a doubly-superstable center: a period-p multiplier can vanish on
multiple phase/critical sheets, so its zero set is not a unique identifier.
The next search must measure both critical-to-orbit residuals directly. It does not
establish doubly-superstable critical membership. A fresh survivor-derived
two-critical test remains mandatory before word encoding.

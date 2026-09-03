# FND-060 — The period-6 Floquet zero surface does not uniquely locate the center

Status: tested local locator rejected; doubly-superstable claim still open

EXP-188 resolves 289 period-6 orbit cells with closure below `5.19e-12`, fixing
EXP-187's immediate continuation-scale failure. The signed dominant transverse
multiplier surface is not a simple pair of zero curves: it contains 65
adjacent sign crossings and 17 near-zero cells in the frozen neighborhood.

One coarse stencil satisfies the four-sign-change saddle screen, but its fit
already misses the declared stationary-value and RMS gates. More importantly,
its fully resolved `5 x 5` refinement contains no stationary saddle candidate.
Coverage is `0.655329`, below `0.75`, so both the coarse and refinement gates
fail and independent Radau validation is never invoked.

This negative result does not reject the Jones/Barrio doubly-superstable
geometry. It rejects using a stationary zero of the full period multiplier as
a unique local proxy. A period-p multiplier is a product over orbit phases and
can vanish whenever any phase encounters either critical, producing multiple
zero sheets. The scientifically sharper search is the one stated in the
source definition itself: independently reconstruct both return-map criticals
and minimize their two separate distances to the corrected periodic orbit.

Evidence: [`../experiments/EXP-188-fine-jones-floquet-center-search.md`](../experiments/EXP-188-fine-jones-floquet-center-search.md).

# FND-059 — The first Floquet-center mesh is too coarse

Status: resolution failure; center claim not evaluated

EXP-187 attempts a word-blind search for the period-6 intersection geometry
expected at a doubly-superstable center. Its exact seed passes, but the first
`0.0005` a and `0.025` c continuation steps violate the preregistered scaled
whole-orbit identity gate. One negative-c step also fails periodic correction.
The mandated stop rule leaves only one valid cell and prevents any saddle fit.

This is not evidence against a center. Three neighbor corrections retain six
returns and close below `5.33e-13`. Their signed dominant multipliers are all
negative, whereas the seed is positive: `-1.37298`, `+0.219271`, and
`-0.523691` along the a stencil, with `-3.59710` on the positive-c neighbor.
The surface can therefore cross zero more than once inside one failed coarse
cell. That structure makes finer identity-preserving continuation necessary.

EXP-188 is allowed to change only the mesh scale and provenance: it shrinks
both steps tenfold and restricts the bounds to the failed EXP-187 center cell.
The signed-Floquet objective, saddle-zero rule, refinements, solvers, and
scientific thresholds remain unchanged.

Evidence: [`../experiments/EXP-187-jones-floquet-center-search.md`](../experiments/EXP-187-jones-floquet-center-search.md).

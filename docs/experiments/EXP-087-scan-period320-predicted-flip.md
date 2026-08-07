# EXP-087 — Scan the predicted period-320 flip

Status: preregistered after EXP-086; pending clean execution

Continue one independently qualified EXP-083 period-320 representation through
nine frozen `b` values from `0.1797132` to `0.1797122`, densely sampling the
EXP-086 prospective 320→640 prediction `0.1797124942943`. At every point use
32-segment fixed-parameter correction and the block-cyclic Floquet operator.
Raise each cluster of block roots to the 32nd power to retain the sign of the
full-orbit multiplier as well as its modulus.

Pass only if every correction has matching residual `<=1e-8`, every orbit
remains distinct from its half-period parent by node RMS `>=1e-5`, and a real
`-1` crossing is bracketed within width `2e-7` and midpoint error `2e-7` of the
frozen prediction. Passing creates a prospective refinement bracket; it does
not establish period 640 until branch switching and independent qualification
also pass.

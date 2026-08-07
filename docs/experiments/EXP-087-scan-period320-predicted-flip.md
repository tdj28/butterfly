# EXP-087 — Scan the predicted period-320 flip

Status: executed; passed

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

The clean run at `bf4661d9dfeb73da8e3e4729bd62551e68e3a281` passed. All
nine corrections have matching residual below `1.01e-12`. The real dominant
multiplier changes from `-0.99066886` at `b=0.17971250` to `-1.06854231` at
`b=0.17971245`. The bracket width is `5e-8`, and its midpoint misses the
frozen EXP-086 prediction by only `1.93e-8`. Full receipt SHA-256:
`1351d98012678006f951e1480f214197a66abaeffa07fdecaecdf3288d12ecd4`.

EXP-088 binds the full scan and refines the signed `-1` residual before any
period-640 branch switch is attempted.

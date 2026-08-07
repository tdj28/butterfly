# EXP-052 — Switch the true period-5 flip to period 10

Status: executed; failed full-arm identity gate

Represent the verified period-5 parent over twice its fundamental period, where
the `-1` multiplier becomes `+1`. Use the doubled shooting null space to switch
both coordinate directions and continue 16 steps. Require ten points per arm,
orthogonal primary/secondary tangents, nontrivial separation from the doubled
parent, closure below `1e-8`, and ten section intersections per accepted child
traversal. Passing recovers a candidate period-10 branch; phase-invariant arm
identity and stability exchange remain separate tests.

The clean run at `2957c10181fc64b73998c072983ce77392002fb1` corrected
16/16 points on both arms, with tangent dot zero, closures below `4.22e-12`,
and endpoint distances `0.1080` and `0.1396`. It nevertheless failed: only the
first 10 and 11 points retain ten section crossings; farther along, the smooth
stable closed orbit has eleven. Receipt SHA-256:
`201960219e3fc8b396fccabfcfcd6b95e500fc9b9a0677e8dcc1f33855af4fb7`.

Retain EXP-052 as failed. The qualifying ten-crossing prefixes are sufficient
for a prospective local branch-identity/stability test. The later 10-to-11
change is tracked separately as a candidate section-topology transition.

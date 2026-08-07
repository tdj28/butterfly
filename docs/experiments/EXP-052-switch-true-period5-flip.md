# EXP-052 — Switch the true period-5 flip to period 10

Status: preregistered after EXP-051; pending clean execution

Represent the verified period-5 parent over twice its fundamental period, where
the `-1` multiplier becomes `+1`. Use the doubled shooting null space to switch
both coordinate directions and continue 16 steps. Require ten points per arm,
orthogonal primary/secondary tangents, nontrivial separation from the doubled
parent, closure below `1e-8`, and ten section intersections per accepted child
traversal. Passing recovers a candidate period-10 branch; phase-invariant arm
identity and stability exchange remain separate tests.

# EXP-178 critical-identity path frozen

Date: 2026-08-07

With neutral two- and three-branch endpoint controls now qualified on the same
historical representation, EXP-178 freezes a prospective attracting-set scan
over `a in [0.11,0.20]` at `(b,c)=(0.2,20)`. Periodic attractors and unresolved
oracles remain explicit gaps.

Identity is tested only across the last unanimously resolved two-branch row
and first unanimously resolved three-branch row. Critical-interval midpoints
are normalized by their occupied scalar domains. A descendant must lie within
`0.12`, beat the other candidate by at least `0.05`, occur across an `a` bracket
no wider than `0.005`, and have the same increasing-coordinate index in `x`
and `z`. This local operational rule is frozen before the path is run. It does
not establish a global TBA curve or map branch numerals.

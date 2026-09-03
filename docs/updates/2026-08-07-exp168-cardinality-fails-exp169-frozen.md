# EXP-168 cardinality fails; unchanged-gate EXP-169 frozen

Date: 2026-08-07

EXP-168 finds a real `-1` bracket between `c=4.708476891711592` and
`c=4.711572660267806`, but fails overall because the bracket occurs so early
that its four-post-bracket stopping rule produces only seven points against a
frozen minimum of twelve. This is an administrative cardinality failure, not
an identity failure: closure, eight windings, half-period nonclosure, two
Radau identities, and multiplier parity all pass by wide margins.

EXP-169 preserves every solver and acceptance threshold, including the
twelve-point minimum. It changes only `post_bracket_points` from four to ten,
forcing the run to collect more evidence after the already observed crossing.
The EXP-168 failure remains immutable and is not reclassified as a pass.

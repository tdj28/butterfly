# Why a converged equation is not always a symbolic turning point

This distinction matters for Jones's symbolic chains: the letters C and D
must refer to actual turning points of the declared scalar return relation,
not merely to places where a numerical equation returns zero.

## The small piece of calculus behind the check

Suppose a curve on the section is labeled by a parameter u. Its scalar input
and next-return output are X(u) and Y(u). If X'(u) is nonzero, the local graph
Y = F(X) has slope

\[
F'(X(u)) = \frac{Y'(u)}{X'(u)}.
\]

A candidate turning point therefore needs Y'(u) = 0 **and a regular input
coordinate**. For a nondegenerate quadratic turning point, the derivative
changes sign across it. Solving only the numerator equation loses the
denominator condition. In computation we also need enough input-curve gain
to resolve that denominator reliably. A tiny denominator is a conditioning
problem, not permission to interpret a noisy ratio as zero.

Compare two exact examples:

| Parameterized relation | At u = 0 | Actual scalar graph |
| --- | --- | --- |
| X = u, Y = u² | X' = 1, Y' = 0 | F(X) = X²: a genuine turning point |
| X = u², Y = k u², k > 0 | X' = Y' = 0 | F(X) = kX on X >= 0: a straight line, not a turning point |

The second example can satisfy a zero-output-derivative equation while both
neighboring scalar slopes remain k. The input parameter doubles back along a
straight graph. Calling this a critical symbol would be a classification
mistake. These examples are algebraic controls, not substitutes for flow
calculations or models fitted to the observed failure.

There is an equally important converse: if X = εu and Y = (εu)² with tiny
positive ε, the graph is still F(X) = X², but this parameterization may fail a
numerical gain threshold. **Failure to qualify a representation does not
prove that the physical turning point does not exist.** Improving branch
tracking or parameterization is different from relaxing the threshold.

## What the Rössler computation actually found

The complete [EXP-509 raw replay](../updates/2026-09-09-exp509-failed-predictor-replay.md)
shows that the failed EXP-508 depth-8 candidates reached their Newton equation
tolerances. Nevertheless, their measured center input gains were about
1.40e-12–2.39e-11, below the unchanged 1e-4 qualification threshold; neighboring
scalar slopes were approximately +0.28447 on both sides. The code correctly
refused to qualify these roots as folds. A separate controller bug then
crashed while reporting that refusal; its repaired replay preserves rejection.

These finite-precision observations do not establish exactly zero gain or
an exactly singular physical return map. “Collapsed input curve” here means
almost no resolved input displacement in the chosen parameterization, not
that trajectories or the attractor physically collapse to a point.

The shorter-history representations at the same endpoint qualify as folds,
but miss the required full-state contact tolerance. The audited
[EXP-510 smaller-step test](../updates/2026-09-09-exp510-four-substep-fold-transport.md)
qualifies all representations at its first substep, then reproduces the
input-regularity failure at its second. That recipe is insufficient; direct
curve coverage and root-isolation checks are the next diagnostic, not a
relaxed gain threshold. Neither result proves that no other qualified branch
or better-conditioned parameterization exists.

## Implication for Jones

This rejects our attempted numerical identification, not Jones's paper.
Verifying a flow-level chain still requires a declared return relation,
qualified critical points, correspondence to the corrected primitive orbit,
and the proposed transition to the next symbolic word. A converged root or
an attractive scalar plot alone establishes none of that chain.

The unchanged implementation enforces input regularity through
`observe_curve` and connected sign-change brackets through
`candidate_intervals`. The exact examples above have direct, no-IVP controls
in `tests/test_critical_point_regularity_examples.py`; those tests make the
interpretive distinction explicit without changing any frozen experiment.

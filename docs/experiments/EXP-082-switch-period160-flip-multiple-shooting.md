# EXP-082 — Switch the period-160 flip with multiple shooting

Status: preregistered after EXP-081; pending clean execution

At the precision-consistent EXP-077 160→320 event, build the validated analytic
matching system with 32 cyclic segments. Split its two-dimensional nullspace
using the independently continued EXP-073 parent tangent, then correct both
secondary-tangent signs at frozen steps `0.0025`, `0.005`, `0.01`, and `0.02`.

Pass only if at least one candidate lies on the supercritical side within
`2e-6` of the event, has matching and phase residuals `<=1e-8`, differs from
the double-covered parent by both direct half-period closure and paired-node
RMS `>=1e-5`, and has child/parent period ratio within `0.001` of two. The
full segmented nodes are retained for independent continuation and
qualification.

Passing establishes a numerically distinct period-320 candidate. It does not
alone establish stability, attraction, or a supercritical sixth rung; those
require a subsequent frozen qualification from the segmented state.

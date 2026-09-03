# EXP-082 — Switch the period-160 flip with multiple shooting

Status: executed; passed candidate gate

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

The clean run at `130c641faf5df95f496b24882f18cf0ab6754bdb` passed. All
eight frozen corrections converged with matching residual at most `1.90e-12`.
Four candidates inside the prospective `2e-6` event neighborhood pass every
gate, two from each sign. Their half-node RMS values are `5.05e-4` to
`1.01e-3`, direct half-period closures are `1.29e-4` to `2.65e-4`, and period
ratios differ from two by at most `2.53e-8`. Full receipt SHA-256:
`3f0c0b4290d93c4942455d3eb202ccb69c624f38e10f3077e53a4696f70981cd`.

This establishes distinct period-320 candidates without composing the
ill-conditioned full monodromy. EXP-083 freezes independent fixed-parameter
identity and block-Floquet stability tests before calling the sixth rung
supercritical.

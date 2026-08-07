# EXP-058 — Switch the period-10 flip to period 20

Status: executed; failed as specified

Represent the verified period-10 parent over twice its fundamental duration at
the EXP-057 `-1` event. Use the nullspace of the extended shooting Jacobian to
separate the parent tangent from a secondary branch direction, then continue
both signs for 14 pseudo-arclength steps.

Pass if the smallest singular value is `<=1e-7`, tangent dot is `<=0.25`, both
arms contain at least 10 corrected points, endpoint distance from the doubled
parent is `>=1e-5`, endpoint half-period closure is `>=0.01`, and every full
closure is `<=1e-8`. No section-count gate is used. Passing establishes a
period-20 branch candidate; phase-invariant arm identity and parent/child
stability still require an independent fixed-parameter qualification.

The clean run at `04ef852` failed. The smallest shooting singular value
`2.70e-8` and tangent dot `0` pass their gates. One direction produced six
well-closed, half-period-distinct points before leaving the frozen `b` guard;
the other direction's first `0.006` predictor did not correct. Receipt SHA-256:
`760e76de0f8ec87d4e7cb849302d0eb9c66f5f46fe8a25dbf888527d7fe11b97`.

The accepted arm is a valid local period-20 candidate prefix but is not enough
to pass the two-arm experiment. Its first two points are stable and a later
point is unstable, prospectively suggesting a further cascade event; that
candidate is not refined until the period-20 identity is independently
qualified. EXP-059 retries both switch directions with a threefold smaller
frozen step and a wider guard. A post-write summary-printer crash on the empty
arm was also fixed; the EXP-058 receipt itself was complete before that crash.

# DEC-011 — PIM states seed orbits; they do not certify them

Date: 2026-08-07

## Decision

Use close returns from qualified PIM saddle trajectories only to propose
unstable-periodic-orbit shooting seeds. A seed becomes a recovered UPO only if
all of the following independent gates pass:

1. exact DOP853 section returns from the seed close after the proposed lag;
2. phase-conditioned flow shooting converges with a declared closure bound;
3. an independent one-period integration contains exactly the proposed number
   of oriented Barrio-section crossings;
4. the autonomous neutral Floquet multiplier is near one, while both the
   direct determinant and integrated-divergence prediction are retained (their
   agreement is binding only when the strongly contracting multiplier remains
   resolvable in the declared arithmetic); and
5. at least one nontrivial multiplier lies outside the unit circle by a
   declared margin.

PIM advancement includes occasional straddle refinement. Consequently, a close
pair in the stored state sequence may straddle a pseudo-orbit reset and is not
itself a recurrence of the flow. The exact-return gate rejects those cases.
Likewise, shooting may converge to the stable period-4 attractor; the crossing-
identity and transverse-instability gates record and reject that outcome as a
saddle UPO.

## Why this matters

Branch counts locate a representation change but do not identify the global
bifurcation that causes it. Recovered, identity-qualified saddle UPOs provide
the finite objects needed to seed stable/unstable manifold calculations and
formulate a continuation residual. Only that later manifold test can promote
a set of finite two/three brackets toward a mechanism-level TBA curve.

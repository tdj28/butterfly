# EXP-153 Hopf curve passes

Date: 2026-08-07

The next local-theory gap is now executable. A reusable closed-form Rössler
Hopf-locus implementation, independent characteristic-polynomial checks, and
unit tests have been added. EXP-153 freezes a 192-point fixed-`b=0.2` curve,
including the reported hub abscissa, plus an independent Brent eigensystem root
and transverse sign test at every point.

The clean execution subsequently passes every point. Maximum equilibrium,
Routh, complex-pair, frequency, and independent-root errors are all below
`6e-15`; the smallest transverse sign margin is `4.25e-8`. The locus reaches
`c=0.5192306256940273` at the reported hub abscissa `a=0.1798`, making the
fixed-`a` separation to the reported hub `9.789169374305974`.

This qualifies the Andronov--Hopf boundary underlying Jones Figure 2. It does
not assume that the resulting fixed-`a` path reaches a homoclinic point; that
global endpoint remains a separate manifold-intersection problem.

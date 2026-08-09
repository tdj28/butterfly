# EXP-153 Hopf-curve method frozen

Date: 2026-08-07

The next local-theory gap is now executable. A reusable closed-form Rössler
Hopf-locus implementation, independent characteristic-polynomial checks, and
unit tests have been added. EXP-153 freezes a 192-point fixed-`b=0.2` curve,
including the reported hub abscissa, plus an independent Brent eigensystem root
and transverse sign test at every point.

This targets the Andronov--Hopf boundary underlying Jones Figure 2. It does not
assume that the resulting fixed-`a` path reaches a homoclinic point; that global
endpoint remains a separate manifold-intersection problem.

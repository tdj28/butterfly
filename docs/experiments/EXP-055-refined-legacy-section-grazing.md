# EXP-055 — Refine the true legacy-section grazing

Status: executed; passed

Refine the continuous condition at which the stable period-10 child's closest
local maximum satisfies `y_max=y_eq`. At every local extremum of `y`, the
Rössler equation gives `x=-a y`; consequently `y=y_eq` also forces
`x=x_eq`, the boundary of the historical gated section. This directly tests a
section-boundary grazing without relying on a discrete crossing counter that
can miss a close pair.

Bisect the frozen EXP-052 branch bracket and require width `<=1e-9`, absolute
`y` clearance and gate margin `<=1e-8`, tangency residual `<=1e-10`, negative
second derivative, closure `<=1e-9`, and stable Floquet modulus. Passing would
establish a return-section topology change on a smooth stable period-10 orbit,
not a periodic-orbit bifurcation and not by itself a global TBA curve.

The clean run at `c28aae1177824dc8f6fca740795742cc69e800ce` passed.
It locates the grazing at
`b=0.18175023232062854` in a bracket of width `6.71e-11`. The best corrected
orbit has closure `8.00e-14`, nontrivial Floquet modulus `0.141731`, section
clearance `7.51e-10`, gate margin `1.84e-10`, tangency residual `8.07e-15`,
and negative second derivative `-17.2589`. The tangency state is approximately
`(0.00874614,-0.03569852,17.29455)`: its `x,y` coordinates meet the section
corner, but its large `z` coordinate makes clear that this is not an encounter
with the small equilibrium. Receipt SHA-256:
`dbef53745e163ea1a24f1b7b36f250c2d1f3191ca639501f98893827d7fddfe1`.

Accept a smooth stable-orbit grazing of the Jones legacy section. The accepted
intersection count changes from 10 to 11 across the grazing, but this is a
property of the return-section representation, not a change in the flow
orbit's fundamental period or stability. Near the grazing, event counts also
require step-size convergence because a close crossing pair can be skipped.

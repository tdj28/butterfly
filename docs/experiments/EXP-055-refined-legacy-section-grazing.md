# EXP-055 — Refine the true legacy-section grazing

Status: preregistered after the EXP-054 event-loss diagnosis; pending clean execution

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

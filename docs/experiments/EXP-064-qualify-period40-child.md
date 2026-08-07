# EXP-064 — Independently qualify the one-arm period-40 child

Status: preregistered after EXP-063; pending clean execution

At `(a,b,c)=(0.245,0.1798,5.1)`, independently correct the period-20 parent and
the distinct positive-arm period-40 candidate. Require full closures `<=1e-8`,
child half-period closure `>=0.01`, duration ratio within `1e-3` of two,
unstable parent, and stable child.

As an independent attraction test, perturb the child state by the frozen
vector `(1e-4,-1e-4,5e-5)`, integrate for 16 child periods, correct the terminal
state, and require phase-aligned RMS `<=1e-5` to the shooting child with stable
Floquet modulus. Passing establishes a supercritical period-20-to-period-40
flip despite EXP-063's failed symmetric two-arm continuation gate.

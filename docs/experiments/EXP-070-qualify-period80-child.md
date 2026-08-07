# EXP-070 — Independently qualify the period-80 child

Status: preregistered after EXP-069; pending clean execution

At `(a,b,c)=(0.245,0.179735,5.1)`, independently correct the period-40 parent
and distinct period-80 candidate. Require closures `<=1e-8`, child half-period
closure `>=0.001`, duration ratio within `1e-3` of two, unstable parent, and
stable child.

Perturb the child by `(5e-5,-5e-5,2.5e-5)`, integrate for 12 child periods,
correct the terminal state, and require phase-aligned RMS `<=1e-5` to the
shooting child with stable modulus. Passing establishes the supercritical
40→80 rung. Only then may the independently predicted 80→160 event be refined.

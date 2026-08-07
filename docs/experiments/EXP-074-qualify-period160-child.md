# EXP-074 — Independently qualify the period-160 child

Status: preregistered after EXP-073; pending clean execution

At `(a,b,c)=(0.245,0.17971425,5.1)`, independently correct the period-80
parent and period-160 candidate. Require closures `<=1e-8`, child half-period
closure `>=2e-4`, duration ratio within `1e-3` of two, unstable parent, and
stable child.

Perturb the child by `(1e-5,-1e-5,5e-6)`, integrate for 32 child periods,
correct the terminal state, and require phase-aligned RMS `<=1e-5` to the
shooting child with stable modulus. Passing establishes the fifth
supercritical rung, 80→160.

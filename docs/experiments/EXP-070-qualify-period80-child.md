# EXP-070 — Independently qualify the period-80 child

Status: executed; passed

At `(a,b,c)=(0.245,0.179735,5.1)`, independently correct the period-40 parent
and distinct period-80 candidate. Require closures `<=1e-8`, child half-period
closure `>=0.001`, duration ratio within `1e-3` of two, unstable parent, and
stable child.

Perturb the child by `(5e-5,-5e-5,2.5e-5)`, integrate for 12 child periods,
correct the terminal state, and require phase-aligned RMS `<=1e-5` to the
shooting child with stable modulus. Passing establishes the supercritical
40→80 rung. Only then may the independently predicted 80→160 event be refined.

The clean run at `42d53f52d84744ad03a56292188fcb9097737abc` passed.
At `b=0.179735`, the period-40 parent has modulus `1.240957`; the period-80
child has modulus `0.00553596`, half-period closure `0.0048954`, duration ratio
`2.00000159`, and closure `1.39e-12`. The perturbed trajectory recovers the
same stable orbit at phase-aligned RMS `1.88e-8`. Receipt SHA-256:
`91b348fd755e0e5478997e5e2a14df23fb0cbc607f25462353b7f2005f6dbde8`.

Accept a supercritical period-40-to-period-80 flip. The observed period-80
`-1` bracket contains the untouched EXP-066 prediction; EXP-071 now refines it
as an out-of-sample test.

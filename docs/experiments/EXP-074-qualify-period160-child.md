# EXP-074 — Independently qualify the period-160 child

Status: executed; passed

At `(a,b,c)=(0.245,0.17971425,5.1)`, independently correct the period-80
parent and period-160 candidate. Require closures `<=1e-8`, child half-period
closure `>=2e-4`, duration ratio within `1e-3` of two, unstable parent, and
stable child.

Perturb the child by `(1e-5,-1e-5,5e-6)`, integrate for 32 child periods,
correct the terminal state, and require phase-aligned RMS `<=1e-5` to the
shooting child with stable modulus. Passing establishes the fifth
supercritical rung, 80→160.

The clean run at `74490b25359e06e234d55c54b2b1b895da374c17` passed.
At `b=0.17971425`, the period-80 parent has modulus `1.443266`; the period-160
child has modulus `0.878470`, half-period closure `0.00174818`, duration ratio
`1.99999968`, and closure `1.02e-12`. The perturbed trajectory recovers the
same stable orbit at phase-aligned RMS `2.22e-7`. Receipt SHA-256:
`7373248b2ae9399f4d087050b4532fe708a71b26cb509484df88b412e1b88dc2`.

Accept a supercritical period-80-to-period-160 flip. The EXP-073 distinct arm
brackets a further `-1` crossing; refine it next without yet claiming the
period-320 child.

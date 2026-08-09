# EXP-156 — Coupled first flip on the Hopf-to-hub path

Status: exact c-derivative implementation, tests, method, and gates frozen
before execution

## Question

Does the first stability-loss bracket from EXP-155 contain a genuine
one-winding period-1 flow orbit with a nontrivial Floquet multiplier exactly
equal to `-1`?

## Frozen method

Four shooting nodes, the flow period, `c`, and four transported tangent nodes
are solved simultaneously. Orbit matching, phase, anti-periodic tangent
transport, and tangent normalization form a square system. The Jacobian uses
the exact state, `c`, and second-variational derivatives of the Rössler flow;
finite-difference unit tests cover both segment actions and the full augmented
system.

The source is the hash-bound EXP-155 receipt and the frozen bracket is
`c in [3.1556294736842108,3.2536126315789478]` at
`(a,b)=(0.1798,0.2)`. Four cyclic monodromy products and the block-cyclic
representation must agree. An independent Radau monodromy must close the
orbit, reproduce neutral `+1` and flip `-1`, and preserve winding one.

## Interpretation boundary

Passing establishes the codimension-one flip event on this particular path.
It does not establish or stabilize the period-2 child, continue the higher
cascade, demonstrate symbolic/logistic ordering, or test the homoclinic claim.

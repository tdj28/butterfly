# FND-005 — The published unimodal and bimodal controls reproduce directly

Date: 2026-08-07
Status: qualified endpoint reproduction; boundary and saddle continuation pending

EXP-108 implements the Poincare section explicitly declared by Barrio, Blesa,
and Serrano: the plane through the small equilibrium's `x` coordinate with
`dx/dt>0`. This differs from the historical half-plane recovered from Jones's
code and therefore closes an important object-definition gap.

At fixed `(b,c)=(0.2,20)`, all 42 primary `y` classifications reproduce the
paper's Figure 2 endpoint claims across three section offsets and seven frozen
oracle settings:

- `a=0.11`: unimodal, two branches;
- `a=0.2`: bimodal, three branches.

All 42 independent `z` classifications agree. Every bootstrap consensus is
`1.0`, coverage is `0.98--1.0`, and conditional spread is at most `0.02389`.
This is stronger than visual similarity: it supplies an operational,
uncertainty-gated reproduction of both attracting endpoint maps.

It does not yet locate the codimension-one boundary, establish that the Jones
and Barrio loci coincide, or reproduce the PRL's continuation through regular
windows. A prospective `a`-path scan is now authorized. Periodic gaps on that
path must remain unresolved until a nonattracting chaotic-saddle method is
qualified; they may not be filled by interpolating attractor labels.

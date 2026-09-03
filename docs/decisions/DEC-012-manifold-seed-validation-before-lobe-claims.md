# DEC-012 — Validate manifold seeds before interpreting lobes

Date: 2026-08-07

## Decision

Do not plot or interpret an unstable-manifold branch merely by perturbing a
periodic-orbit state along a raw flow-monodromy eigenvector. At an exact
positive Barrio-section crossing:

1. select the real Floquet eigenpair of largest modulus;
2. remove its flow-phase component so the direction is tangent to the section;
3. normalize in the declared section coordinate scales;
4. apply the exact first-return map for the orbit's fundamental lag; and
5. require the observed signed amplification to reproduce the Floquet
   multiplier on both perturbation signs and at multiple seed sizes.

The comparison uses the independently advanced unperturbed base point, so
finite orbit-closure error does not masquerade as seed amplification. At least
two of the three frozen sizes per sign must pass relative multiplier and
transverse-residual gates. Only a passed seed instance may enter later lobe,
pruning, or reinjection calculations.

## Why this matters

The Rössler UPOs are strongly unstable, and their raw monodromy eigenvectors
contain an arbitrary autonomous-flow phase component. A visually plausible
perturbation can therefore depart the section or follow a numerical direction
unrelated to the Poincare-map unstable manifold. EXP-142 applies this
validation to all eleven recovered families at both topology endpoints.

Passing EXP-142 establishes a qualified local seed library, not a manifold
connection or TBA event. Global lobe geometry still requires seed-density,
seed-size, return-horizon, and section/coordinate convergence.

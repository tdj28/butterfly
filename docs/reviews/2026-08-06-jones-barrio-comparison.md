# Jones and Barrio-Blesa-Serrano: overlap and differences

Date received: 2026-08-06

Source: user-supplied GPT Pro comparison, checked where possible against the two
local 2012 papers. Claims about their common 2011 foundation remain pending
primary-source verification.

## Bottom line

The papers are best described as **independent, near-simultaneous discoveries
of the topology-change curve's explicit relationship to periodicity-hub and
shrimp organization**, followed by different elaborations.

They are not redundant:

- Barrio, Blesa, and Serrano provide the stronger invariant-set and global-
  bifurcation formulation.
- Jones provides the more ambitious orbit-level geometric and symbolic
  mechanism.

## Shared 2012 advance

Both papers connect a locus where the Rössler first-return map changes between
unimodal/two-branch and bimodal/three-branch structure to the organization of
shrimp centers in the periodicity hub. Both relate the locus to doubly-
superstable periodic orbits.

The names and operational definitions differ:

- Jones uses `TTL23`, initially inferred from return-map geometry, shrimp
  alignment, and stable-periodic-orbit organization.
- Barrio-Blesa-Serrano use the topological branch-adding bifurcation curve
  (`TBA`), tracked through the topology of chaotic invariant sets.

The working hypothesis is that these denote the same underlying dynamical
locus. That equivalence must be tested numerically rather than assumed from
similar figures and language.

## Distinct contributions

| Topic | Jones | Barrio-Blesa-Serrano | Project interpretation |
|---|---|---|---|
| Object followed | Stable windows, periodic orbits, return-map branches, and spiral connections | Chaotic attractors and nonattracting chaotic saddles | Complementary views of the same parameter region |
| Curve inside regular windows | Not defined through the complete nonattracting chaotic set | TBA remains defined using chaotic saddles computed by the sprinkler method | Major PRL-only extension to reproduce |
| Hub envelope | Hopf-to-homoclinic slices proposed to inherit logistic/unimodal ordering | Not developed | Distinctive Jones hypothesis |
| Logistic ordering | Critical-point caustics and window ordering tested through period seven | No equivalent slice/conjugacy test | Distinctive Jones finite-range analysis |
| Doubly-superstable points | Used to explain shrimp alignment with the transition | TBA passes through these points and is tangent to `s+` | Strong overlap; PRL makes the sharper local geometric claim |
| Shrimp anatomy | Mutant tails connect different periods across the transition | One period-four shrimp divided into six regions by TBA, `s+`, and `s-` | Inter-period versus fixed-period analyses |
| Nested-spiral mechanism | Rotating third-branch reinjection produces new inner orbit points and `p -> p+1` transitions | Successive TBA tangencies at doubly-superstable shrimp centers organize the spiral | Candidate state-space mechanism versus parameter-space organizer |
| Symbolic dynamics | Inter-period `C,D,0,1,2` transitions through period seven | Local `L,A,M,B,R` partition within a fixed-period shrimp | Different symbolic questions, not competing encodings |
| Experimental support | None | Rössler-type circuit return maps on both sides of the transition | External empirical corroboration, not a Jones result |
| Claimed generality | Rössler-specific | Generic strongly dissipative 3D systems with Shilnikov saddle foci | Broader PRL framing, still numerical rather than a general theorem |

## Priority wording

| Criterion | Record |
|---|---|
| Earlier journal receipt | Barrio-Blesa-Serrano, 2011-12-16 |
| Earlier publicly accessible version identified here | Jones arXiv v1, 2012-01-20 |
| Peer-reviewed publication | Barrio-Blesa-Serrano, 2012-05-25 |
| Rotating-reinjection and inter-period symbolic mechanism | Jones |
| TBA across attractors and chaotic saddles | Barrio-Blesa-Serrano |

Chronology supports independence but cannot, by itself, exclude undocumented
communication. The project has found no evidence of derivation in either
direction. See [`DEC-001`](../decisions/DEC-001-independent-codiscovery.md) for
the required wording.

## Consequences for the validation program

1. Test whether Jones's `TTL23` and the PRL's `TBA` coincide under one published
   return-map and branch-classification definition.
2. Reproduce the TBA through regular regions using chaotic saddles, not only
   observable attractors or period labels.
3. Continue `s+`, `s-`, and TBA and quantify their intersection and tangency at
   doubly-superstable points.
4. Treat the PRL's fixed-period shrimp subdivision and Jones's cross-period
   mutant-shrimp connectivity as separate experiments.
5. Test whether rotating reinjection predicts information not already implied
   by TBA geometry and Shilnikov homoclinic organization.
6. Keep finite logistic-like ordering separate from any claim of conjugacy.

## Verification status

The following GPT Pro comparison points were confirmed directly in the local
Barrio-Blesa-Serrano PRL: use of chaotic saddles and the sprinkler method,
definition of TBA through chaotic and regular regions, experimental circuit
return maps, six subregions in a representative shrimp, the `L,A,M,B,R`
symbolic partition, and TBA tangency to `s+` at a doubly-superstable point.

The claimed common 2011 foundation and its exact priority scope remain in the
source-verification queue until the cited 2011 paper is added and reviewed.

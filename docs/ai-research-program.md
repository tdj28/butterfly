# Topology-aware AI research program

Status: adopted with mathematical corrections; execution gated by numerical evidence

## Objective

Use AI to discover previously unknown structure in the Rössler periodicity hub,
not merely reproduce diagrams or decorate established results. The target is a
parameterized description of branch addition, symbolic period insertion, and
related global bifurcation geometry whose proposals are checked by independent
numerical dynamics and selectively certified by validated computation.

Working title:

> **Learning and Certifying the Branch-Addition Skeleton of the Rössler
> Periodicity Hub: Parameterized Quotient Coordinates, Active Search, and
> Symbolic-Rule Discovery**

The title deliberately says **quotient**, not **neural conjugacy**.

## Governing principle

> **ML proposes; dynamical-systems numerics tests; validated computation
> certifies.**

A neural model is never sole evidence for a periodic orbit, branch-addition
curve, symbolic transition, conjugacy, or topological statement.

## Central mathematical correction

Where defined, a Poincaré return map of a smooth flow is locally invertible. A
multimodal logistic-like one-dimensional map is noninvertible. The full
two-dimensional return map therefore cannot generally be topologically
conjugate to the proposed one-dimensional map.

The defensible construction has two parts:

1. an invertible coordinate change `H_mu` between two-dimensional section
   representations; and
2. a non-injective projection along candidate strongly contracting leaves to a
   one-dimensional factor.

The resulting relationship is a quotient or semiconjugacy unless stronger
hypotheses are actually established. “Approximate conjugacy” is not used to
hide a dimension mismatch or failure of injectivity.

## Falsifiable quotient hypothesis

For a bounded parameter region and a declared invariant subset of the section,
test whether coordinates `(u,v)=H_mu(x)` can make the return map approximately
skew-product:

```text
H_mu P_mu H_mu^-1(u,v) approximately equals (g_mu(u), q_mu(u,v)).
```

The hypothesis requires all of the following:

- parameter-continuous local coordinate charts with fixed orientation/gauge;
- forward-invariant declared domains and dynamically relevant branch ranges;
- small dependence of the first component on the transverse coordinate;
- invariant-cone or invariant-fiber evidence, not only a pointwise derivative
  penalty;
- uniform transverse contraction and singular-value separation;
- agreement on chart overlaps;
- robustness to alternative Poincaré sections and numerical solvers; and
- out-of-region failure detection.

The implementation must be allowed to conclude that no valid global
one-dimensional quotient exists. Failure or singularity near the homoclinic or
branch-addition geometry would itself be a scientific result. Use an atlas of
local charts rather than forcing one global neural coordinate.

## AI workstreams

### A. Interpretable quotient discovery

Compare progressively more flexible models:

1. declared scalar projections and principal-curve/manifold baselines;
2. local constrained splines and sparse polynomial/rational maps;
3. parameter-conditioned monotone-segment splines;
4. parameter-conditioned invertible networks with explicit chart alignment.

The latent one-dimensional map must penalize unsupported curvature and
critical points. Branch count is not merely `1 + number of extrema`: critical
points must lie in the maximal relevant invariant domain, and branches entering
through domain boundaries or return-time singularities must be handled
explicitly.

Primary metrics:

- commutation and reconstruction residuals on geographically held-out regions;
- transverse contraction and invariant-cone violations;
- critical-point and critical-value localization;
- branch-count and kneading-word agreement with the numerical oracle;
- periodic-orbit recovery and Floquet-multiplier error;
- transition-matrix or entropy agreement; and
- sensitivity to section, coordinate chart, precision, and solver.

### B. Active branch-addition search

Use calibrated uncertainty to choose new parameter boxes only after an
independent numerical oracle exists. The oracle—not the learner—supplies branch
labels, critical itineraries, periodicity, multipliers, and continuation
residuals.

Efficiency is an empirical claim. Compare integrations and wall cost required
to reach a fixed curve error against:

- uniform grids;
- adaptive quadtrees;
- ordinary numerical continuation;
- Gaussian-process level-set estimation; and
- an unconstrained neural surrogate.

Retain explicit space-filling exploration so uncertainty errors cannot hide
isolated shrimps. Measure uncertainty calibration rather than treating model
ensembles as calibrated by construction.

### C. Symbolic grammar discovery

Build a versioned database of parameter, branch count, critical itinerary,
period, orbit permutation, stability, and transition type. Canonicalize cyclic
word shifts, orientation reversal, and symbol relabeling before fitting rules.
Freeze the symbolic partition independently of the proposed grammar.

Search for the smallest human-readable rule using finite-state transducers,
string rewriting, decision trees, symbolic expressions, or constrained program
synthesis. A transformer may be a predictive baseline, not the scientific
result.

Prospective protocol:

1. train through a declared maximum period or spiral turn;
2. commit predicted unseen transitions before computing them;
3. continue the predicted exact periodic orbits;
4. report confirmations, failures, and revisions; and
5. test the rule on an entirely held-out contiguous region.

### D. Selective certification

Interval and covering-relation methods certify selected numerical premises and
consequences: representative periodic orbits, branch boxes, doubly superstable
points, critical itineraries, and forcing/entropy statements. They certify
explicit boxes and maps, not a neural network in the abstract.

Lean or another proof assistant is deferred. It may later check finite
combinatorial consequences of certified inputs, but it cannot replace validated
numerics for those inputs.

### E. Optional observation-only extension

After the equation-informed program succeeds, hide the vector field, expose
partial noisy observations, reconstruct a section in delay coordinates, and
ask whether the branch skeleton can be recovered. A circuit experiment is a
separate extension, not a dependency of the core paper.

## Execution gates

### Gate 0 — trustworthy numerical oracle

- reproduce the known hub with explicit unresolved states;
- compute converged Lyapunov spectra;
- continue equilibria, periodic orbits, and the known two-to-three transition;
- include unstable periodic orbits and chaotic-saddle data; and
- freeze section, partition, orbit, and branch definitions.

No neural quotient work begins before this gate.

### Gate 1 — quotient plausibility

- demonstrate transverse contraction and dimensional separation;
- show local quotient consistency across sections and solver changes;
- establish chart alignment across parameters; and
- identify regions where the hypothesis fails.

If Gate 1 fails, publish the failure and continue with two-dimensional return
map topology rather than forcing a latent line.

### Gate 2 — known-transition positive control

- recover unimodal and bimodal regions;
- recover the known branch-addition curve and selected shrimp-center crossings;
- pass contiguous-region holdouts; and
- outperform or add information beyond constrained non-neural baselines.

### Gate 3 — new discovery

Require at least one prospectively verified result not already visible in the
2012 work: a higher branch curve, mutant-shrimp family, symbolic connection,
winding/period relation, curve termination/crossing, or homoclinic accumulation
relationship.

### Gate 4 — selective certification and release

- certify a decisive subset;
- release frozen training/holdout regions and negative results;
- publish trajectory, section, orbit, continuation, and symbolic artifacts; and
- bind every figure and table to immutable receipts.

## Scope control

The balanced core paper contains the quotient hypothesis, known-transition
positive control, active discovery, one genuinely new result, prospective
symbolic prediction, and selective certification. Observation-only inference,
circuit experiments, dozens-system transfer, and formal proof-assistant work
are follow-on studies.

## Relationship to current implementation

The reference vector field, adaptive integration, interpolated Poincaré events,
conservative recurrence classifier, and hashed scan receipts are Gate 0
infrastructure. The immediate work remains numerical: Lyapunov spectra,
classifier completion, GPU parity, hub reproduction, and continuation. GPU
compute initially generates and verifies the ground-truth database; it does not
train a headline neural network prematurely.

## Verified related work

- [Deep Learning of Conjugate Mappings](https://arxiv.org/abs/2104.01874)
- [Learning normal form autoencoders](https://arxiv.org/abs/2106.05102)
- [Active search for bifurcations](https://doi.org/10.1063/5.0226625)
- [Inferring bifurcation diagrams with transformers](https://doi.org/10.1063/5.0204714)
- [Testing topological conjugacy of time series](https://doi.org/10.1137/23M1594728)
- [Inferring bifurcation diagrams of two distinct chaotic systems by a single
  machine](https://arxiv.org/abs/2604.26632)

These sources establish relevant precedents but do not prove that the combined
novelty gap is unoccupied. A systematic literature review remains required
before making a publication novelty claim.

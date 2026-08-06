# World-class dynamical-systems research platform roadmap

Status: strategic draft; not a frozen experiment plan
Last updated: 2026-08-06

## Ambition

Build an open, reproducible platform that can discover, classify, continue, and
selectively validate periodicity hubs and related structures across many
continuous-time chaotic systems.

"World-class" will not mean the largest raster image. It will mean that the
platform joins capabilities that are usually separated:

1. high-throughput CPU/GPU discovery;
2. numerical bifurcation continuation;
3. phase-space topology and symbolic dynamics;
4. multistability and uncertainty analysis;
5. computer-assisted validation for selected claims;
6. cross-system comparison through one declared model interface; and
7. complete machine-verifiable provenance from configuration to publication.

The recovered 2012 code remains a historical implementation and regression
source. It should not become the architecture of the new platform.

## Scientific products

The program should yield three connected products.

### Butterfly Engine

A tested numerical library for model definition, simulation, Poincaré maps,
Lyapunov spectra, periodic-orbit detection, continuation, topology, basin
analysis, and selected rigorous validation.

### Butterfly Atlas

A versioned atlas of parameter planes, periodic windows, hubs, bifurcation
curves, invariant-set topology, and uncertainty regions across curated strange
attractors. Every cell and curve must trace to an experiment receipt.

### Butterfly Research Program

A sequence of claim-ledger-driven studies: first reconstruct Jones and
Barrio-Blesa-Serrano, then test the distinctive Jones mechanisms, then ask
which structures persist across other systems.

## Governing research discipline

The project adopts the adjacent `agent-skill-documents` playbooks:

- separate exploratory discovery from frozen confirmatory tests;
- define falsifiable claim boundaries and acceptance tests before outcomes;
- validate the exact expensive code path on cheap hardware;
- measure throughput before renting larger hardware;
- preserve immutable raw ingredients and hashed receipts;
- bind remote execution to an exact commit and container digest;
- prove forced-kill resume behavior before using interruptible compute;
- require explicit approval for each costed paid run; and
- terminate task-owned resources immediately after verified retrieval.

## Recommended technical architecture

### 1. Declarative system registry

Every system implements one versioned specification:

- state variables and vector field;
- analytic or automatically differentiated Jacobian;
- parameter names, units, admissible ranges, and constraints;
- equilibria and known local bifurcations where available;
- candidate Poincaré sections with orientation;
- deterministic initial conditions and basin-sampling policies;
- known reference regimes and primary citations; and
- optional symmetries, symbolic partitions, and physical interpretation.

The same specification must drive CPU reference integration, GPU ensemble
integration, continuation, and artifact metadata. Duplicating equations across
backends invites scientific drift.

### 2. Reference numerical path

Create a readable Float64 CPU implementation before optimizing:

- adaptive high-order integration with dense output;
- interpolated and oriented event crossings;
- explicit transient and convergence criteria;
- complete tangent/variational equations;
- full Lyapunov spectrum with documented QR cadence;
- recurrence-based period candidates followed by a true minimal-period test;
- separate labels for periodic, chaotic, quasiperiodic, escaping,
  multistable, numerical failure, and unresolved; and
- at least two independent solver paths for important results.

This reference path is the correctness oracle for GPU parity, not necessarily
the production scanner.

### 3. GPU ensemble path

Parameter-plane integration is an ensemble of many small, independent ODEs and
is therefore well suited to GPUs. The first implementation should evaluate
Julia's SciML stack rather than immediately maintaining custom CUDA:

- `DiffEqGPU.jl` provides massively parallel ensemble kernels;
- `DynamicalSystems.jl` and `ChaosTools.jl` provide Poincaré, Lyapunov,
  periodicity, entropy, and basin tools; and
- `BifurcationKit.jl` provides equilibria, periodic orbits, Floquet analysis,
  bifurcation detection, and multi-parameter continuation.

Use a custom CUDA/C++ kernel only after profiling demonstrates a material
bottleneck that the maintained ensemble stack cannot solve. Preserve the
legacy C and CUDA code as comparison implementations, not as silent truth.

GPU arithmetic is an experiment variable. Discovery may use a qualified faster
path, but headline results require Float64 parity and precision/horizon sweeps.
Chaotic point trajectories need not remain pointwise identical; declared
classification observables and invariant quantities must remain consistent.

### 4. Continuation and global bifurcations

Raster scans locate candidates; continuation establishes geometry.

Required capabilities:

- equilibrium, Hopf, fold, and codimension-two continuation;
- periodic-orbit shooting/collocation and Floquet multipliers;
- saddle-node, period-doubling, and Neimark-Sacker curves;
- two-parameter continuation of superstable and topology-change loci;
- homoclinic/heteroclinic boundary-value problems; and
- branch switching and restart artifacts.

Use BifurcationKit/HclinicBifurcationKit for the integrated development path
and AUTO-07p/HOMCONT as an independent mature cross-check for consequential
curves. Agreement between two packages is stronger evidence than one elaborate
pipeline agreeing with itself.

### 5. Topology and symbolic dynamics

Implement explicit, testable objects:

- return-map critical points and branch count;
- symbolic partitions and critical itineraries;
- kneading invariants, orbit permutations, pruning, and entropy estimates;
- unstable-periodic-orbit enumeration;
- linking and winding data, template matrices, and branch ordering;
- persistent homology and, experimentally, templex-based classifications; and
- a coordinate/section sensitivity analysis for every proposed reinjection
  observable.

This layer must distinguish topology from a visually persuasive projection.

### 6. Validated-numerics path

Do not attempt to interval-validate every atlas pixel. Select decisive objects:

- the focal homoclinic intersection;
- representative periodic windows and their widths;
- critical low-period orbits and Floquet data;
- covering relations or forcing results; and
- points on the topology-change and superstability curves.

CAPD::DynSys is a strong independent C++ path because it supports interval ODE
integration, variational equations, Poincaré maps, derivatives, and
multiprecision. Computer-assisted validation is a distinct workstream requiring
specialist review; AI-generated proof code is not self-validating.

### 7. Data and provenance layer

Use durable, language-neutral artifacts:

- chunked arrays such as Zarr for dense parameter fields;
- Parquet/Arrow tables for orbits, crossings, bifurcations, and classifications;
- JSON configuration, schema, run receipt, and figure receipt files;
- SHA-256 manifests generated before transfer;
- stable IDs for systems, parameter planes, tiles, experiments, datasets,
  curves, orbits, and figures; and
- immutable raw shards with derived products generated separately.

Do not store full trajectories for every grid point. Preserve the raw
ingredients needed for frozen and plausible follow-up analyses—crossing
sequences, convergence diagnostics, Lyapunov summaries, classification scores,
and selected full trajectories—without creating an unaffordable data lake.

## Rössler flagship program

The Rössler study should be the platform's qualification suite.

### Reproduce before extending

1. Reproduce the primary hub and period map with convergence and basin tests.
2. Reproduce the Lyapunov diagram with a documented algorithm.
3. Continue the Hopf, periodic-orbit, superstability, and TBA/TTL curves.
4. Reproduce chaotic saddles inside regular windows.
5. Test whether Jones's `TTL23` and the PRL's `TBA` are numerically the same
   locus under one operational definition.
6. Validate the proposed focal homoclinic point and state a bounded uniqueness
   claim, if one survives.

### Strengthen the distinctive Jones contributions

1. Publish exact definitions of the `L1` and `L2` paths.
2. Recreate logistic critical-point caustics and finite window ordering.
3. Determine whether a normally attracting one-dimensional graph or quotient
   exists; use finite agreement or semiconjugacy language unless conjugacy is
   actually established.
4. Continue mutant-shrimp tails and periodic-orbit branches rather than
   inferring connectivity from pixels.
5. Define reinjection with a geometric section coordinate, winding/linking
   quantity, or template invariant.
6. Test whether reinjection predicts `p -> p+1` transitions beyond what TBA
   tangency and homoclinic-sheaf geometry already predict.
7. Generate and verify symbolic transitions beyond period seven.
8. Validate a small set of decisive orbits/windows with interval methods.

## Scaling to dozens of attractors

### Do not begin with dozens

Qualify the full pipeline on Rössler, then two deliberately different systems,
before expanding. Otherwise the project will create dozens of incomparable
images and one shared bug.

### Curated expansion tiers

1. **Qualification tier:** Rössler plus two systems with well-documented but
   structurally different chaos.
2. **Saddle-focus tier:** approximately 10 three-dimensional dissipative flows
   where periodicity-hub theory is genuinely plausible.
3. **Application tier:** circuits, lasers, chemical, biological, and mechanical
   systems with primary literature and meaningful parameter pairs.
4. **Boundary tier:** switching attractors, toroidal chaos, four-dimensional
   systems, and hyperchaos, where template assumptions may fail.

The `dysts` database is a useful discovery corpus—it reports more than 100
known chaotic systems—but its fixed reference trajectories are not, by
themselves, a parameter-plane benchmark. Each accepted model still needs
curated parameter semantics, domains, sections, and primary sources.

### Cross-system pipeline

For each candidate:

1. validate equations and a known reference trajectory;
2. classify equilibria and local eigenstructure;
3. choose parameter pairs prospectively;
4. run coarse scans and multiple initial conditions;
5. detect candidate windows, shrimps, and hubs automatically;
6. refine boundaries adaptively rather than uniformly;
7. continue the candidate structures;
8. compute phase-space topology and symbolic data;
9. test robustness across sections, precision, and solver; and
10. promote only validated candidates into the public atlas.

Absence of a hub is a result. The pipeline must not tune every system until the
desired picture appears and then present the selection as universal.

## Appropriate uses of AI

AI can substantially accelerate:

- primary-literature triage and claim/source mapping;
- translation of model equations into a typed registry;
- test generation and CPU/GPU differential testing;
- anomaly detection and active selection of refinement tiles;
- candidate Poincaré-section and symbolic-partition proposals;
- pattern mining across orbit and topology descriptors;
- generation of result-free experiment plans and adversarial reviews; and
- provenance, documentation, accessibility, and release checks.

AI must not be the numerical oracle, the proof checker, or the source of a
classification that cannot be recomputed mechanically. Every scientific number
must derive from committed code and immutable data, and every literature claim
must resolve to a primary source.

## Work packages and indicative duration

These estimates assume one committed researcher using AI assistance, with
periodic expert review. A small specialist team can parallelize them; a
part-time solo effort should expect longer.

| Work package | Indicative duration | Exit condition |
|---|---:|---|
| Preserve legacy and build CPU reference | 4-8 weeks | Tested solver, events, classifier, golden cases |
| GPU ensemble and Runpod qualification | 4-8 weeks | CPU/GPU parity, timed tiles, forced-kill resume, receipts |
| Reproduce Jones/Barrio figures and curves | 2-4 months | Regenerable figures with convergence and continuation |
| Reinjection, mutant-shrimp, and symbolic program | 4-8 months | Operational definitions and decisive tests |
| Selected rigorous validation | 4-12 months, overlapping | CAPD/AUTO-backed enclosures or bounded claims |
| Three-system qualification atlas | 3-6 months | One schema and pipeline works across distinct systems |
| Curated 20-50-system atlas | 6-18 additional months | Audited cross-system results and public benchmark |

A credible world-leading program is therefore approximately 18-36 months for a
solo researcher plus AI, or 9-18 months for a focused 3-4 person team. The
validated-numerics and topology work benefit greatly from collaborators with
specific expertise.

## People and expertise

Ideal roles, even if part-time:

- scientific lead in nonlinear dynamics;
- numerical/HPC engineer;
- bifurcation and continuation specialist;
- rigorous-numerics/interval-method collaborator; and
- topology/symbolic-dynamics collaborator.

AI can multiply each role's productivity but cannot replace independent domain
review for a theorem-level or priority-sensitive claim.

## Success criteria

The platform earns a leadership claim only when it has:

- reproduced the Rössler results with public, one-command workflows;
- resolved or sharply narrowed the original paper's strongest gaps;
- produced at least one genuinely new, falsifiable result about reinjection,
  symbolic progression, or hub organization;
- demonstrated the same audited pipeline on structurally different systems;
- validated selected periodic or global objects with independent tools;
- released a useful benchmark/atlas with stable schemas and provenance;
- survived external reproduction; and
- separated confirmed universality from attractive counterexamples.

## First 90 days

1. Freeze the legacy implementation and extract golden comparison cases.
2. Write the system schema and Float64 serial reference integrator.
3. Add equilibrium, Jacobian, event-crossing, period, and Lyapunov tests.
4. Reproduce a small Rössler hub map with explicit unresolved states.
5. Prototype the same ensemble with DiffEqGPU locally or on the cheapest
   qualified GPU.
6. Benchmark one tile, estimate the full cost, and do not launch a full scan.
7. Stand up continuation of the equilibrium/Hopf/periodic-orbit branches.
8. Freeze the first confirmatory Rössler reproduction only after adversarial
   plan review.

## Primary technical references

- [DiffEqGPU ensemble kernels](https://docs.sciml.ai/DiffEqGPU/stable/manual/ensemblegpukernel/)
- [DynamicalSystems.jl and ChaosTools](https://juliadynamics.github.io/DynamicalSystemsDocs.jl/chaostools/)
- [BifurcationKit tutorials](https://bifurcationkit.github.io/BifurcationKitDocs.jl/stable/tutorials/tutorials/)
- [HclinicBifurcationKit](https://bifurcationkit.github.io/HclinicBifurcationKit.jl/dev/)
- [AUTO-07p](https://auto-07p.github.io/)
- [CAPD::DynSys](https://capd.sourceforge.net/capdDynSys/docs/html/)
- [Dysts/chaotic-system benchmark paper](https://arxiv.org/abs/2110.05266)
- [Computer-assisted Rössler forcing](https://doi.org/10.1016/j.jde.2022.01.022)
- [Templex taxonomy preprint](https://arxiv.org/abs/2602.01575)

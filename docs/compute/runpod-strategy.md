# Runpod GPU execution strategy

Status: implementation active; first qualification pod authorized
Last updated: 2026-08-06

## Decision boundary

Runpod is a suitable execution target for large ensembles of independent ODE
trajectories. It is not the default home for every calculation.

Use GPUs for:

- dense or adaptively selected parameter ensembles;
- batched tangent/variational integration and Lyapunov summaries;
- basin sampling with many initial conditions; and
- large candidate searches with compact per-trajectory outputs.

Prefer CPU or specialist continuation software for:

- equilibrium and periodic-orbit continuation;
- homoclinic boundary-value problems;
- symbolic/topological post-processing;
- most interval validation; and
- plotting, aggregation, and publication verification.

Continuation can use GPU-capable software experimentally, but it should not be
forced onto a GPU merely because a GPU is available.

## Hardware selection

Choose hardware from measured total cost, not brand prestige or hourly price.

- Consumer GPUs can be excellent for qualified Float32 discovery but often
  have weak Float64 throughput.
- A100/H100/H200-class devices are stronger candidates when Float64 dominates.
- Memory is unlikely to be the primary limit for three-dimensional ODE states;
  arithmetic throughput, control-flow divergence, compiler support, and output
  bandwidth matter more.
- Multi-GPU is tile-level data parallelism first. It does not require model
  sharding or inter-GPU communication.

At launch time, query Runpod's current catalog and `costPerHr`; do not hard-code
prices or assume availability.

## Cheap-node qualification ladder

No full paid scan may skip these gates:

1. **Local CPU:** entire workflow on a tiny grid, including analysis and
   receipt verification.
2. **Local/cheap GPU:** exact production kernel on a small tile; compare against
   frozen Float64 CPU cases.
3. **Cheapest representative rented GPU:** measure steady-state trajectories per
   second, output rate, startup time, and failure behavior.
4. **Target GPU:** only after a written cost estimate and explicit approval.

Correctness and throughput are separate gates. A correct kernel that is 100
times too slow is not ready.

## Precision and parity contract

Record storage, operation, accumulator, and output dtypes separately, including
TF32 or fused-math settings. For each backend:

- reuse identical input bytes;
- compare section crossings, period, Lyapunov summaries, and classification
  confidence against the CPU reference;
- run horizon and tolerance sweeps;
- test repeatability on the actual driver/CUDA/library stack; and
- scope nulls as "no divergence observed on this stack," not proof of global
  determinism.

Do not demand long chaotic trajectories be bit-identical. Demand that the
frozen observables meet prospectively defined error and classification-parity
criteria.

## Tile and job model

Each job consumes immutable tile manifests. A tile ID binds:

- system/version;
- parameter pair, bounds, and coordinates;
- initial-condition set;
- solver, tolerances, horizon, and dtype contract;
- observable/classifier version;
- Git commit, container digest, and plan-manifest hash; and
- expected output schema and count.

Tiles write unique immutable shards. Never allow workers to mutate a shared
index or write the same file. Runpod warns that concurrent workers writing one
network volume can corrupt data; unique paths plus atomic completion markers
avoid that class of failure.

Resume behavior:

- partial files use temporary names;
- completed shards are atomically renamed and hashed;
- restart skips only verified completed tile IDs;
- duplicate tile results are rejected or retained as explicit replications;
- logs are append-only by attempt; and
- a completion marker is written only after counts and hashes pass.

Forced-kill and restart must be tested before using spot/interruptible capacity.

## Remote execution design

Use a self-contained container rather than debugging interactively on an
expensive pod.

The container must:

- check out or embed the exact frozen source commit;
- verify its own source/config hashes before execution;
- contain all runtime dependencies and a narrow preflight command;
- accept a frozen tile manifest and output location;
- emit machine-readable progress and no-progress heartbeats;
- write a full environment and hardware receipt; and
- terminate the workload process cleanly after success or failure.

Provider credentials remain outside the image and repository. Prefer narrowly
scoped, short-lived credentials. Do not expose unrelated ports or copy personal
SSH material when a task-specific key suffices.

## Storage

Runpod network volumes persist independently of Pods and can be accessed
through an S3-compatible interface. They are useful for reusable containers,
inputs, and retrieved shards, but storage continues to cost money after compute
terminates.

For a durable research archive, use an external object store or institutional
archive as the canonical copy. Treat the Runpod volume as staging/cache unless
there is an explicit retention decision.

Before a pod is terminated:

1. close every expected shard;
2. generate remote SHA-256 and byte-count manifests;
3. retrieve or copy artifacts;
4. verify local/object-store hashes against remote hashes;
5. preserve completion/failure logs and the cost receipt; and
6. terminate the task-owned pod and verify it is gone.

## Cost gate

Every paid run requires a run-specific approval containing:

- current GPU type and actual `costPerHr`;
- measured steady-state unit throughput;
- provisioning, image, warm-up, compute, output, and retrieval time;
- base and slow-case cost estimates;
- maximum wall time and hard spend ceiling;
- optional lower soft check-in threshold;
- no-progress timeout and safe checkpoint boundary; and
- exact resource ownership and teardown plan.

No general instruction to "keep going" authorizes a new paid pod. A healthy run
may proceed only within its approved hard ceiling. Duplicate, idle,
misconfigured, or no-progress work terminates immediately.

## Why not start with a `5000 x 5000` scan

Twenty-five million parameter points magnify every classifier defect and every
unmeasured transient. The recovered algorithm performs tens of thousands of
RK4 steps per point before Poincaré returns, so a direct restoration implies at
least hundreds of billions of integration steps.

The sequence should be:

1. small reference grid;
2. convergence and false-classification study;
3. GPU tile benchmark;
4. coarse atlas;
5. uncertainty-guided/adaptive refinement;
6. continuation of boundaries; and
7. a dense raster only if it answers a remaining scientific or presentation
   need.

## First Runpod milestone

The first paid milestone is not a paper-scale map. It is one cost-capped tile
that proves:

- exact container/commit binding;
- CPU/GPU classification parity on frozen cases;
- measured steady-state throughput;
- forced-kill resumability already tested cheaply;
- receipt completeness;
- remote/local hash agreement; and
- immediate verified teardown.

Only after that receipt is reviewed should the project request approval for a
multi-tile exploratory scan.

### Current authorization and live catalog snapshot

On 2026-08-06 the repository owner authorized use of the local
`RUNPOD_API_KEY` for a cheap qualification worker. `scripts/runpodctl.py` is the
resource-control boundary: it refuses duplicate names, requires an explicit
hourly ceiling, records the returned pod ID/cost, and exposes a direct terminate
command. Credentials remain in ignored `.env` and are never printed.

The live catalog query found a $0.13/hour RTX 3070 and $0.19/hour V100 PCIe,
both with low stock. The first Float64 qualification targets the V100 with a
$0.20/hour hard ceiling because its double-precision throughput is more
representative of this numerical workload. This snapshot is evidence for this
launch only and must not be reused as future pricing.

`scripts/gpu_qualify.py` is the first workload. It gates short-horizon Float64
and Float32 CUDA RK4 endpoints against SciPy DOP853 on a frozen 16-point grid,
then records raw ensemble throughput and the complete software/GPU environment.
It explicitly does not claim Poincaré or period-classification parity.

### First provisioning attempt

The V100 and A5000 had no available instances. A community RTX 3090 was then
created at $0.22/hour as pod `zjc8il0kri5fyf`, and its GPU/SSH endpoint were
verified. Remote execution stopped before source transfer because the GitHub
repository is private and GPU-spend authorization does not by itself authorize
uploading private source to a third-party host. The idle pod was terminated and
the account pod list was verified empty. No qualification result was produced.

## Runpod primary documentation

- [Create a Pod](https://docs.runpod.io/api-reference/pods/POST/pods)
- [Manage and terminate Pods](https://docs.runpod.io/pods/manage-pods)
- [Network volumes](https://docs.runpod.io/storage/network-volumes)
- [Runpod REST API overview](https://docs.runpod.io/api-reference/overview)

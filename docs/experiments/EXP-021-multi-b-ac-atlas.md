# EXP-021 — Multi-b Rössler (a,c) atlas animation

Status: preregistered; pending frozen GPU execution
Manifest: `experiments/manifests/EXP-021-multi-b-ac-atlas.json`
Claim targets: CLM-001 and bounded global-atlas reconnaissance

## Purpose

Generate Jones-Figure-1-style `(a,c)` period portraits over a substantially
larger declared plane, then animate their evolution as `b` increases. This is a
reconnaissance atlas for discovering persistent families, mergers, births,
boundary activity, and targets for continuation. Raster adjacency is not proof
of branch connectivity or a global organizing mechanism.

## Frozen domain and method

- `a in [0.05,0.4]` at 141 points;
- `c in [1,20]` at 191 points;
- 11 frames at `b=0.10,0.12,...,0.30`;
- 26,931 pixels per frame and 296,241 pixels total;
- one declared initial condition `(0,4,0)` per parameter point;
- Float64 RK4 with `dt=0.005`, transient 2,400, observation 800;
- cubic-Hermite legacy-section crossings and the EXP-018-qualified recurrence
  classifier through period 32.

Each frame is written atomically with its own result hash and completion
receipt. A restarted sweep skips a frame only after revalidating its manifest,
source commit, index, completion flag, and result SHA-256. The execution gate
allows at most 0.1% numerical-failure pixels per frame; unresolved pixels are
retained rather than relabeled chaotic.

## Deliverables and limits

The run produces 11 provenance-bound result frames, a combined receipt, a GIF,
and a contact sheet. The fixed color mapping makes the same period comparable
across every frame. The map is still basin-dependent, finite-time, bounded, and
rasterized. Candidate structures require longer-transient/basin qualification
and numerical continuation before entering the claim ledger as geometry.

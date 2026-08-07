# EXP-021 — Multi-b Rössler (a,c) atlas animation

Status: executed; all 11 frames passed and visualization verified
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

## Result

The frozen NVIDIA L4 sweep at commit
`b524ddcda6f19018ceea9259c8173cb197df881d` completed all 296,241 pixels in
131.45 seconds. Every frame passed. Ten frames had no numerical failures; the
`b=0.24` frame had one (`3.71e-5` of its pixels), well below the frozen 0.1%
ceiling. Depending on `b`, 7,346–8,577 pixels were recurrence-periodic; all
other nonterminal points remain unresolved rather than being called chaotic.

Detected periods across the sweep include 1 through 14, with 13 and 14 sparse.
Period-1 detections rise from 3,169 at `b=0.10` to 4,168 at `b=0.30`, while
periods 2–12 persist across the slab. Visually, the broad low-period band,
nested curved shells, steep organizing spine, and many isolated higher-period
windows move coherently as `b` increases.

The combined remote/local summary-receipt SHA-256 is
`c9718d5e1272ce7f12e0ef158b48614cbd9c49bff33721c35b926b8786b38017`.
The complete output package hash also matched:
`c6ca78cf882e0faaa64db5aa840fee703a968fe9a5ba28c86d886e02dd5e8b53`.
The EXP-021 pod was terminated and is absent from the account list; the
unrelated `ndl-lyapunov-20260806` pod was left untouched.

## Figures

- `artifacts/EXP-021/EXP-021-multi-b-ac-atlas.gif`, SHA-256
  `399adfc9c27fa25a87e37e62667cc8284d5c7ebad8d5d86cd99db82a28618d98`;
- `artifacts/EXP-021/EXP-021-multi-b-contact-sheet.png`, SHA-256
  `ac84a6e9f229c46d30628507270203b697fe7b5d8e24afe5037a69e5abd5c9f5`.

Both are generated from frame results whose hashes are revalidated before
rendering. The GIF uses a fixed period-color mapping across every `b` value.

## Decision

The Jones recurrence-section methodology is computationally extensible across
this bounded `(a,b,c)` slab and exposes coherent 3-D organization suitable for
family tracking. The atlas does not by itself establish that visually adjacent
windows are one continued family, identify saddle-node/period-doubling curves,
or explain the global homoclinic structure. The next computation tracks same-
period raster components across frames, followed by periodic-orbit and boundary
continuation on selected persistent families.

## Cross-b raster family candidates

`scripts/summarize_multi_b_atlas.py` applies same-period 26-neighbor adjacency
in the regular `(b,c,a)` index cube after revalidating every frame hash. It
finds 5,142 raster components: 129 span at least six frames and 46 span all
eleven. The all-frame count is 2 period-1, 10 period-2, 7 period-3, 17 period-4,
4 period-5, 1 period-6, and 5 period-8 candidates.

Several persistent components do not touch an `a` or `c` boundary and are
especially useful continuation seeds. Examples include period-2/3/4 candidates
over approximately `a in [0.28,0.40]`, `c in [2.3,3.8]`, a period-4 candidate
over `a in [0.1575,0.2275]`, `c in [6.2,8.8]`, and period-5 candidates over
`a in [0.135,0.1775]`, `c in [12.2,17.9]` and `a in [0.2225,0.265]`,
`c in [4.7,5.9]`. Large components touching `a_min` or `c_max` are truncated
and motivate domain expansion rather than global claims.

The component result SHA-256 is
`163ded4c78033d194cd17bbacc75e4b855bdef420cc5c34c71930447a36d4496`.
This adjacency is deliberately called candidate tracking: diagonal raster
contact on anisotropic grid spacings is not proof that periodic orbits or their
bifurcation boundaries form a single smooth family.

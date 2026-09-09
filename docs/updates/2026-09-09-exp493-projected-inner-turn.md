# EXP-493: the extra crossing carries an extra projected turn

**The saved-trajectory test is complete.** All 128 side profiles pass the
geometric checks, all 64 paired-solver comparisons pass, and all 64
opposite-side comparisons show one additional projected winding, with the
endpoint correction appropriate to open arcs. The complete candidate result
remains **15/16**: EXP-492's one failed state-accuracy comparison remains a
failure. No new trajectory was integrated and no threshold was relaxed.

## What this means for Jones

This is a concrete local link to the proposed inner-turn mechanism. The
additional accepted crossing is accompanied by additional turning in the
retained x--y trajectory geometry; it is not only a change in our counter.
We measured angle from trajectory points first and compared the event list
afterward. A separate signed-ray-intersection calculation also reproduces
all 128 measured polygon winding indices.

There is an important qualification. The paths tested here start at slightly
different initial conditions at the **same parameter values**. They are not
a continued family of corrected periodic orbits. Winding about an x--y
projection is also not a full three-dimensional topological invariant.
Consequently this supports a local geometric ingredient of Jones's proposal,
not a C/D assignment, verified word, p-to-p+1 connection, or complete
explanation of the parameter plane.

In fact, [EXP-480](../experiments/EXP-480-paired-section-reproducibility.md)
already found the same six historical-section/eight Barrio-section returns
for the corrected cycles at both of these parameter values. These two cases
must not be presented as opposite-period endpoints of an arrow. The newly
tested initial-condition arcs and the corrected periodic cycles are distinct
objects; transporting the marker between them is still research to do.

The next decisive step is to transport this geometric marker onto corrected
periodic cycles, check minimal period, and qualify its relationship to the symbolic partition, then
follow one claimed connection. Matching a drawing or choosing a dictionary
to reproduce the target word will not count as verification.

## The measured result

| Check | Complete outcome |
| --- | --- |
| Retained parent intervals | 26: sixteen nominated, ten unselected |
| Geometry profiles | 128/128 pass; both solvers, all four displacements |
| Paired geometry comparisons | 64/64 pass |
| Relative-turn comparisons | 64/64 pass; both magnitudes and both solvers |
| Complete candidates, including parent accuracy | 15/16 pass; original failure retained |
| New integrations / new paid services | 0 / $0 |

The relative open-arc angle change ranges from **0.9995888 to 0.9999973
turns**; subtracting the small endpoint-angle difference gives exactly one
additional integer branch-cut crossing. Do not interpret either individual
open arc as a closed periodic orbit.

The measured local polygon radii range from 2.70e-6 to 4.07e-4 about the
equilibrium's projection. In contrast, the minimum three-dimensional polygon
distances from the equilibrium range from 8.913 to 8.925 over the local
windows. Passing close to the projection origin is therefore not evidence
that these local arcs reach the equilibrium. These polygon distances are
numerical measurements, not rigorous lower bounds for the exact flow.

Maximum paired differences are 8.69e-12 radians in angle change, 5.15e-5 in
relative projected minimum radius, and 2.56e-8 in scaled endpoint state.
The maximum enriched-polygon angular step is 1.783 radians, below the frozen
2.9-radian guard. Every augmented/enriched polygon comparison passes.
The ordinary saved meshes also agree on the winding index in all 128 real
profiles; the undersampling problem exposed by the analytic control did
not occur in this completed dataset.

The retained unqualified candidate is
`local-a025-c083--region-0--depth-8--direction-0--candidate-1`.
Its geometric checks pass, but that cannot override EXP-492's separate
paired-state failure. The multiple upstream searches remain strongly related
samples of nearly coincident physical grazing locations within two parameter
cases, not sixteen independent discoveries.

## Reproduce the result

The [frozen protocol](../experiments/EXP-493-projected-inner-turn.md) was
designed and analytically tested while EXP-492 was running, before its target
outcomes were opened. Its parent hashes were bound after the complete parent
audit, without changing the geometric design. Source
`972ca987d10b420d8d136151434f77d408c222a4` was pushed and verified live before
analysis, and remains on `codex/exp493-local-execution`.

The complete local result has SHA-256
`b9a6ec1834dfaa4de51fd260ac2da26184aa6c97ba964532e72c639af62daf2a`.
A second raw-to-result replay reproduces it exactly, including the frozen
source binding and all controls. It first re-audits EXP-492's full retained
run. These are same-agent replays, not independent researchers or peer review.

The public release includes the
[compact result](../experiments/receipts/EXP-493-projected-inner-turn-result.json)
and a compressed archive of **every local-window polygon**, not only selected
examples. The 29,805,481-byte uncompressed analysis is preserved exactly in
[the compressed data](../experiments/receipts/EXP-493-projected-inner-turn-data.json.gz).
The archive and receipt carry their checksums and executed source bindings.
Full-horizon EXP-492 variational trajectories remain local; this is a release
of the complete geometric diagnostic, not the full research archive.

From a checkout, the public-only verification command is:

```bash
.venv/bin/python scripts/export_exp493_projected_inner_turn.py \
  --verify-only --output-dir docs/experiments/receipts
```

It decompresses and checks the exact analysis hash, replays all 128 polygons,
reconstructs the complete decision matrix, and independently counts signed
polygon intersections with the negative ray. It does not need credentials,
a GPU or the private full-horizon trajectories. It does not revalidate ODE
integration or rule out every possible hidden smooth loop between saved
vertices.

Portable polygon replay allows arithmetic roundoff at relative 1e-12 and
absolute 1e-13 when comparing computed floating-point measurements across
platforms. Data hashes, identities, integer indices and acceptance decisions
remain exact. This is not a relaxation of any experiment's scientific gates;
the original saved measurements and failed verdict are unchanged.
The original Linux CI at head
`895cabb66c64f46d5d5c29df10e8bda43305c6cf` failed only the public polygon
test's exact floating-point dictionary comparison on both Python versions;
2,060 other tests passed. The
[failed CI run](https://github.com/tdj28/butterfly/actions/runs/34322536769)
is retained. The revised comparison still rejects changed decisions and
material numerical errors; it requires final-head CI before merge.

Before execution, 31 focused tests and the complete 2,051-test suite passed
(one Linux-only skip). All twelve exact-data consumer controls passed; the
controls include origin contact and deliberately missed small detours.
After the public exporter was added, all 40 focused geometry/release tests
passed, including complete public-only replay, both winding orientations,
branch-cut endpoint handling, and rejection of altered archives or verdicts.
The complete final local suite also passed 2,060 tests with one Linux-only
skip in 135.29 seconds. A subsequent public-replay regression additionally
checks that machine roundoff is tolerated but changed decisions and material
numerical errors are rejected; all 41 focused tests pass with that addition.
EXP-492 merged to `main` as
`4ab72f21d119a9e9d98c4c0a473c2bd7e3b8fc1f` only after all four final-head
push/PR Python 3.12/3.13 checks passed. This successor preserves its separately
executed source and is reviewed as a distinct result change.
The formal manuscript is unchanged pending the separate legacy-impact audit
and stronger periodic-family evidence.

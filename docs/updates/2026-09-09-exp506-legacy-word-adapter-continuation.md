# EXP-506: finish the complete historical sensitivity

## Complete numerical replay; resource deviation explicitly retained

**All 2,040 original/filtered branch fits and 40 word-slope splines replay
successfully. The turning-point filter changes none of EXP-186's saved
partitions, bootstrap decisions, critical intervals or word outcomes.**
All 510 old retained-root occurrences pass the additional turning geometry.
There are no omitted pre-spline failures. The original failed parity/word
conclusion remains unchanged; no Jones arrow is thereby verified or refuted.

| Saved profile | Coordinate | Return pairs | Branches, old -> filtered | Word, both orbit solvers |
| --- | --- | --- | --- | --- |
| dt=0.01 | x | 7,335 | 2 -> 2 | 010011 |
| dt=0.01 | z | 7,335 | 1 -> 1 | unresolved |
| dt=0.005 | x | 7,299 | 2 -> 2 | C10011 |
| dt=0.005 | z | 7,299 | 1 -> 1 | unresolved |

This clears **only the added turning-filter sensitivity on EXP-186's saved
partitions/words**. It does not recertify the trajectories, all earlier methods,
the 41 other exposure candidates or a generating partition. x and z are two
projections of the same saved returns, not independent data sets.

There is a separate engineering deviation: the run directory uses
**124,055,116 bytes**, exceeding the frozen 104,857,600-byte output limit by
19,197,516 bytes. The writer and frozen auditor counted the 51,851,415 bytes
of prior products but omitted the final 72,203,701-byte duplicated summary from
quota admission. The original audit's numerical comparisons pass; it was not
a sufficient end-to-end resource check. The new compact receipt explicitly
sets `numerical_replay_passed=true` and **`protocol_compliant=false`**. Nothing
was deleted, no quota was retroactively enlarged and no old receipt was edited.

The new `python/butterfly/bounded_json.py` admits the complete serialized JSON
size **before** creating a file, including summaries and reserved failure space.
Ten controls pass, including these exact overrun sizes, canonical UTF-8/JSON
byte accounting, the free-space floor, no partial oversized file, no overwrite
or path escape, and symlink rejection. Frozen historical writers stay unchanged;
new runners must use the bounded writer and compact summary references rather
than duplicating large fit journals. This helper assumes a single writer;
concurrent writers need a shared lock.

The [91,941-byte public comparison receipt](../experiments/receipts/EXP-506-legacy-turning-impact-result.json)
has SHA-256
`4de5d276e8a74b97c31a0bc3eb636da8815c6f685c442b3df2a7325a275a9f32`.
It includes every profile/coordinate's original and filtered robust outputs and
word records, with the resource deviation and limited public-replay scope.
It is not a substitute for the complete local fit records or unavailable raw
EXP-186 arrays. The 72,192,202-byte complete local numerical audit is retained,
SHA-256 `a196976f7ef4d20df0e9e069067ff3b366b6cb8a735c43d41c72d964ec120988`.
No new raw evidence was uploaded.

Execution source: `23ca793bc63b11a5b690f1aca9385d680abc25a6`, preserved at
`codex/exp506-local-execution`. The run completed in 5.82 seconds, reusing all
255 old branch fits and executing 1,785 remaining branch fits plus 40 word-slope
fits. The full audit separately re-fitted all 2,040 branch and 40 slope cases.
Raw summary SHA-256:
`9156024ffc6323232c2ab5fa0c1bc6abfd0652b2e224050e145e8d850f440d66`.
The new marker is consumed, and EXP-505's failed marker remains unchanged.

Final local release checks passed: **2,468 tests**, one Linux-only skip, in
172.96 seconds (artifacts/EXP-506/release-suite-01.xml). The manuscript citation
and figure-availability check and receipt-generated quadratic table check pass.
The staged public scan passed 2,832 files. EXP-504's SVG, PDF and PNG redraws
are byte-identical to the published figure, whose rendered layout was checked.
All final-head push and pull-request Python 3.12/3.13 checks remain a required
gate before normal merging of [PR #73](https://github.com/tdj28/butterfly/pull/73).

## Prospective validation and implementation history

The [protocol](../experiments/EXP-506-legacy-word-adapter-continuation.md)
preserves EXP-505's implementation failure and all 255 completed first-population
branch fits. It completes the four original word-comparison fields using the
unchanged source logic and authenticated target list, after partition inference.
Every remaining original/filtered fit and all word rows stay in the fixed scope.

Before new target fits, **21 focused controls passed in 1.73 seconds**.
An authentic isolated copied-source startup passed with an 85-path closure.
Its preflight reconstructed the old robust result from all 255 retained fits
without any new branch or word-slope spline, and reproduced the complete schemas
of all eight old word rows. Tests forbid new spline construction during prefix
reuse, reject a changed sample hash and verify helper restoration after failure.

Frozen machine-plan SHA-256:
`b32268130ac71ea33e3637b9f6314345260c0afd32705ab389a1cb556943119a`.
The new attempt permits 600 seconds and 100 MiB of output while preserving
an 8 GiB free-space floor. It does not reset EXP-505, modify its source, change
scientific tolerances, rent hardware, upload raw evidence or call a paid model.

Word-slope splines are now retained and counted separately from branch-oracle
fits. The earlier failure executed the first two word calls before the schema
comparison, but their spline outputs were not retained; they are not falsely
treated as reusable branch evidence. After the new run, the full audit re-fits
all populations from the same authenticated saved arrays, including the reused
prefix, and checks every recorded result before scientific interpretation.

The pre-target checkpoint above preceded the completed numerical replay and
resource-deviation report at the top of this update.

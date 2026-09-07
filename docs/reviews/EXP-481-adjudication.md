# EXP-481 review adjudication

The preserved Pro review returned **READY AFTER SPECIFIED FIXES**, not an
unconditional approval. Its exact promoted bundle passes the canonical offline
validator. Cost reconstructed from reported usage is **$0.5888**; aggregate
output was 7,378 tokens despite the 6,000 requested limit, within the reserved
12,000 output-work allowance. This is a correlated advisory review, not an
independent source audit or scientific validation.

All five findings are now locally resolved before target outcomes. The
structured adjudication approves the finding-mapped final release; the actual
controller must still verify the pushed release, fresh setup and unused attempt.

| Finding | Decision and specific implementation |
| --- | --- |
| B01 | Accept. Extend the existing `qualify_paired_phases.py` with a bounded synthetic benchmark of actual journal collection/replay, all-profile qualification, and complete both-case analysis. Freeze the workload and extrapolation below before running. Preserve measurements even if resource headroom fails. |
| B02 | Accept with clarification. Existing `test_real_both_case_analysis_reports_every_reference_row_and_model` already exercises full cubic `analyze_campaign` with clustered four-pair seeds, both cases/profiles/windows and all five variants. Strengthen its expected full six-row near/far matrix, add a whole-seed two-sheet adverse campaign, and explicitly test that failed bootstrap replicates remain in the denominator. Benchmark the full retained population as well. |
| I01 | Accept. `paired_campaign.py` now explicitly describes separate fresh trajectories in a **reference-conditioned retained finite-time cohort**, emits the q90/support criteria, and forbids rare-sheet or support-gap extrapolation. All raw metric details remain in the existing casewise variant records. |
| I02 | Accept with bounded dependency disposition below. Keep both nominations and all preserved event rows. Broader historical branch-count reinterpretation remains open, but is not confused with the independently recomputed event inputs. |
| I03 | Accept. Freeze the casewise reporting and outcome table below. The existing result already retains cohort exclusions, support, errors, bootstrap counts, joint reasons and full event matrices; no new success threshold or selected subset is introduced. |

Accepted source changes are confined to `scripts/qualify_paired_phases.py`
(B01/B02), `tests/test_paired_campaign.py` (B01/B02/I01),
`tests/test_seed_return_map.py` (B02), and `python/butterfly/paired_campaign.py`
(I01). The numeric design, seed table, target parameters, reference states,
integrators, fits and all inference thresholds remain unchanged.

## Frozen synthetic workload and expectations

The collection benchmark records 64 analytic-circle trajectories through
t=20 at both target RK4 steps (.01/.005), using the actual recorder, checkpoint
writes, 1,000-step journals, full audit and replay. A discarded evaluation of
the actual vectorized Rössler RHS is added to every circle field call to charge
that arithmetic without integrating any target trajectory. Circle crossings
have period four and both raw sections are recorded. This is a workload proxy,
not a claim that chaotic trajectories cost exactly the same.

The actual qualification phase runs all four solver profiles through t=20 for
one seed in each of two synthetic cases. It must pass its ordered event checks.
The analysis benchmark uses all 8,192 retained IDs per case, four pairs per
window, both windows/profiles, three projections and all five variants. The
known cubic has turns at .25/.75. It must resolve three branches in both cases;
reference rows 0 and 1 must match turns 0 and 1 respectively, and rows 2–5 must
match neither. A matched two-sheet primary must not receive positive support.
These are schema-faithful synthetic pair arrays, not reconstructed flow orbits;
the raw-journal-to-profile path is covered separately by the circle control.

For bounded benchmarking only, use eight bootstrap draws; scale the **entire**
full-population analysis time by 200/8 for the target estimate. Scale the two
short collection and replay measurements by 300/20 and 256 batches per profile;
scale qualification by 128/8 trials. Apply a factor of two to all estimates.
Storage adds scaled qualification, scaled analysis output and 128 MiB of
metadata/runtime reserve before the factor of two. Peak memory adds 128 MiB for
bootstrap draws and complete-profile metadata before doubling. These estimates
must fit the unchanged phase limits; otherwise B01 remains open. A 900-second
parent-loss/deadline guard and sampled 2 GiB memory/disk limits bound the
benchmark itself. No target pilot, retry or target-driven threshold tuning.

The plan's `maximum_wall_seconds=14400` is the **collection** limit, not an
overall four-hour deadline. Separate qualification/analysis bounds are
1,800/7,200 seconds. Their sum is 23,400 seconds (6.5 hours), plus bounded setup
and orchestration; the current controller has no separate whole-campaign
deadline. Do not describe any of these limits as observed runtime.

## I02: reference dependency disposition

The legacy helper can influence earlier branch interpretation, local critical
location estimates and therefore the motivation or selection of the two
nominations. We retain that selection dependence rather than claiming the
cases were drawn independently or replacing them.

The executable EXP-481 reference states are not spline roots. The EXP-480
producer `check_historical_event_transport.py` re-corrects each nominated
periodic orbit using variational shooting, integrates it with DOP853/Radau,
records raw roots of both geometric section equations and normal-velocity
extrema, and selects all accepted rows in the fixed [.25,1.25) period window.
Its event ordering and section membership use time, the vector field and gates,
not `return_map._critical_points`. Importing a package that exports the helper
does not mean this numerical path calls it.

`paired_inputs.extract_references` independently reopens those hash-bound raw
arrays, recomputes velocities and section acceptance, and requires exact row
and phase equality with every declared reference. Both references passed this
audit again in execution-source-control-02. `from_reference_audit` constructs
capture geometry directly from these six/eight rows and the unchanged fixed
capture scales/radius/streak rule. Neither it nor the current analysis calls
the old helper. No supplied reference coordinate, ordering or capture rule is
computed from a legacy spline critical point. This closes the specific known
defect's executable-input dependency, not the historical interpretation audit
or a proof of every numerical property of the nominated cycle.

## I03: frozen interpretation and reporting

Apply the table **separately to each case** and report all failed components.
Several deficiencies may coexist; do not reduce them to a favorable label.

| Observed outcome | Permitted interpretation |
| --- | --- |
| Technical failure, cap, incomplete journal or invalid provenance | Invalid/incomplete execution; no completed scientific assessment or retry |
| Too few retained seeds, inadequate occupied support, interior gaps or unsupported holdout rows | Insufficient information for this population/projection; not evidence that the map or Jones's claim is false |
| Excess supported-row q90 error, profile-retention disagreement, unstable branch counts/turn intervals or failed bootstrap stability | Observed failure of the specified operational adequacy/stability criterion; state precisely which criterion, without inferring nonexistence of a map |
| Adequate map with no prominent turns, or no cycle event meeting the complete proximity rule | Adequate finite-resolution map but no supported turning-region proximity under this test; not a symbolic or homoclinic refutation |
| Adequate stable map plus event-region proximity in every required model | Bounded descriptive support on the reference-conditioned retained cohort only; no exact criticality, alphabet, arrows or invariant-set claim |

For every case retain original and retained counts, split sizes, all exclusion
categories, profile-retention disagreement, calibration bounds, occupied bins
and coverage, unsupported fraction, spline/affine q90 errors on identical rows,
all branch/bootstrap outcomes and cross-map intervals. Emit the complete
distance/slope matrix only when the primary gate enables it. The qualifying
thresholds are q90 <=.08, unsupported fraction <=.05, coverage >=.7; include
**observed** values and covered domain with any positive summary. No familywise
confidence statement or inference across unsupported gaps. Mixed cases stay
separate; neither diagnostic coordinates nor the better case rescue the other.

## Completed qualification

At pushed code freeze `68585e2bf853fcd2778b6efdf4b2e652bb6749db`, the fixed
benchmark completed with verified process cleanup in 7.044 seconds. Its worker
receipt is 21,367 bytes, SHA-256
`d6cc4641dd10b9f191848b645e127e559f35a13a62b50b1d06e9d30d124301e8`.
Both full-population positive cases and the adverse fixture passed their exact
expectations. This qualifies the declared control paths, not actual target
retention, precision or runtime.

| Doubled, reserve-inclusive estimate | Estimated | Existing limit |
| --- | ---: | ---: |
| Qualification | 59.82 s | 1,800 s |
| Collection | 5,647.04 s | 14,400 s |
| Analysis including replay | 502.18 s | 7,200 s |
| Evidence storage | 1,563,917,120 bytes | 8,589,934,592 bytes |
| Peak memory | 558,923,776 bytes | 2,147,483,648 bytes |

The unchanged limits have headroom under this synthetic extrapolation. No
resource or sample-size amendment was needed. Both raw measurements and the
conservative formulas are retained; none is a runtime guarantee.

The final source-bound production control also passed at the same freeze:
**381 tests, zero skips**, both raw reference audits, all 640 configurations
and all three analytic phases. Its complete 364-file source closure matches
the reviewed inventory except for the four explicitly mapped source/test
repairs. The [public evidence summary](../experiments/receipts/EXP-481-review-fixes.json)
binds the actual source qualification and benchmark receipts. The first focused
test run was denied `/bin/ps` by the sandbox; the preserved incomplete receipt
is not a scientific failure. The actual OS-enabled run passed all 86 focused
tests. No research trajectory or target attempt was used for these checks.

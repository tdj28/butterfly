# EXP-482: full-size controls pass; resource polling needs adjustment

The finer-step CPU route now has a complete synthetic workload measurement,
not just a short timing test. Both t=300 trajectory batches passed their
analytic expectations. The real full-size map analysis also recovered its known
three-branch cubic, with all six reference rows checked; the adverse two-sheet
primary remained unresolved. No Rössler trajectory was generated.

| Measured work | Result |
| --- | --- |
| 512 seeds, RK4 .0025, complete journals | 28.643 s; analytic final-state error 1.01e-8 |
| 512 seeds, RK4 .00125, complete journals | 57.127 s; analytic final-state error 6.33e-10 |
| Raw events, each section and step profile | 74,752, exactly as predicted |
| Independent replay, both profiles | 2.773 s total |
| Both-case analysis, 8,192 seeds/case, 200 resamples | 63.423 s; positive and adverse controls pass |
| Whole supervised workload | 160.443 s; process cleanup verified |

## The failure we are preserving

The original **feasibility gate failed**, despite the controls passing. Its
conservative model extrapolates the full journal tree to 23,232 files and
charges twice a full-tree scan at every .25-second resource poll. That model
projects 50,609 seconds of collection, above the 14,400-second cap. The worker
therefore returned 2, and its supervisor correctly records `incomplete` with
`nonzero-exit`. This is not a numerical failure, and is not relabeled a pass.

The large penalty is in the conservative scan-overhead **model**; we did not
measure a 50,609-second campaign or establish that actual CPU execution would
take that long. All measurement rows, file inventories, failed feasibility
decision and cleanup receipt remain in `artifacts/EXP-482/full-workload-01`.
Source and expectations were pushed first at
`bdce7efeeda18ce1537a55a42af8be1490b831ec`.

A subsequent code-review fix explicitly rejects NaN analytic final-state errors
in the benchmark checker (with a regression test). The observed errors above
are finite; no measured outcome changes, and the benchmark was not rerun or
relabeled as execution under that later source. Before this follow-up, the full
local suite passed 1,726 tests with one older Linux-only skip. Focused tests and
the final-head CI checks cover the later reporting/checker changes separately.

## The proposed solution

The existing supervisor permits one-second resource polling. Substituting that
interval into the **same measured-data projection**, without repeating any
trajectory or changing any scientific threshold, gives:

| Resource | Projection with headroom | Existing limit |
| --- | ---: | ---: |
| Qualification | 217 s | 1,800 s |
| Collection | 7,064 s | 14,400 s |
| Replay and analysis | 304 s | 7,200 s |
| Evidence storage | 1.56 GiB | 8 GiB |
| Peak memory | 0.60 GiB | 2 GiB |

This is a **post-observation design calculation, not a new measured pass** or a
runtime promise. Unknown target event frequency, retained population, reference
geometry, inventory overhead and OS load still matter. One-second polling
reduces resource-monitoring frequency only; the RK4 timesteps, journal interval,
worker deadline/parent-loss guard and numerical acceptance thresholds are
unchanged. Sampled RSS/disk limits can overshoot for longer between polls; this
tradeoff must appear in the successor's prospective review and frozen plan.

The read-only `scripts/summarize_exp482_workload.py` checks independent original
receipt hashes and the complete worker inventory, reproduces the original
failed estimate, then labels the new scenario separately. The compact public
[receipt](../experiments/receipts/EXP-482-full-workload.json) preserves both.

## Next research step

Freeze .0025/.00125, batch 512, 240,000 steps, 262,144 raw events/batch and
one-second resource polling for prospective EXP-482 review. Use a newly declared
seed draw (PCG64 482001; bootstrap 482002) so the inference sample is not the
EXP-481 draw already inspected during qualification. Keep both nominated cases,
all map/retention/accuracy gates, and disclose that parameter nominations and
numerical design are informed by prior results. New seeds do not make those
choices independent or turn an early solver check into a long-time guarantee.

Then qualify actual Rössler event accuracy before collecting the full paired
sample. Jones' symbolic alphabet and chain remain unverified at this checkpoint;
these controls make the next scientific test practical, not already successful.

The raw EXP-481 prax backup is still local: the environment rejected the renewed
upload after the user's general go-ahead. No upload or workaround occurred.

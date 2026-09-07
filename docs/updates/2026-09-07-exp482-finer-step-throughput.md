# EXP-482: a practical CPU path for finer steps

After preserving EXP-481's failed numerical qualification, the first successor
engineering measurement passes. This is an analytic-circle benchmark, not a
Rössler trajectory or a repaired scientific result.

The [draft and fixed workload](../experiments/EXP-482-step-refinement-draft.md)
were pushed before measurement at
`8cddf0d8d69465d230036f72dd5542dbff76d918`. All three bounded runs finished
cleanly with verified process cleanup and passed the unchanged synthetic
state/event expectations. Each uses both finer RK4 steps, .0025/.00125,
through t=20.5, with durable 1,000-step journals.

| Fixed batch | Both profiles, measured seconds | Seconds per synthetic trajectory |
| --- | ---: | ---: |
| 128 | 2.502 | 0.01954 |
| 256 | 3.034 | 0.01185 |
| 512 | 4.869 | 0.00951 |

The 512-sized batch is about **2.05 times faster per trajectory** than the
128-sized batch on this workload. Larger vectorized batches are therefore a
promising CPU option; there is no need to assume a GPU is required. This does
not yet qualify a target batch size or a full-horizon completion estimate.
The benchmark omits actual Rössler RHS work and uses synthetic capture geometry;
full target event/storage/replay and analysis costs must still be bounded.

The [receipt](../experiments/receipts/EXP-482-synthetic-throughput.json) binds
all actual measurements and supervisor observations. Complete raw evidence is
under `artifacts/EXP-482/synthetic-throughput-01`. No paid review, upload or
research trajectory occurred in this measurement. The previous $0.5888 review
remains attached only to EXP-481.

Next: complete a conservative target-path feasibility estimate, freeze the
finer-step numerical successor with the same accuracy threshold, and qualify
those steps on the declared diagnostic seeds. Their Rössler accuracy remains
unmeasured; EXP-481's failure and consumed attempt stay unchanged.

# Update — EXP-130 transverse GPU pilot result

The next calculation is now concrete: it tests whether the locally qualified
signed branch-opening observable produces ordered finite brackets at `c=19.8`
and `c=19.9`, rather than spending another hour bisecting only `c=20`.

The GPU remains a discovery accelerator. Stable-cycle construction and
classification use adaptive DOP853; the ensemble uses the already qualified
Float64 RK4/Hermite kernel; any newly discovered bracket must later pass an
independent adaptive-DOP853 PIM experiment. Unresolved points are preserved.

The live Runpod account was empty before preregistration. EXP-130 has a
run-specific `$0.40/hour`, one-hour, `$0.40` hard gate and an explicit
retrieve/hash/terminate/verify-empty teardown contract.

## Execution checkpoint

EXP-130 completed from clean pushed commit `2cbe797` on a secure RTX A5000 and
correctly failed its scientific-resolution gate. The two published controls
pass, but neither narrow PIM-qualified local endpoint resolves under the same
deep finite sprinkler. The failure is not sample starvation or integration:
all executed runs clear the frozen survivor/pair floors with zero numerical
failure and zero buffer saturation. The branch and edge-slope oracle variants
instead disagree near the boundary.

No transverse bracket is claimed. The result establishes a method boundary:
GPU sprinklers can discover candidates away from the opening, but adaptive PIM
must carry the topology claim. It selects PIM tests at `c=19.8` with
`a=(0.145,0.148)` and at `c=19.9` with `a=(0.145,0.150)`. The retrieved receipt
hash matches, spend is below `$0.10`, the pod is terminated, and the Runpod
account is empty.

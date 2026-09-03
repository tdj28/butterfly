# Update — EXP-150 transverse UPO recovery preregistered

EXP-132's qualified `c=19.9` bracket creates the first clean second slice on
which the local lobe/pruning mechanism can be tested without inferring a curve
from raster adjacency. EXP-150 now freezes the prerequisite orbit-recovery
step before inspecting any close return on those target PIM trajectories.

The complete EXP-133 selector, DOP853 shooting method, and numerical gates are
reused unchanged at the `a=0.145` two-branch and `a=0.150` three-branch
endpoints. A pass requires at least one identity-qualified unstable periodic
orbit on each side. Any recovered solutions will still undergo a separately
frozen primitivity/deduplication audit before lobe tracing or cross-slice family
claims.

This work is queued behind the active EXP-148 midpoint PIM so the eight-worker
pool is not oversubscribed.

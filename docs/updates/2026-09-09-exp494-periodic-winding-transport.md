# Moving the inner-turn test onto corrected periodic orbits

## Execution started

EXP-494 is running from public source
`4e5054955e8ddeb9db94e4702fe78d6232eda303`, also preserved at
`codex/exp494-local-execution`. The exact source was verified on the remote
before the runner opened any new geometry or generated target trajectories.

The question is now about periodic families, rather than nearby transient
initial conditions. The fixed survey has 64 new parameter nodes: two starting
cycles, increasing/decreasing a and c, eight steps per arm. Each node uses
both DOP853 and Radau. Two paired base corrections and all eight retained
EXP-480 profiles also receive winding/minimal-period diagnostics.

The known 6/8 return counts restrict a repeated-traversal multiplicity to two;
the new check explicitly tests the half-period state rather than assuming
the candidate period is minimal. The survey permits winding/count changes
between parameter nodes. It does not fit a C/D dictionary or compare words.

All four actual circular-orbit controls and 35 focused regressions passed;
the final full suite passed **2096 tests**, with one Linux-only skip.
The [preflight](../experiments/EXP-494-preflight.md) retains the pre-outcome
test failures and repairs. The
[frozen protocol](../experiments/EXP-494-periodic-winding-transport.md) gives
every threshold, grid point, stopping rule and claim limitation.

Raw data are being retained in `artifacts/EXP-494/target-4e50549`: all shooting
trial meshes, observation meshes, dense interpolation coefficients, ordinary
and extremum-bracketed crossings, and failed or unrun branches. No failed
point can silently supply the next continuation seed. The full ledger is
audited after completion before interpreting a winding transition.

No paid reviews, API calls, or cloud GPU charges are authorized or needed for
this run. This says nothing about previously incurred project spending.

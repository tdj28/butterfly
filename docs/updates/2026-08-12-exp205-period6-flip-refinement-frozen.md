# EXP-205 freezes seven period-6 flip refinements

EXP-203's stable-strip edge contains 18 adjacent corrected-orbit brackets of a
real `-1` Floquet multiplier. EXP-205 prospectively selects seven slices across
the observed range and freezes scalar `a` bisection with unchanged DOP853,
closure, neutral multiplier, and two-section identity gates.

A pass will supply seeds for coupled curve continuation, not identify the
topology-changing curve or a double-superstable center.

The first direct invocation stopped before loading candidate data or running
an integration because the script-only import path omitted the repository
root. The entrypoint was made self-contained and received a regression test; no
event, threshold, evidence input, or acceptance rule changed before execution.

The clean rerun passes all seven events. Each final `a` bracket is
`7.63e-11` wide, maximum absolute multiplier residual is `2.02e-7`, maximum
closure is `2.83e-13`, and all two-section identity counts remain exact. The
period-6 stable strip has a genuine real `-1` Floquet edge. This promotes the
seven points to coupled flip-curve and period-12 branch-switch seeds while
leaving the topology-changing and double-critical claims open.

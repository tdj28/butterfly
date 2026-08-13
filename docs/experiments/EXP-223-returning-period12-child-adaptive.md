# EXP-223 — Adaptive returning-child continuation

Status: frozen — awaiting execution

EXP-222 proves that the stable period-12 child survives EXP-221's first coarse
root jump when the event interval is resolved finely. EXP-223 generalizes that
path-resolution fix prospectively across all 52 exact EXP-217 returning-arm
events from `c=7.16299104` to the unresolved middle slice at `c=7.70247507`.

The closest-to-event independently qualified EXP-220 child is held at its
constant event-relative offset `a_child-a_event=-5.73024e-7`. Each exact next
event is tried directly. A trial is accepted only if the parent is unstable,
the primitive child is stable, the period ratio is two, historical/Barrio
counts remain `7/8` versus `14/16`, closure and proper-subperiod gates pass,
and the child-state step is at most `0.003`. A rejected trial is retained in
the receipt and its event-seed interval is recursively bisected to maximum
depth six. No scientific tolerance is relaxed.

Exact source-event indices 0, 25, and 51 receive independent DOP853/Radau
whole-orbit controls. A pass establishes a regular sampled child strip from
the near to middle returning arm. It does not establish a global child sheet,
paired shrimp boundaries, TBA membership, or double-criticality.

Manifest:
[`../../experiments/manifests/EXP-223-returning-period12-child-adaptive.json`](../../experiments/manifests/EXP-223-returning-period12-child-adaptive.json).

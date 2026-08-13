# EXP-223 — Adaptive returning-child continuation

Status: complete — full-range claim failed at a localized double-cover collapse

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

## Result

The full 52-event claim fails, but adaptive continuation accepts 212 points
through 45 exact EXP-217 events and 44 complete intervals, reaching
`(a,c)=(0.2406767067,7.6251864206)`. All accepted points retain the frozen
primitive-child gates. Period ratios are `2.00000038--2.00005208`, parent
multiplier moduli `1.00145--1.44027`, child moduli
`0.000674--0.994189`, minimum proper-subperiod closure `0.00514`, and maximum
orbit closure `3.32e-10`. The largest accepted child-state step is `0.002965`,
below the prospective `0.003` bound. Independent controls pass at source-event
indices 0 and 25; index 51 is not reached.

Depth six is exhausted inside source interval 44 over
`c=[7.6251864206,7.6254156527]`. The terminal rejected solve is coherent in
state but fails because the offset parent has become stable and the putative
child closes after half its nominal period. A deterministic diagnostic replay
gives parent multiplier `-0.9979916265`, period ratio
`2.0000000000014`, parent/child phase-state distance `9.29e-8`, and child
half-period closure `3.41e-7`. Thus this is a double-covered parent collapse,
not another distant primitive-root jump like EXP-221.

EXP-224 freezes a two-solver scalar localization of the intervening parent
real-`-1` crossing on this exact constant-offset path, plus bilateral
primitive-child and double-cover controls. Until that passes, EXP-223 supports
a broad sampled child strip and a localized endpoint candidate—not a global
child sheet or paired shrimp-boundary assignment.

Raw receipt: `artifacts/EXP-223/receipt.json`, 632,948 bytes, SHA-256
`1ee1f5c4c59e15403b06c745e5c66ce64944f01700d02bfb54fafb2a86dd1782`.
Compact receipt:
[`receipts/EXP-223.json`](receipts/EXP-223.json).

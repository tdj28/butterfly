# EXP-217 — Broad continuation of the returning period-6 flip arm

Status: prospectively frozen before execution

EXP-216 qualifies an exact turn in the `c` projection and stops only because
its frozen upper guard is `c=7.0`. EXP-217 expands that guard to `c=8.8` and
continues from the last two accepted events toward `c>=8.25`.

The adaptive policy and every scientific gate are unchanged. At least 20 and
at most 160 points may be accepted. Each must remain an exact real-`-1`
period-6 event with extremum-partitioned historical count seven, Barrio count
eight, and bounded parameter jumps. The terminal point must independently
recorrect under Radau.

Manifest:
[`../../experiments/manifests/EXP-217-period6-flip-returning-arm.json`](../../experiments/manifests/EXP-217-period6-flip-returning-arm.json).

A pass establishes a broad returning event arm. It does not prove global
closure, assign either arm to a shrimp boundary, continue the child sheet,
identify the TBA, or establish double-criticality.

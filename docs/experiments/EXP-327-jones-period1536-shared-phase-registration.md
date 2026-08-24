# EXP-327 — Shared-phase registration at event eight

Status: frozen; not yet run

EXP-326 continues the exact immediate seventh daughter across the 4,096-step
event-eight coordinate and corrects it there below `9e-23`. The connected
period differs from EXP-306's target by only `3.13e-22`, its primitive
half-node RMS is `7.98849e-6`, and its transverse multiplier is
`-1.00000000000025`. The receipt nevertheless fails its integer-node identity
gate at `1.20e-6` RMS.

The selected half-period-shifted target mesh lies `3.16e-6` off the connected
orbit's phase hyperplane. Integer cyclic shifts therefore do not register the
two continuous phases. EXP-327 preserves the failure and changes no orbit
equation: it starts from the bound target nodes after only EXP-326's selected
integer shift, imposes the connected orbit's exact phase hyperplane, and
recorrects at the same fixed `a` in the same 50-digit RK4 3/8 map.

A pass requires `1e-20` matching and phase closure, primitive amplitude,
direct shared-phase node RMS below `1e-8`, period difference below `1e-8`, and
unchanged cyclic and neutral gates. Combined with EXP-326, a pass qualifies a
bounded sheet connection; EXP-326 itself remains failed.

Manifest:
[`../../experiments/manifests/EXP-327-jones-period1536-shared-phase-registration.json`](../../experiments/manifests/EXP-327-jones-period1536-shared-phase-registration.json).

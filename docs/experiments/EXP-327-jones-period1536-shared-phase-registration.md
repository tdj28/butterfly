# EXP-327 — Shared-phase registration at event eight

Status: passed — exact shared-phase identity qualified

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

## Result

EXP-327 passes every frozen gate after 161.38 seconds and two full Newton
steps. The first step removes the continuous phase mismatch and reduces direct
node RMS from `1.1986e-6` to `1.5079e-13`. The second restores exact-map
closure and reduces the same-phase node RMS to `6.3542e-18`.

Final matching is `8.57e-26`, connected-period difference is `1.02e-21`, and
half-node RMS remains `7.9884935e-6`. Cyclic spread is zero, neutral residual
is `2.37e-23`, and the transverse multiplier is
`-0.9999999999999993`. Combined with EXP-326's passed bracket and connected
root, this qualifies the bounded sheet connection tracked as FND-107.

Raw receipt: `artifacts/EXP-327/receipt.json`, 350,053 bytes, SHA-256
`c9ec92bd735fb8460ed0e7986ef07102943ff2032261c0c72edabcfa6b54d9c9`.
Compact receipt: [`receipts/EXP-327.json`](receipts/EXP-327.json).

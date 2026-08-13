# EXP-250 — Secant-seeded exact period-48 flip

Status: completed — failed optimizer-status and full-period Radau gates

EXP-249 stalls just above its orbit gate when initialized from one bracket
endpoint. EXP-250 interpolates the two exact, phase-aligned EXP-247 endpoint
node sets and periods at the multiplier secant estimate. It changes only that
initial guess and raises the corrector ceiling from 30 to 60.

The bracket, augmented equations, 64 segments, fixed coordinates, DOP853 and
Radau profiles, primitive `56/64` identity, and every scientific acceptance
threshold are unchanged. A pass qualifies the event; a failure triggers a
sparse or collocation formulation rather than threshold relaxation.

Manifest:
[`../../experiments/manifests/EXP-250-jones-period48-augmented-flip-secant.json`](../../experiments/manifests/EXP-250-jones-period48-augmented-flip-secant.json).

## Result

The secant seed resolves the orbit plateau: at the 60-evaluation ceiling,
orbit and tangent residuals are `2.16e-10` and `1.31e-10`, and the DOP853 flip
residual is `2.00e-8`, all within their frozen gates. The receipt remains
failed because the optimizer reports maximum evaluations and the full-period
Radau replay gives multiplier `-0.998569`, outside the `1e-4` gate, after
accumulating closure drift `1.45e-6` over period `357.74`.

EXP-251 freezes a residual-qualified status rule and evaluates the same
64-segment augmented equations and block-Floquet products under Radau. It does
not reuse the ill-conditioned single-shot representation, and it changes no
scientific threshold.

Raw receipt: `artifacts/EXP-250/receipt.json`, 17,683 bytes, SHA-256
`376a8f433a7ca73297bd4d9f00b73fbe638176c620aa2c0a5334c91aedddd5a8`.
Compact receipt:
[`receipts/EXP-250.json`](receipts/EXP-250.json).

# EXP-250 — Secant-seeded exact period-48 flip

Status: frozen — not yet executed

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
